from odoo import api, fields, models
from odoo.osv import expression


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    _rec_names_search = ['name', 'partner_name', 'email_from', 'sh_firstname', 'sh_lastname']

    # Virtual field that replaces the 'name' field in the search view so the
    # broad Enter-key search calls _search_sh_lead (settings-aware) instead of
    # Odoo's default direct ('name', 'ilike', value) SQL clause.
    sh_lead_search = fields.Char(
        string='Search All Fields',
        compute='_compute_sh_lead_search',
        search='_search_sh_lead',
        store=False,
    )
    sh_full_name_search = fields.Char(
        string='First or Last Name',
        compute='_compute_sh_full_name_search',
        search='_search_sh_full_name',
        store=False,
    )
    # Virtual Char — description is Html (no search widget in v18 → CrmKanbanArchParser crash).
    sh_notes_search = fields.Char(
        string='Notes & Messages',
        compute='_compute_sh_notes_search',
        search='_search_sh_notes',
        store=False,
    )

    def _compute_sh_lead_search(self):
        for rec in self:
            rec.sh_lead_search = rec.name or ''

    def _compute_sh_full_name_search(self):
        for rec in self:
            rec.sh_full_name_search = ' '.join(filter(None, [rec.sh_firstname, rec.sh_lastname]))

    def _compute_sh_notes_search(self):
        for rec in self:
            rec.sh_notes_search = ''

    def _enabled(self, key, default=True):
        val = self.env['ir.config_parameter'].sudo().get_param(
            key, 'True' if default else 'False'
        )
        # Odoo v18 stores str(bool): 'True'/'False'. Guard legacy '1'/'0' too.
        return val.lower() not in ('false', '0', '')

    def _search_sh_lead(self, operator, value):
        domain = [('name', operator, value)]

        if self._enabled('crm_search.partner_name'):
            domain = expression.OR([domain, [('partner_name', operator, value)]])
        if self._enabled('crm_search.partner_id_name'):
            domain = expression.OR([domain, [('partner_id.name', operator, value)]])
        if self._enabled('crm_search.email_from'):
            domain = expression.OR([domain, [('email_from', operator, value)]])
        if self._enabled('crm_search.contact_name'):
            domain = expression.OR([domain, [('contact_name', operator, value)]])
        if self._enabled('crm_search.sh_names'):
            if operator.endswith('like') and value and ' ' in value:
                parts = value.split(' ', 1)
                sh_domain = expression.OR([
                    expression.AND([
                        [('sh_firstname', operator, parts[0])],
                        [('sh_lastname', operator, parts[1])],
                    ]),
                    expression.AND([
                        [('sh_firstname', operator, parts[1])],
                        [('sh_lastname', operator, parts[0])],
                    ]),
                ])
            else:
                sh_domain = ['|',
                    ('sh_firstname', operator, value),
                    ('sh_lastname', operator, value),
                ]
            domain = expression.OR([domain, sh_domain])
        if self._enabled('crm_search.notes'):
            domain = expression.OR([domain, [('description', operator, value)]])
        if self._enabled('crm_search.messages', False):
            domain = expression.OR([domain, [('message_ids.body', operator, value)]])

        return domain

    def _search_sh_full_name(self, operator, value):
        if operator in ('ilike', 'like', '=ilike', '=like') and value and ' ' in value:
            parts = value.split(' ', 1)
            return expression.OR([
                expression.AND([
                    [('sh_firstname', operator, parts[0])],
                    [('sh_lastname', operator, parts[1])],
                ]),
                expression.AND([
                    [('sh_firstname', operator, parts[1])],
                    [('sh_lastname', operator, parts[0])],
                ]),
            ])
        return ['|', ('sh_firstname', operator, value), ('sh_lastname', operator, value)]

    def _search_sh_notes(self, operator, value):
        parts = []
        if self._enabled('crm_search.notes'):
            parts.append(('description', operator, value))
        if self._enabled('crm_search.messages', False):
            parts.append(('message_ids.body', operator, value))
        if not parts:
            return [('id', '=', False)]
        if len(parts) == 1:
            return [parts[0]]
        return ['|'] + [list(p) for p in parts]

    @api.model
    def _search_display_name(self, operator, value):
        # Delegates to _search_sh_lead so M2O lookups and search bar use
        # the same settings-aware logic. Products module overrides _search_sh_lead.
        return self._search_sh_lead(operator, value)
