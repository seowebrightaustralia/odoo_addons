from odoo import api, fields, models
from odoo.osv import expression


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Extend autocomplete dropdown to show leads matching by partner name,
    # sh_firstname, or sh_lastname (Odoo default is just 'name').
    _rec_names_search = ['name', 'partner_name', 'email_from', 'sh_firstname', 'sh_lastname']

    sh_full_name_search = fields.Char(
        string='First or Last Name',
        compute='_compute_sh_full_name_search',
        search='_search_sh_full_name',
        store=False,
    )
    # Virtual Char field so the search view gets a safe Char widget instead of
    # the Html widget (description) which has no search widget in Odoo v18 and
    # causes CrmKanbanArchParser to crash with "Cannot read properties of undefined".
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
        return ['|', ('description', operator, value), ('message_ids.body', operator, value)]

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)
        # Combined "Firstname Lastname" search in CRM autocomplete.
        if operator.endswith('like') and value and ' ' in value:
            parts = value.split(' ', 1)
            combined = expression.OR([
                expression.AND([
                    [('sh_firstname', operator, parts[0])],
                    [('sh_lastname', operator, parts[1])],
                ]),
                expression.AND([
                    [('sh_firstname', operator, parts[1])],
                    [('sh_lastname', operator, parts[0])],
                ]),
            ])
            domain = expression.OR([domain, combined])
        return domain
