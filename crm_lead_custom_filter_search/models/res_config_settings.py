from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ── CRM Lead Search Fields ──────────────────────────────────────────────
    # Each Boolean controls whether that field is included in the broad Enter-key
    # search in CRM. Stored in ir.config_parameter as '1' (on) or '0' (off).

    crm_search_partner_name = fields.Boolean(
        string='Partner Name',
        config_parameter='crm_search.partner_name',
        default=True,
    )
    crm_search_partner_id_name = fields.Boolean(
        string='Company Name',
        config_parameter='crm_search.partner_id_name',
        default=True,
    )
    crm_search_email_from = fields.Boolean(
        string='Email',
        config_parameter='crm_search.email_from',
        default=True,
    )
    crm_search_contact_name = fields.Boolean(
        string='Contact Name',
        config_parameter='crm_search.contact_name',
        default=True,
    )
    crm_search_sh_names = fields.Boolean(
        string='First / Last Name (sh_first_last_name)',
        config_parameter='crm_search.sh_names',
        default=True,
    )
    crm_search_notes = fields.Boolean(
        string='Internal Notes',
        config_parameter='crm_search.notes',
        default=True,
    )
    crm_search_messages = fields.Boolean(
        string='Chatter Messages',
        config_parameter='crm_search.messages',
        default=False,
    )
    crm_search_products = fields.Boolean(
        string='Products Quoted (name)',
        config_parameter='crm_search.products',
        default=True,
    )
    crm_search_product_categ = fields.Boolean(
        string='Products Quoted (ecommerce category)',
        config_parameter='crm_search.product_categ',
        default=False,
    )
