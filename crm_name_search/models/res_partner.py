from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Extend partner name search to include sh_firstname and sh_lastname.
    # Odoo v18 uses _rec_names_search to drive name_search / M2O autocomplete.
    # Without this, "Search Customer for: X" only matches the `name` field.
    _rec_names_search = [
        'complete_name',
        'email',
        'ref',
        'vat',
        'company_registry',
        'sh_firstname',
        'sh_lastname',
    ]
