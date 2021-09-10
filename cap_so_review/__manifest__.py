# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

{
    'name': 'Sale Order Review',
    'version': '12.0.1.0',
    'author': 'Captivea',
    'category': 'Sales',
    'website': 'https://www.captivea.us',
    'summary': 'Review for sale order.',
    'description': """Review for sale order.""",
    'depends': [
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/so_review_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
