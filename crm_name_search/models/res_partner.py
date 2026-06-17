from odoo import api, models
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

    @api.model
    def _search_display_name(self, operator, value):
        domain = super()._search_display_name(operator, value)
        # Handle "Firstname Lastname" combined search — split on first space
        # and match both orderings: Alex Dimitrijevski or Dimitrijevski Alex.
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
