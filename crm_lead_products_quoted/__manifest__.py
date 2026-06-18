{
    'name': 'CRM Lead Products Quoted',
    'version': '1.0',
    'category': 'CRM',
    'summary': 'Adds a Products Quoted tab to CRM Lead/Opportunity form.',
    'author': 'SEOWebright',
    'depends': ['crm', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
