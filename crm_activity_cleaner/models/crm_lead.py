# -*- coding: utf-8 -*-
from odoo import models, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None, **kwargs):
        # 1. Check Context (Catches standard search bar filters)
        ctx = self.env.context
        is_activity_filter = any(key in ctx for key in [
            'search_default_activities_overdue',
            'search_default_activities_today',
            'search_default_activities_upcoming',
            'search_default_my_activities'
        ])
        
        # 2. Check Domain (Catches the Top-Right Notification Clock Icon)
        if domain and 'activity' in str(domain):
            is_activity_filter = True

        # If an activity filter is active, bypass Odoo's default behavior
        if is_activity_filter:
            # ONLY return the stages that currently have data in them
            return stages

        # 3. Safely call super, explicitly providing 'order' (even if None) 
        # to completely prevent the "missing 1 required positional argument" error!
        return super()._read_group_stage_ids(stages, domain, order)