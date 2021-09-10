# -*- coding: utf-8 -*-

{
    'name': 'POS Extend Main Screen',
    'version': '12.0.1.0.0',
    'summary': 'Allows you to update the main POS screen ',
    'author': 'Nathan Quijoux',
    'website': "http://www.captivea.com",
    'company': 'Captivea',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_main_view.xml',
    ],
    'qweb': [
        # 'static/src/xml/pos_main.xml',
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
