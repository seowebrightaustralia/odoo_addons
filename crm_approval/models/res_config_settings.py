# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_pending_tag_id = fields.Many2one(related='company_id.crm_pending_tag_id', readonly=False)
    crm_approved_tag_id = fields.Many2one(related='company_id.crm_approved_tag_id', readonly=False)
    crm_declined_tag_id = fields.Many2one(related='company_id.crm_declined_tag_id', readonly=False)
    crm_on_hold_tag_id = fields.Many2one(related='company_id.crm_on_hold_tag_id', readonly=False)