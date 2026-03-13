# -*- coding: utf-8 -*-
{
    'name': "Recycle Bin",

    'summary': """
        Recycle Bin | Trash Management for deleted record history, include the screenshot of the data and 
        ability to restore deleted data""",

    'description': """
        Recycle Bin | Trash Management for deleted record history, include the screenshot of the data and 
        ability to restore deleted data
    """,

    'author': "Adi Nurcahyo",
    'website': "https://www.linkedin.com/in/adinc13",
    'support': "https://www.linkedin.com/in/adinc13",
    'category': 'Tools',
    'version': '18.0.1.0.0',
    'sequence': 0,
    "auto_install": False,
    "installable": True,
    "application": True,
    "license": "OPL-1",
    "images": [
        'static/description/banner.png'
    ],
    # "price": 114.29,
    # discount price for first release
    "price": 43.49,
    "currency": "EUR",
    "live_test_url": "https://apps.adinc.my.id/login_employee?login=demo&password=demo&action=recycle_bin.action_window_recycle_bin",
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_setup'
    ],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/recycle_bin.xml',
        'views/res_config_settings.xml',
        'views/wizard_empty_trash.xml',
        'views/wizard_advance_restore.xml',
    ],
    "assets": {
        'web.assets_backend': [
            'recycle_bin/static/src/lib/html2canvas.min.js',
            'recycle_bin/static/src/js/basic_model.js',
        ]
    },
}
