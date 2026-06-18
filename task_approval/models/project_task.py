# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    # The "Ghost Field" that mirrors your tags for the Kanban columns
    approval_status = fields.Selection([
        ('1_pending', '1. Pending'),
        ('2_approved', '2. Approved'),
        ('3_declined', '3. Declined'),
        ('4_on_hold', '4. On-Hold')
    ], string='Approval Status', compute='_compute_approval_status', store=True)

    @api.depends('tag_ids')
    def _compute_approval_status(self):
        for task in self:
            comp = task.company_id or self.env.company
            
            if comp.task_approved_tag_id and comp.task_approved_tag_id in task.tag_ids:
                task.approval_status = '2_approved'
            elif comp.task_declined_tag_id and comp.task_declined_tag_id in task.tag_ids:
                task.approval_status = '3_declined'
            elif comp.task_on_hold_tag_id and comp.task_on_hold_tag_id in task.tag_ids:
                task.approval_status = '4_on_hold'
            else:
                # If it has none of those three tags, it falls into Pending
                task.approval_status = '1_pending'

    def _remove_approval_tags(self):
        """Helper to clear existing approval tags before adding a new one"""
        comp = self.company_id or self.env.company
        tags_to_remove = comp.task_pending_tag_id | comp.task_approved_tag_id | comp.task_declined_tag_id | comp.task_on_hold_tag_id
        self.tag_ids -= tags_to_remove

    def action_reset_pending(self):
        for task in self:
            tag = (task.company_id or self.env.company).task_pending_tag_id
            task._remove_approval_tags()
            if tag:
                task.tag_ids += tag

    def action_approve_task(self):
        for task in self:
            tag = (task.company_id or self.env.company).task_approved_tag_id
            task._remove_approval_tags()
            if tag:
                task.tag_ids += tag

    def action_decline_task(self):
        for task in self:
            tag = (task.company_id or self.env.company).task_declined_tag_id
            task._remove_approval_tags()
            if tag:
                task.tag_ids += tag

    def action_on_hold_task(self):
        for task in self:
            tag = (task.company_id or self.env.company).task_on_hold_tag_id
            task._remove_approval_tags()
            if tag:
                task.tag_ids += tag