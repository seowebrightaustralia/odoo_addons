# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WizardEmptyTrash(models.TransientModel):
    _name = 'wizard.empty.trash'
    _description = 'Empty Trash Wizard'
    
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company.id)

    def action_confirm(self):
        self.env['recycle.bin'].sudo().empty_all_trash()
