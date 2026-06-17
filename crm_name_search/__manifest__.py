{
    'name': 'CRM Customer Name Search',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Adds separate First Name and Last Name filters to the CRM search bar.',
    'author': 'SEOWebright',
    'depends': [
        'crm',
        'sh_first_last_name'  # <-- This is the crucial missing piece!
    ],
    'data': [
        'views/crm_lead_search_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}