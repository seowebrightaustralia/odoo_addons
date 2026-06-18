# -*- coding: utf-8 -*-
{
    'name': 'Webright Global Search',
    'version': '18.0.1.6.0',
    'summary': 'Search across all Odoo records instantly — press Ctrl+Shift+F',
    'description': """
        Global search across Contacts, Sale Orders, Tasks, Tickets, Invoices,
        Products, Projects, Deliveries, Employees, and more.

        Usage:
          • Press Ctrl+Shift+F to open the search dialog.
          • Type any keyword, name, number, or reference (e.g. Jick, INV-11942).
          • Results appear instantly grouped by record type.
          • Click any result to open the record directly.
    """,
    'category': 'Tools',
    'author': 'Webright Capital',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'webright_global_search/static/src/js/global_search.js',
            'webright_global_search/static/src/xml/global_search.xml',
            'webright_global_search/static/src/scss/global_search.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
