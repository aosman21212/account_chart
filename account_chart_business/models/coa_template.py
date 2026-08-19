from odoo import models, fields, api

BUSINESS_TYPES = [
    ('construction',  'Construction & Contracting — مقاولات وتشييد'),
    ('real_estate',   'Real Estate & Rent — عقارات وإيجارات'),
    ('trading',       'Trading & Retail — تجارة وتجزئة'),
    ('manufacturing', 'Manufacturing — تصنيع'),
    ('services',      'Professional Services — خدمات مهنية'),
    ('restaurant',    'Restaurant & F&B — مطاعم وأغذية'),
]

ACCOUNT_TYPE_SELECTION = [
    ('asset_receivable',        'Receivable'),
    ('asset_cash',              'Bank and Cash'),
    ('asset_current',           'Current Assets'),
    ('asset_non_current',       'Non-current Assets'),
    ('asset_prepayments',       'Prepayments'),
    ('asset_fixed',             'Fixed Assets'),
    ('liability_payable',       'Payable'),
    ('liability_credit_card',   'Credit Card'),
    ('liability_current',       'Current Liabilities'),
    ('liability_non_current',   'Non-current Liabilities'),
    ('equity',                  'Equity'),
    ('equity_unaffected',       'Current Year Earnings'),
    ('income',                  'Income'),
    ('income_other',            'Other Income'),
    ('expense',                 'Expenses'),
    ('expense_depreciation',    'Depreciation'),
    ('expense_direct_cost',     'Cost of Revenue'),
    ('off_balance',             'Off Balance Sheet'),
]


class AccountCoaTemplate(models.Model):
    _name = 'account.coa.template'
    _description = 'Chart of Accounts Template by Business Type'
    _order = 'business_type, sequence, code'

    business_type = fields.Selection(
        BUSINESS_TYPES,
        string='Business Type',
        required=True,
        index=True,
    )
    sequence = fields.Integer(default=10)
    code = fields.Char(
        string='Account Code',
        required=True,
    )
    name = fields.Char(
        string='Account Name (EN)',
        required=True,
    )
    name_ar = fields.Char(string='اسم الحساب (AR)')
    account_type = fields.Selection(
        ACCOUNT_TYPE_SELECTION,
        string='Account Type',
        required=True,
    )
    reconcile = fields.Boolean(
        string='Allow Reconciliation',
        default=False,
        help='Enable for receivable / payable accounts.',
    )
    note = fields.Char(string='Note / Description')

    # ── Display helpers ──────────────────────────────────────────────────
    business_type_label = fields.Char(
        compute='_compute_labels', store=False,
    )
    account_type_label = fields.Char(
        compute='_compute_labels', store=False,
    )

    @api.depends('business_type', 'account_type')
    def _compute_labels(self):
        bt_map = dict(BUSINESS_TYPES)
        at_map = dict(ACCOUNT_TYPE_SELECTION)
        for rec in self:
            rec.business_type_label = bt_map.get(rec.business_type, '')
            rec.account_type_label  = at_map.get(rec.account_type, '')

    # ── Constraint ───────────────────────────────────────────────────────
    _sql_constraints = [
        ('unique_code_business',
         'UNIQUE(code, business_type)',
         'Account code must be unique per business type.'),
    ]
