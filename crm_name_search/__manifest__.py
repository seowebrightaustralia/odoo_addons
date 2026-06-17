{
    'name': 'CRM Customer Name Search',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Adds separate First Name and Last Name filters to the CRM and Contact search bars.',
    'author': 'SEOWebright',
    'depends': [
        'crm',
        'contacts',          # Added dependency for the Contacts module
        'sh_first_last_name' 
    ],
    'data': [
        'views/crm_lead_search_views.xml',
        'views/res_partner_search_views.xml', # Added the new view file here
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}