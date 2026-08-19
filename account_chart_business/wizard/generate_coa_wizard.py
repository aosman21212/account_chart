from odoo import models, fields, api, _
from odoo.exceptions import UserError

# ── Account-group definitions ──────────────────────────────────────────────
# Level-1  (1-digit prefix) — same across all business types
# Tuple: (prefix, name_en, name_ar)
_GROUP_LEVEL1 = [
    ('1', 'Assets',          'الأصول'),
    ('2', 'Liabilities',     'الخصوم'),
    ('3', 'Equity',          'حقوق الملكية'),
    ('4', 'Revenue',         'الإيرادات'),
    ('5', 'Cost of Revenue', 'تكلفة الإيرادات'),
    ('6', 'Expenses',        'المصروفات'),
]

# Level-2  (2-digit prefix) — business-type-specific sub-groups
# Derived from the actual account code ranges in coa_template_data.xml
_GROUP_LEVEL2 = {
    'construction': [
        # 1xxx — Assets
        ('11', 'Cash & Banks',                 'النقد والبنوك'),
        ('12', 'Receivables & Advances',       'الذمم والدفعات المقدمة'),
        ('13', 'Materials & Inventory',        'المواد والمخزون'),
        ('14', 'WIP & Contract Billing',       'مشاريع تحت التنفيذ والمستخلصات'),
        ('15', 'Fixed Assets',                 'الأصول الثابتة'),
        ('16', 'Long-term Deposits',           'الودائع طويلة الأجل'),
        # 2xxx — Liabilities
        ('21', 'Trade Payables',               'الذمم الدائنة التجارية'),
        ('22', 'Client Advances & Billings',   'دفعات مقدمة من العملاء'),
        ('23', 'Statutory Payables',           'المستحقات النظامية'),
        ('24', 'Long-term Debt',               'الديون طويلة الأجل'),
        # 3xxx — Equity
        ('30', 'Shareholders Equity',          'حقوق المساهمين'),
        # 4xxx — Revenue
        ('41', 'Contract Revenue',             'إيرادات المقاولات'),
        ('42', 'Other Income',                 'إيرادات أخرى'),
        # 5xxx — Cost of Revenue
        ('51', 'Direct Materials Cost',        'تكلفة المواد المباشرة'),
        ('52', 'Direct Labor Cost',            'تكلفة العمالة المباشرة'),
        ('53', 'Subcontractor Costs',          'تكاليف المقاولين من الباطن'),
        ('54', 'Equipment & Machinery',        'تكاليف المعدات والآليات'),
        ('55', 'Site Indirect Costs',          'التكاليف غير المباشرة للموقع'),
        # 6xxx — Expenses
        ('61', 'Personnel & HR',               'الرواتب والموارد البشرية'),
        ('62', 'Office & Admin Expenses',      'مصروفات المكتب والإدارة'),
        ('63', 'Finance Charges',              'التكاليف التمويلية'),
        ('64', 'Other G&A Expenses',           'مصروفات عمومية وإدارية أخرى'),
    ],
    'real_estate': [
        # 1xxx — Assets
        ('11', 'Cash & Banks',                 'النقد والبنوك'),
        ('12', 'Receivables & Prepaid',        'الذمم والمصروفات المقدمة'),
        ('13', 'Investment Properties',        'العقارات الاستثمارية'),
        ('14', 'Other Fixed Assets',           'أصول ثابتة أخرى'),
        ('15', 'Long-term Deposits',           'الودائع طويلة الأجل'),
        # 2xxx — Liabilities
        ('21', 'Trade Payables',               'الذمم الدائنة'),
        ('22', 'Tenant Liabilities',           'التزامات المستأجرين'),
        ('23', 'Mortgage & Long-term Debt',    'الرهن العقاري والديون طويلة الأجل'),
        # 3xxx — Equity
        ('30', 'Owners Equity',                'حقوق الملاك'),
        # 4xxx — Revenue
        ('41', 'Rental & Property Income',     'إيرادات الإيجار والعقارات'),
        ('42', 'Other Income',                 'إيرادات أخرى'),
        # 5xxx — Cost of Revenue
        ('51', 'Property Direct Costs',        'التكاليف المباشرة للعقار'),
        ('52', 'Depreciation',                 'الاستهلاك'),
        # 6xxx — Expenses
        ('61', 'Management Expenses',          'مصروفات الإدارة'),
        ('62', 'Property Operating Costs',     'تكاليف تشغيل العقارات'),
        ('63', 'Finance Costs',                'التكاليف التمويلية'),
    ],
    'trading': [
        # 1xxx — Assets
        ('11', 'Cash & Banks',                 'النقد والبنوك'),
        ('12', 'Receivables & Prepaid',        'الذمم والمدفوعات المقدمة'),
        ('13', 'Inventory',                    'المخزون'),
        ('14', 'Fixed Assets',                 'الأصول الثابتة'),
        # 2xxx — Liabilities
        ('21', 'Trade & Other Payables',       'الذمم الدائنة والمستحقات'),
        ('22', 'Bank Facilities',              'التسهيلات المصرفية'),
        # 3xxx — Equity
        ('30', 'Shareholders Equity',          'حقوق المساهمين'),
        # 4xxx — Revenue
        ('41', 'Sales Revenue',                'إيرادات المبيعات'),
        ('42', 'Other Income',                 'إيرادات أخرى'),
        # 5xxx — Cost of Revenue  (codes 5001–5003 → prefix "50")
        ('50', 'Cost of Goods Sold',           'تكلفة البضاعة المباعة'),
        # 6xxx — Expenses
        ('61', 'Personnel Expenses',           'مصروفات الموظفين'),
        ('62', 'Operating Expenses',           'المصروفات التشغيلية'),
        ('63', 'Finance Charges',              'التكاليف التمويلية'),
        ('64', 'Depreciation & Write-offs',    'الاستهلاك والإطفاء'),
    ],
    'manufacturing': [
        # 1xxx — Assets
        ('11', 'Cash & Banks',                 'النقد والبنوك'),
        ('12', 'Receivables & Prepaid',        'الذمم والمدفوعات المقدمة'),
        ('13', 'Inventory & WIP',              'المخزون والإنتاج تحت التشغيل'),
        ('14', 'Factory & Fixed Assets',       'المصنع والأصول الثابتة'),
        # 2xxx — Liabilities
        ('21', 'Trade & Statutory Payables',   'الذمم الدائنة والمستحقات'),
        ('22', 'Long-term Debt',               'الديون طويلة الأجل'),
        # 3xxx — Equity
        ('30', 'Shareholders Equity',          'حقوق المساهمين'),
        # 4xxx — Revenue
        ('41', 'Sales Revenue',                'إيرادات المبيعات'),
        # 5xxx — Cost of Revenue
        ('51', 'Direct Materials',             'المواد الخام المباشرة'),
        ('52', 'Direct Labor',                 'العمالة المباشرة'),
        ('53', 'Factory Overhead',             'التكاليف الصناعية غير المباشرة'),
        # 6xxx — Expenses
        ('61', 'Admin & Management',           'الإدارة والمصروفات العامة'),
        ('62', 'Sales & Marketing',            'المبيعات والتسويق'),
        ('63', 'Finance Costs',                'التكاليف التمويلية'),
    ],
    'services': [
        # 1xxx — Assets
        ('11', 'Cash & Banks',                 'النقد والبنوك'),
        ('12', 'Receivables & Prepaid',        'الذمم والمدفوعات المقدمة'),
        ('13', 'Fixed Assets',                 'الأصول الثابتة'),
        ('14', 'Intangible Assets',            'الأصول غير الملموسة'),
        # 2xxx — Liabilities
        ('21', 'Trade & Other Payables',       'الذمم الدائنة والمستحقات'),
        # 3xxx — Equity
        ('30', 'Partners Equity',              'حقوق الشركاء'),
        # 4xxx — Revenue
        ('41', 'Service Revenue',              'إيرادات الخدمات'),
        # 5xxx — Cost of Revenue
        ('51', 'Direct Service Costs',         'التكاليف المباشرة للخدمات'),
        # 6xxx — Expenses
        ('61', 'Admin & Support',              'الإدارة والدعم'),
        ('62', 'Office & Operations',          'مصروفات المكتب والعمليات'),
        ('63', 'Other & Finance Expenses',     'مصروفات أخرى وتكاليف تمويلية'),
    ],
    'restaurant': [
        # 1xxx — Assets
        ('11', 'Cash & Receivables',           'النقد والذمم المدينة'),
        ('12', 'F&B Inventory',                'مخزون الأغذية والمشروبات'),
        ('13', 'Fixed Assets',                 'الأصول الثابتة'),
        # 2xxx — Liabilities
        ('21', 'Trade & Other Payables',       'الذمم الدائنة والمستحقات'),
        # 3xxx — Equity
        ('30', 'Owners Equity',                'حقوق الملاك'),
        # 4xxx — Revenue
        ('41', 'Food & Beverage Revenue',      'إيرادات الأغذية والمشروبات'),
        ('42', 'Other Revenue',                'إيرادات أخرى'),
        # 5xxx — Cost of Revenue
        ('51', 'F&B Direct Costs',             'تكاليف الأغذية والمشروبات المباشرة'),
        # 6xxx — Expenses
        ('61', 'Staff Expenses',               'مصروفات الموظفين'),
        ('62', 'Restaurant Operations',        'تكاليف تشغيل المطعم'),
        ('63', 'Other & Finance Costs',        'مصروفات أخرى وتكاليف تمويلية'),
    ],
}


