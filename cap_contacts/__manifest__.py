# coding: utf-8
# Part of CAPTIVEA. Odoo 12 EE.

{
    'name': "cap_contacts",
    'author': "captivea-ilo",
    'version': "12.0",
    'depends': ["base", "contacts"],
    'summary': "",
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'view/res_partner.xml',
        'wizard/partner_creation.xml',
        ],
    'installable': True
}
