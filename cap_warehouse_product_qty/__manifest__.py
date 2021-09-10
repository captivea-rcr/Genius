# -*- coding: utf-8 -*-
# Part of CAPTIVEA. Odoo 12 EE.

{
    'name': 'Delivery Order Product Search',
    'version': '12.0.1.0',
    'author': 'Captivea',
    'category': 'stock',
    'website': 'https://www.captivea.us',
    'summary': 'Product Based on warehouse.',
    'description': """
Product Search is limited to the Products available in this Warehouse (Qty on Hand > 0).
""",
    'depends': [
        'stock'
    ],
    'data': [
        'views/view_picking_form.xml',
    ],
    'installable': True,
    'auto_install': False,
}
