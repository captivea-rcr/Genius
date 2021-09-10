# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

{
    'name': 'UOM Unit',
    'version': '12.0.1.0',
    'author': 'Captivea',
    'category': 'Base',
    'website': 'https://www.captivea.us',
    'summary': 'Not allow decimal precision in Unit(s) for Sales Order Lines and StockPicking Order Lines.',
    'description': """
Not allow decimal precision in Unit(s).
""",
    'depends': [
        'sale',
        'stock'
    ],
    'installable': True,
    'auto_install': False,
}
