# -*- coding: utf-8 -*-
# =============================================================================
#  Chart of Accounts by Business Type
# -----------------------------------------------------------------------------
#  Location  : King Abdulaziz Branch Road, Riyadh, Saudi Arabia
#  Email     : sales@leapai.ai
#  Phone     : +966 53 553 3627
#  Website   : https://leapai.ai
#  Developer : Abdulkaraim Osman — Tech Manager | Backend Engineer | DevOps Engineer
#              at Bab International Corp For Specialized Services
#  LinkedIn  : https://www.linkedin.com/in/abdulkaraim-o-385b7a110/
# =============================================================================
{
    'name': 'Chart of Accounts by Business Type',
    'version': '19.0.1.0.0',
    'summary': 'Generate a ready-made Chart of Accounts for Construction, Rent, Trading, Manufacturing, Services and Restaurant',
    'description': '''
Generate a full, structured Chart of Accounts in one click.
Choose your business model — Construction, Real Estate & Rent,
Trading, Manufacturing, Professional Services or Restaurant —
and the module creates all account codes, names and types
pre-configured and ready to use.

Supports Arabic names for every account.
    ''',
    'author': 'leapai.ai',
    'maintainer': 'Abdulkaraim Osman',
    'support': 'sales@leapai.ai',
    'website': 'https://leapai.ai',
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/coa_template_data.xml',
        'views/coa_template_views.xml',
        'wizard/generate_coa_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/screenshot_01_wizard_step1.png',
        'static/description/screenshot_02_preview.png',
        'static/description/screenshot_03_accounts_list.png',
        'static/description/screenshot_04_groups.png',
        'static/description/screenshot_05_overview.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
