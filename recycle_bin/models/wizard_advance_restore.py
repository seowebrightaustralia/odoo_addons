# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WizardAdvanceRestore(models.TransientModel):
    _name = 'wizard.advance.restore'
    _description = 'Wizard Advance Restore'

    recycle_id = fields.Many2one(comodel_name="recycle.bin", string="Recycle Bin", required=True)
    raw_data_json = fields.Text(string="Raw Data in JSON", required=True)

    def action_confirm(self):
        vals = json.loads(self.raw_data_json)
        try:
            record = self.env[self.recycle_id.model_id.model or self.recycle_id.model_name].with_context(lang=None).sudo().create(vals)
            self.recycle_id.sudo().write({
                'state': 'restored',
                'restored_by': self.env.user.id,
                'restored_at': fields.Datetime.now(),
                'restored_record_id': record.id,
            })
        except Exception as e:
            raise ValidationError(e)