class GenerateCoaWizard(models.TransientModel):
    _name = 'account.coa.generate.wizard'
    _description = 'Generate Chart of Accounts from Business Template'

    # ── Step 1 inputs ─────────────────────────────────────────────────────
    business_type = fields.Selection(
        [
            ('construction',  'Construction & Contracting — مقاولات وتشييد'),
            ('real_estate',   'Real Estate & Rent — عقارات وإيجارات'),
            ('trading',       'Trading & Retail — تجارة وتجزئة'),
            ('manufacturing', 'Manufacturing — تصنيع'),
            ('services',      'Professional Services — خدمات مهنية'),
            ('restaurant',    'Restaurant & F&B — مطاعم وأغذية'),
        ],
        string='Business Type',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    use_arabic_names = fields.Boolean(
        string='Use Arabic Names',
        default=False,
    )

    # ── Replace / reset option ─────────────────────────────────────────────
    replace_existing = fields.Boolean(
        string='Replace Existing Chart of Accounts',
        default=True,
        help=(
            'Before creating new accounts:\n'
            '• Accounts with NO journal entries → permanently deleted.\n'
            '• Accounts WITH journal entries → archived (history preserved).\n'
            '• Existing account groups → replaced with business-specific groups.\n\n'
            'This gives you a clean slate for the new business chart.'
        ),
    )
    # stats populated by action_load_preview
    count_will_delete    = fields.Integer(readonly=True)
    count_will_deprecate = fields.Integer(readonly=True)

    # ── Preview lines (new accounts to create) ────────────────────────────
    preview_ids = fields.One2many(
        'account.coa.wizard.line', 'wizard_id',
        string='New Accounts Preview',
    )
    preview_loaded = fields.Boolean(default=False)

    count_new      = fields.Integer(compute='_compute_counts')
    count_adjusted = fields.Integer(compute='_compute_counts')
    count_total    = fields.Integer(compute='_compute_counts')
    count_groups   = fields.Integer(compute='_compute_counts')

    @api.depends('preview_ids', 'preview_ids.status', 'business_type')
    def _compute_counts(self):
        for wiz in self:
            wiz.count_new      = len(wiz.preview_ids.filtered(lambda l: l.status == 'new'))
            wiz.count_adjusted = len(wiz.preview_ids.filtered(lambda l: l.status == 'adjusted'))
            wiz.count_total    = len(wiz.preview_ids)
            level2 = _GROUP_LEVEL2.get(wiz.business_type, [])
            wiz.count_groups   = len(_GROUP_LEVEL1) + len(level2)

    # ── Helpers ────────────────────────────────────────────────────────────
    def _unique_code(self, desired, taken):
        """Return a code not in `taken`, adding a letter suffix if needed."""
        if desired not in taken:
            taken.add(desired)
            return desired, False

        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            candidate = desired + letter
            if candidate not in taken:
                taken.add(candidate)
                return candidate, True

        for l1 in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            for l2 in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                candidate = desired + l1 + l2
                if candidate not in taken:
                    taken.add(candidate)
                    return candidate, True

        raise UserError(
            _('Cannot find a unique code for "%s". Please clean up existing accounts first.') % desired
        )

    def _classify_existing_accounts(self):
        """
        Split company accounts into:
          deletable    — no journal entries → safe to unlink
          deprecatable — has entries → must keep, archive (active=False)
        """
        company_accounts = self.env['account.account'].search(
            [('company_ids', 'in', self.company_id.id)]
        )
        deletable    = self.env['account.account']
        deprecatable = self.env['account.account']

        for acc in company_accounts:
            has_lines = self.env['account.move.line'].search_count(
                [('account_id', '=', acc.id)], limit=1
            )
            if has_lines:
                deprecatable |= acc
            else:
                deletable |= acc

        return deletable, deprecatable

    def _create_account_groups(self):
        """
        Create level-1 (1-digit) and level-2 (2-digit) account groups for
        the selected business type and company.

        Odoo auto-assigns parent_id via _adapt_parent_account_group:
        a group with prefix "11" automatically becomes a child of "1".
        """
        self.ensure_one()
        level2 = _GROUP_LEVEL2.get(self.business_type, [])
        Group  = self.env['account.group']
        created = []

        # All groups to create: level1 first, then level2
        all_defs = [
            (prefix, name_en, name_ar)
            for prefix, name_en, name_ar in _GROUP_LEVEL1
        ] + [
            (prefix, name_en, name_ar)
            for prefix, name_en, name_ar in level2
        ]

        for prefix, name_en, name_ar in all_defs:
            name = name_ar if self.use_arabic_names else name_en
            grp = Group.create({
                'name':              name,
                'code_prefix_start': prefix,
                'code_prefix_end':   prefix,
                'company_id':        self.company_id.id,
            })
            created.append(grp.id)

        return created

    # ── Load preview ──────────────────────────────────────────────────────
    def action_load_preview(self):
        self.ensure_one()
        if not self.business_type:
            raise UserError(_('Please select a business type first.'))

        templates = self.env['account.coa.template'].search(
            [('business_type', '=', self.business_type)],
            order='sequence, code',
        )
        if not templates:
            raise UserError(_(
                'No template accounts found for "%s".\n'
                'Check Configuration → Account Templates.'
            ) % self.business_type)

        # ── Count what will be removed (for the warning banner) ──
        if self.replace_existing:
            deletable, deprecatable = self._classify_existing_accounts()
            self.count_will_delete    = len(deletable)
            self.count_will_deprecate = len(deprecatable)
        else:
            self.count_will_delete    = 0
            self.count_will_deprecate = 0

        # ── Build taken-codes set ──
        # When replacing, the old codes will disappear, so only codes that
        # belong to OTHER companies (or have entries and will stay) are truly
        # taken after the reset.
        if self.replace_existing:
            deletable_ids = deletable.ids
            surviving = self.env['account.account'].search([
                ('id', 'not in', deletable_ids),
                ('company_ids', 'not in', self.company_id.id),
            ])
            deprecatable_codes = set(deprecatable.mapped('code'))
            taken_codes = set(surviving.mapped('code')) | deprecatable_codes
        else:
            taken_codes = set(
                self.env['account.account'].sudo().search([]).mapped('code')
            )

        # ── Build preview lines ──
        self.preview_ids.unlink()
        lines = []
        for tmpl in templates:
            name = tmpl.name_ar if (self.use_arabic_names and tmpl.name_ar) else tmpl.name
            final_code, adjusted = self._unique_code(tmpl.code, taken_codes)
            lines.append({
                'wizard_id':     self.id,
                'template_id':   tmpl.id,
                'original_code': tmpl.code,
                'code':          final_code,
                'name':          name,
                'name_ar':       tmpl.name_ar or '',
                'account_type':  tmpl.account_type,
                'reconcile':     tmpl.reconcile,
                'status':        'adjusted' if adjusted else 'new',
                'selected':      True,
            })

        self.env['account.coa.wizard.line'].create(lines)
        self.preview_loaded = True
        # Re-open the same wizard record — must include `views` list or
        # Odoo 19 JS _preprocessAction crashes with "cannot read .map of undefined"
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'flags': {'mode': 'edit'},
        }

    # ── Generate ──────────────────────────────────────────────────────────
    def action_generate(self):
        self.ensure_one()
        if not self.preview_loaded:
            raise UserError(_('Please load the preview first.'))

        to_create = self.preview_ids.filtered(lambda l: l.selected)
        if not to_create:
            raise UserError(_('No accounts selected. Tick at least one account.'))

        # ── Step 1: Reset old chart of accounts ──────────────────────────
        if self.replace_existing:
            deletable, deprecatable = self._classify_existing_accounts()

            # Try to permanently delete accounts with no journal entries.
            # Use a savepoint so a failed unlink() only rolls back that one
            # operation, leaving the overall transaction healthy for the rest.
            for acc in deletable:
                try:
                    with self.env.cr.savepoint():
                        acc.unlink()
                except Exception:
                    # Referenced by a tax/journal/property → archive instead
                    try:
                        with self.env.cr.savepoint():
                            acc.write({'active': False})
                    except Exception:
                        pass  # last resort: leave it alone

            # Accounts with journal history must be kept for audit purposes.
            # Archive them so they no longer appear in new-entry dropdowns.
            for acc in deprecatable:
                try:
                    with self.env.cr.savepoint():
                        acc.write({'active': False})
                except Exception:
                    pass

            # ── Step 1b: Remove old account groups for this company ───────
            existing_groups = self.env['account.group'].search(
                [('company_id', '=', self.company_id.id)]
            )
            if existing_groups:
                try:
                    with self.env.cr.savepoint():
                        existing_groups.unlink()
                except Exception:
                    pass

        # ── Step 2: Create account groups ────────────────────────────────
        # Groups are created before accounts so Odoo's _compute_account_group
        # can immediately assign group_id to the new accounts.
        group_ids = self._create_account_groups()

        # ── Step 3: Create new accounts ───────────────────────────────────
        # Re-fetch live codes after deletion
        live_codes = set(
            self.env['account.account'].sudo().search([]).mapped('code')
        )
        taken = set(live_codes)

        Account = self.env['account.account']
        created = []
        for line in to_create.sorted('code'):
            safe_code, _adj = self._unique_code(line.code, taken)
            acc = Account.create({
                'code':         safe_code,
                'name':         line.name,
                'account_type': line.account_type,
                'reconcile':    line.reconcile,
                'company_ids':  [(4, self.company_id.id)],
            })
            created.append(acc.id)

        business_label = dict(self._fields['business_type'].selection).get(
            self.business_type, self.business_type
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Chart of Accounts — %s') % business_label,
            'res_model': 'account.account',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('id', 'in', created)],
            'target': 'current',
            'context': {'create': False},
        }


class GenerateCoaWizardLine(models.TransientModel):
    _name = 'account.coa.wizard.line'
    _description = 'Preview Line for CoA Generator'
    _order = 'code'

    wizard_id     = fields.Many2one('account.coa.generate.wizard', ondelete='cascade')
    template_id   = fields.Many2one('account.coa.template')

    original_code = fields.Char(string='Template Code', readonly=True)
    code          = fields.Char(string='Code (will use)', readonly=True)
    name          = fields.Char(readonly=True)
    name_ar       = fields.Char(readonly=True)
    account_type  = fields.Selection([
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
    ], readonly=True)
    reconcile = fields.Boolean(readonly=True)
    status    = fields.Selection(
        [('new', 'New'), ('adjusted', 'Code auto-adjusted')],
        readonly=True,
    )
    selected = fields.Boolean(string='✓', default=True)
