# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    approval_status = fields.Selection([
        ('1_pending', '1. Pending'),
        ('2_approved', '2. Approved'),
        ('3_declined', '3. Declined'),
        ('4_on_hold', '4. On-Hold')
    ], string='Approval Status', compute='_compute_approval_status', store=True)

    @api.depends('tag_ids')
    def _compute_approval_status(self):
        for lead in self:
            comp = lead.company_id or self.env.company
            
            if comp.crm_approved_tag_id and comp.crm_approved_tag_id in lead.tag_ids:
                lead.approval_status = '2_approved'
            elif comp.crm_declined_tag_id and comp.crm_declined_tag_id in lead.tag_ids:
                lead.approval_status = '3_declined'
            elif comp.crm_on_hold_tag_id and comp.crm_on_hold_tag_id in lead.tag_ids:
                lead.approval_status = '4_on_hold'
            else:
                lead.approval_status = '1_pending'

    def _remove_approval_tags(self):
        comp = self.company_id or self.env.company
        tags_to_remove = comp.crm_pending_tag_id | comp.crm_approved_tag_id | comp.crm_declined_tag_id | comp.crm_on_hold_tag_id
        self.tag_ids -= tags_to_remove

    def action_reset_pending(self):
        for lead in self:
            tag = (lead.company_id or self.env.company).crm_pending_tag_id
            lead._remove_approval_tags()
            if tag:
                lead.tag_ids += tag

    def action_approve_lead(self):
        for lead in self:
            tag = (lead.company_id or self.env.company).crm_approved_tag_id
            lead._remove_approval_tags()
            if tag:
                lead.tag_ids += tag

    def action_decline_lead(self):
        for lead in self:
            tag = (lead.company_id or self.env.company).crm_declined_tag_id
            lead._remove_approval_tags()
            if tag:
                lead.tag_ids += tag

    def action_on_hold_lead(self):
        for lead in self:
            tag = (lead.company_id or self.env.company).crm_on_hold_tag_id
            lead._remove_approval_tags()
            if tag:
                lead.tag_ids += tag