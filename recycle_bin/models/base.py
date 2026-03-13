# -*- coding: utf-8 -*-
import json

from collections import defaultdict

from odoo import api, fields, models
from odoo.fields import Command

# special columns automatically created by the ORM
LOG_ACCESS_COLUMNS = ['create_uid', 'create_date', 'write_uid', 'write_date', '__last_update', 'message_follower_ids']
MAGIC_COLUMNS = ['id'] + LOG_ACCESS_COLUMNS


class Base(models.AbstractModel):
    _inherit = 'base'

    def unlink(self):
        if self and not self._transient and 'ir.' not in self._name:
            blacklist_models = ['recycle.bin', 'mail.followers', 'mail.message', 'mail.mail', 'bus.bus', 'bus.presence']
            mode = self.env.company.trash_filter_mode
            if mode in ['all', 'blacklist']:
                if mode == 'blacklist':
                    blacklist_models += self.env.company.trash_model_ids.mapped('model')
                if self._name not in blacklist_models:
                    self.create_recycle_bin()
            else:
                if self._name not in blacklist_models and self._name in self.env.company.trash_model_ids.mapped('model'):
                    self.create_recycle_bin()
        return super(Base, self).unlink()

    def create_recycle_bin(self):
        recycle_obj = self.env['recycle.bin']
        model_name = self._name
        model_id = self.env['ir.model'].sudo().search(
            [('model', '=', model_name)])
        for rec in self:
            vals = rec.sudo().with_context(active_test=False).restore_data()[0]
            raw_vals = rec.sudo().read()
            recycle_vals = {
                'name': rec.display_name,
                'model_id': model_id.id,
                'model_name': model_id.model,
                'record_id': rec.id,
                'deleted_by': self.env.user.id,
                'data_json': json.dumps(vals, default=str, indent=2),
                'raw_data_json': json.dumps(raw_vals, default=str, indent=2),
            }
            try:
                recycle_obj.sudo().create(recycle_vals)
            except Exception:
                recycle_vals['raw_data_json'] = recycle_vals['data_json']
                recycle_obj.sudo().create(recycle_vals)

    # implement and modify method copy_data()
    def restore_data(self, default=None):
        """
        Copy given record's data with all its fields values

        :param default: field values to override in the original values of the copied record
        :return: list of dictionaries containing all the field values
        """
        vals_list = []
        default = dict(default or {})
        # avoid recursion through already copied records in case of circular relationship
        if '__copy_data_seen' not in self._context:
            self = self.with_context(__copy_data_seen=defaultdict(set))

        # build a black list of fields that should not be copied
        blacklist = set(MAGIC_COLUMNS + ['parent_path'])
        whitelist = set(name for name, field in self._fields.items() if not field.inherited)

        def blacklist_given_fields(model):
            # blacklist the fields that are given by inheritance
            for parent_model, parent_field in model._inherits.items():
                blacklist.add(parent_field)
                if parent_field in default:
                    # all the fields of 'parent_model' are given by the record:
                    # default[parent_field], except the ones redefined in self
                    blacklist.update(set(self.env[parent_model]._fields) - whitelist)
                else:
                    blacklist_given_fields(self.env[parent_model])

        blacklist_given_fields(self)

        fields_to_copy = {name: field
                          for name, field in self._fields.items()
                          if field.copy and name not in default and name not in blacklist}

        for record in self:
            seen_map = self._context['__copy_data_seen']
            if record.id in seen_map[record._name]:
                vals_list.append(None)
                continue
            seen_map[record._name].add(record.id)

            vals = default.copy()

            for name, field in fields_to_copy.items():
                if field.type == 'one2many':
                    # duplicate following the order of the ids because we'll rely on
                    # it later for copying translations in copy_translation()!
                    lines = record[name].sorted(key='id').copy_data()
                    # the lines are duplicated using the wrong (old) parent, but then are
                    # reassigned to the correct one thanks to the (Command.CREATE, 0, ...)
                    vals[name] = [Command.create(line) for line in lines if line]
                elif field.type == 'many2many':
                    vals[name] = [Command.set(record[name].ids)]
                # add custom code to handle binary field
                elif field.type == 'binary':
                    val_bytes = field.convert_to_write(record[name], record)
                    vals[name] = val_bytes.decode('utf-8') if val_bytes else ''
                else:
                    vals[name] = field.convert_to_write(record[name], record)
            vals_list.append(vals)
        return vals_list
