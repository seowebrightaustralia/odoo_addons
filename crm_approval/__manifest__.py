# -*- coding: utf-8 -*-
{
    'name': 'CRM Lead Approvals',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Tag-based Lead/Opportunity approvals with Settings configuration',
    'depends': ['crm'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}