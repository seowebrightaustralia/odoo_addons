from odoo import api, fields, models

# Defaults used when ir.config_parameter has no stored value (first install).
CRM_SEARCH_DEFAULTS = {
    'crm_search.partner_name':    True,
    'crm_search.partner_id_name': True,
    'crm_search.email_from':      True,
    'crm_search.contact_name':    True,
    'crm_search.sh_names':        True,
    'crm_search.notes':           True,
    'crm_search.messages':        False,
    'crm_search.products':        True,
    'crm_search.product_categ':   False,
}

# Ordered (field_name, param_key) pairs — shared by get_values and set_values.
_FIELD_PARAMS = [
    ('crm_search_partner_name',    'crm_search.partner_name'),
    ('crm_search_partner_id_name', 'crm_search.partner_id_name'),
    ('crm_search_email_from',      'crm_search.email_from'),
    ('crm_search_contact_name',    'crm_search.contact_name'),
    ('crm_search_sh_names',        'crm_search.sh_names'),
    ('crm_search_notes',           'crm_search.notes'),
    ('crm_search_messages',        'crm_search.messages'),
    ('crm_search_products',        'crm_search.products'),
    ('crm_search_product_categ',   'crm_search.product_categ'),
]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # config_parameter wires each field into Odoo's built-in save/load pipeline.
    # The explicit @api.model get_values below overrides the auto-read to handle
    # first-install defaults (param not yet stored → return True/False from
    # CRM_SEARCH_DEFAULTS instead of False which Odoo would produce by default).
    crm_search_partner_name = fields.Boolean(
        string='Partner Name',
        config_parameter='crm_search.partner_name',
    )
    crm_search_partner_id_name = fields.Boolean(
        string='Company Name',
        config_parameter='crm_search.partner_id_name',
    )
    crm_search_email_from = fields.Boolean(
        string='Email',
        config_parameter='crm_search.email_from',
    )
    crm_search_contact_name = fields.Boolean(
        string='Contact Name',
        config_parameter='crm_search.contact_name',
    )
    crm_search_sh_names = fields.Boolean(
        string='First / Last Name (sh_first_last_name)',
        config_parameter='crm_search.sh_names',
    )
    crm_search_notes = fields.Boolean(
        string='Internal Notes',
        config_parameter='crm_search.notes',
    )
    crm_search_messages = fields.Boolean(
        string='Chatter Messages',
        config_parameter='crm_search.messages',
    )
    crm_search_products = fields.Boolean(
        string='Products Quoted (name)',
        config_parameter='crm_search.products',
    )
    crm_search_product_categ = fields.Boolean(
        string='Products Quoted (ecommerce category)',
        config_parameter='crm_search.product_categ',
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        for fname, key in _FIELD_PARAMS:
            val = ICP.get_param(key)
            if val is False:
                # Not yet stored — use module default so checkboxes open correctly.
                res[fname] = CRM_SEARCH_DEFAULTS[key]
            else:
                # Odoo v18 stores str(bool): 'True' / 'False'.
                res[fname] = (val.strip() == 'True')
        return res

    def set_values(self):
        super().set_values()
        # super() already handles config_parameter fields; we also write
        # explicitly to guarantee 'True'/'False' string format expected by
        # CrmLead._enabled().
        ICP = self.env['ir.config_parameter'].sudo()
        for fname, key in _FIELD_PARAMS:
            ICP.set_param(key, str(self[fname]))
