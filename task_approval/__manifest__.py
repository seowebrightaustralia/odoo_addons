# -*- coding: utf-8 -*-
{
    'name': 'Project Task Approvals',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Tag-based task approvals with Settings configuration',
    'depends': ['project'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}