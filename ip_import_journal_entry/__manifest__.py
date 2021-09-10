# -*- coding: utf-8 -*-
{
    'name': 'Import Journal Entries',
    'summary': "Import Journal Entries from CSV/Excel",
    'description': "Import Journal Entries from CSV/Excel",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Accounting',
    'version': '12.0.0.1.0',
    'depends': ['account'],

    'data': [
        'wizard/journal_entries_view.xml',
        'views/journal_entries_import_view.xml',
    ],

    'license': "OPL-1",
    'price': 15,
    'currency': "EUR",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/main.png'],
}
