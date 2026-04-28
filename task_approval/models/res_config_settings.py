# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    task_pending_tag_id = fields.Many2one(related='company_id.task_pending_tag_id', readonly=False)
    task_approved_tag_id = fields.Many2one(related='company_id.task_approved_tag_id', readonly=False)
    task_declined_tag_id = fields.Many2one(related='company_id.task_declined_tag_id', readonly=False)
    task_on_hold_tag_id = fields.Many2one(related='company_id.task_on_hold_tag_id', readonly=False)