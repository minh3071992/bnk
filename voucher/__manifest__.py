# -*- coding: utf-8 -*-
{
    'name': "Voucher Management",

    'summary': """Manage voucher""",

    'description': """
        Voucher management module for managing voucher
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        #'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/sale_order_apply_voucher.xml',
        # 'templates.xml',
        'views/voucher.xml',
        #'views/partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
