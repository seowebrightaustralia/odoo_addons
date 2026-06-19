{
    'name': 'CRM Custom Filter Search',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Extends CRM Lead/Opportunity search to match opportunity name, partner name, sh_firstname, and sh_lastname.',
    'author': 'SEOWebright',
    'depends': [
        'crm',
        'contacts',
        'base_setup',
        'sh_first_last_name',
    ],
    'data': [
        'views/res_partner_search_views.xml',
        'views/crm_lead_search_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
