# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    trash_duration = fields.Integer(string="Keep Trash Duration", default=30, required=True)
    trash_duration_uom = fields.Selection(string="Trash Duration UoM", selection=[
        ('day', 'Days'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], default='day', required=True)
    trash_filter_mode = fields.Selection(string="Trash Filter Mode", selection=[
        ('all', 'All Models'),
        ('whitelist', 'Whitelist Models'),
        ('blacklist', 'Blacklist Models')
    ], required=True, default='all')
    trash_model_ids = fields.Many2many(comodel_name="ir.model", string="Filter Models")
    trash_screenshot = fields.Boolean(string="Trash Screenshot", default=True)
