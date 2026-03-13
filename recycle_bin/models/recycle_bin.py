# -*- coding: utf-8 -*-
import json

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RecycleBin(models.Model):
    _name = 'recycle.bin'
    _description = 'Recycle Bin'
    _order = 'deleted_at desc'

    name = fields.Char(string="Name", required=True, readonly=True)
    deleted_at = fields.Datetime(string="Deleted at", required=True, readonly=True, default=fields.Datetime.now)
    deleted_by = fields.Many2one(comodel_name="res.users", string="Deleted by", required=True, readonly=True,
                                 ondelete="restrict", default=lambda self: self.env.user.id)
    model_id = fields.Many2one(comodel_name="ir.model", string="Model", required=False, readonly=True)
    model_name = fields.Char(string="Model Name", required=True, readonly=True)
    record_id = fields.Integer(string="Deleted Record ID", required=True, readonly=True)
    restored_record_id = fields.Integer(string="Restored Record ID", required=False, readonly=True)
    restored_at = fields.Datetime(string="Restored at", readonly=True, required=False)
    restored_by = fields.Many2one(comodel_name="res.users", string="Restored by", readonly=True, ondelete="restrict")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", readonly=True,
                                 default=lambda self: self.env.company.id)
    trash_screenshot = fields.Boolean(related='company_id.trash_screenshot')
    screenshot = fields.Binary(string="Screenshot")
    screenshot_name = fields.Char(string="Screenshot Name", required=False, )
    data_json = fields.Text(string="Data in Json", required=False)
    raw_data_json = fields.Text(string="Raw Data in Json", required=False)
    state = fields.Selection(string="Status", selection=[
        ('deleted', 'Deleted'),
        ('restored', 'Restored'),
        ('failed', 'Restore Failed'),
    ], default='deleted', readonly=True)

    @api.model
    def empty_trash(self):
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            days = company.trash_duration if company.trash_duration_uom == 'day' else 0
            months = company.trash_duration if company.trash_duration_uom == 'month' else 0
            years = company.trash_duration if company.trash_duration_uom == 'year' else 0
            limit_date = fields.Datetime.now() - relativedelta(days=days, months=months, years=years)
            records = self.sudo().search([
                ('deleted_at', '<', limit_date),
                ('company_id', '=', company.id)
            ])
            records.sudo().unlink()

    @api.model
    def empty_all_trash(self):
        self.sudo().search([('company_id', '=', self.env.company.id)]).unlink()

    def action_restore(self):
        for rec in self:
            vals = json.loads(rec.data_json)
            record = self.env[rec.model_id.model or rec.model_name].with_context(lang=None).sudo().create(vals)
            rec.sudo().write({
                'state': 'restored',
                'restored_by': self.env.user.id,
                'restored_at': fields.Datetime.now(),
                'restored_record_id': record.id,
            })

    def action_advance_restore(self):
        self.ensure_one()
        return {
            'name': _("Advanced Restore"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.advance.restore',
            'target': 'new',
            'context': {
                'default_recycle_id': self.id,
                'default_raw_data_json': self.raw_data_json},
        }

    def action_view_restored_record(self):
        record = self.env[self.model_id.model or self.model_name].sudo().search([('id', '=', self.restored_record_id)])
        if not record:
            raise ValidationError(_("Record has been deleted!"))
        return {
            'name': _("Restored Record"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self.model_id.model or self.model_name,
            'res_id': self.restored_record_id,
            'target': 'current',
        }
