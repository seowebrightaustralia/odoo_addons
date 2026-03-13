# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    trash_duration = fields.Integer(string="Keep Trash Duration", related='company_id.trash_duration', required=True,
                                    readonly=False)
    trash_duration_uom = fields.Selection(string="Trash Duration UoM", selection=[
        ('day', 'Days'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], related='company_id.trash_duration_uom', required=True, readonly=False)
    trash_filter_mode = fields.Selection(string="Trash Filter Mode", selection=[
        ('all', 'All Models'),
        ('whitelist', 'Whitelist Models'),
        ('blacklist', 'Blacklist Models')
    ], required=True, readonly=False, related='company_id.trash_filter_mode')
    trash_model_ids = fields.Many2many(comodel_name="ir.model", string="Filter Models", readonly=False,
                                       related='company_id.trash_model_ids')
    trash_screenshot = fields.Boolean(string="Trash Screenshot", related='company_id.trash_screenshot', readonly=False)

    def empty_trash(self):
        return {
            'name': 'Empty Recycle Bin Trash',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.empty.trash',
            'view_mode': 'form',
            'target': 'new',
        }
