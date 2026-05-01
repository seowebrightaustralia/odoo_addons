# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    crm_pending_tag_id = fields.Many2one('crm.tag', string='CRM Pending Tag')
    crm_approved_tag_id = fields.Many2one('crm.tag', string='CRM Approved Tag')
    crm_declined_tag_id = fields.Many2one('crm.tag', string='CRM Declined Tag')
    crm_on_hold_tag_id = fields.Many2one('crm.tag', string='CRM On-Hold Tag')