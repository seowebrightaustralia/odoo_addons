from odoo import api, fields, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Extend partner name search to include sh_firstname and sh_lastname.
    # Odoo v18 uses _rec_names_search to drive name_search / M2O autocomplete.
    _rec_names_search = [
        'complete_name',
        'email',
        'ref',
        'vat',
        'company_registry',
        'sh_firstname',
        'sh_lastname',
    ]

    sh_full_name_search = fields.Char(
        string='First or Last Name',
        compute='_compute_sh_full_name_search',
        search='_search_sh_full_name',
        store=False,
    )

    def _compute_sh_full_name_search(self):
        for rec in self:
            parts = filter(None, [rec.sh_firstname, rec.sh_lastname])
            rec.sh_full_name_search = ' '.join(parts)

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

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)
        # Handle "Firstname Lastname" combined search for M2O autocomplete.
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
