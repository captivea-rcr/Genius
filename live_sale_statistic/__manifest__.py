# -*- coding: utf-8 -*-
{
    'name' : 'Live Sale Statistic',
    'version' : '1.2',
    'summary': 'Live Sale Statistic',
    'author':'Mithun Turubudi',
    'license': 'OPL-1',
    'sequence': 15,
    'description': """
Live Sale Statistic
====================
 Live Sale Statistic :- this module helps to view a Statistical representation as line chart.  will
 calculate the confirm sale order amount minute wise and show it on graphical view(line chart)
    """,
    'category': 'Sales',
    'website': 'https://www.odoo.com/',
    'images' : [],
    'depends' : ['sale'],
    'data': [
        'views/assest_backend.xml',
        'views/sale_menu.xml'
        ],
    'demo': [],
    'qweb': ['static/src/xml/statistic.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
