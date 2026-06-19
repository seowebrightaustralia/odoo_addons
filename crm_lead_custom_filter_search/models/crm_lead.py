from odoo import api, fields, models
from odoo.osv import expression


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    _rec_names_search = ['name', 'partner_name', 'email_from', 'sh_firstname', 'sh_lastname']

    sh_full_name_search = fields.Char(
        string='First or Last Name',
        compute='_compute_sh_full_name_search',
        search='_search_sh_full_name',
        store=False,
    )
    # Virtual Char — description is Html (no search widget in v18 → CrmKanbanArchParser crash).
    # Wrap both notes and chatter behind a safe Char so the arch parser resolves a widget type.
    sh_notes_search = fields.Char(
        string='Notes & Messages',
        compute='_compute_sh_notes_search',
        search='_search_sh_notes',
        store=False,
    )

    def _compute_sh_full_name_search(self):
        for rec in self:
            rec.sh_full_name_search = ' '.join(filter(None, [rec.sh_firstname, rec.sh_lastname]))

    def _compute_sh_notes_search(self):
        for rec in self:
            rec.sh_notes_search = ''

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
        get = self.env['ir.config_parameter'].sudo().get_param
        notes_on = get('crm_search.notes', '1') != '0'
        msgs_on = get('crm_search.messages', '0') != '0'
        parts = []
        if notes_on:
            parts.append(('description', operator, value))
        if msgs_on:
            parts.append(('message_ids.body', operator, value))
        if not parts:
            return [('id', '=', False)]
        if len(parts) == 1:
            return [parts[0]]
        return ['|'] + [list(p) for p in parts]

    @api.model
    def _search_display_name(self, operator, value):
        get = self.env['ir.config_parameter'].sudo().get_param
        enabled = lambda key, default='1': get(key, default) != '0'

        # Opportunity name always searched.
        domain = [('name', operator, value)]

        if enabled('crm_search.partner_name'):
            domain = expression.OR([domain, [('partner_name', operator, value)]])
        if enabled('crm_search.partner_id_name'):
            domain = expression.OR([domain, [('partner_id.name', operator, value)]])
        if enabled('crm_search.email_from'):
            domain = expression.OR([domain, [('email_from', operator, value)]])
        if enabled('crm_search.contact_name'):
            domain = expression.OR([domain, [('contact_name', operator, value)]])
        if enabled('crm_search.sh_names'):
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

        return domain
