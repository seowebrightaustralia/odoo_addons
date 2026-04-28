# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    task_pending_tag_id = fields.Many2one('project.tags', string='Pending Tag')
    task_approved_tag_id = fields.Many2one('project.tags', string='Approved Tag')
    task_declined_tag_id = fields.Many2one('project.tags', string='Declined Tag')
    task_on_hold_tag_id = fields.Many2one('project.tags', string='On-Hold Tag')