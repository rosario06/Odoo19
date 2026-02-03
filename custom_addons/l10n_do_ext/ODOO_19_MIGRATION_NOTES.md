# Odoo 19 Migration Notes - l10n_do_ext

## Summary of Changes

This document outlines the changes made to make the `l10n_do_ext` module compatible with Odoo 19.

## Fixed Issues

### 1. Missing Dependency: `l10n_latam_invoice_document`
**Error:** `KeyError: 'Field l10n_latam_document_number referenced in related field definition account.move.ncf does not exist.'`

**Solution:** Added `l10n_latam_invoice_document` to the module dependencies in `__manifest__.py`. This module provides the `l10n_latam_document_number` field that is referenced in `account_move.py`.

### 2. Deprecated Chart of Accounts Templates
**Error:** `ParseError` when parsing chart template XML files

**Solution:** In Odoo 19 (and since Odoo 16), the following models have been deprecated and removed:
- `account.chart.template`
- `account.account.template`
- `account.tax.template`
- `account.fiscal.position.template`

The following data files have been disabled in the manifest:
- `data/l10n_do_chart_template_extended.xml` - Contained deprecated account templates
- `data/l10n_do_taxes.xml` - Contained deprecated tax templates
- `data/l10n_do_taxes_advanced.xml` - Contained deprecated tax templates
- `data/l10n_do_fiscal_positions.xml` - Contained deprecated fiscal position templates

The base file `data/l10n_do_chart_template.xml` has been simplified to only include account groups.

### 3. Document Type Sequence Field Removed
**Error:** `ParseError` - Field `sequence_id` doesn't exist on `l10n_latam.document.type`

**Solution:** In Odoo 19, document type records no longer have a direct `sequence_id` field. Instead:
- NCF sequences are created as `ir.sequence` records
- NCF document types are created as `l10n_latam.document.type` records (without sequence_id)
- Sequences are assigned to document types at the **journal level** in the configuration

**Configuration:** Go to **Accounting > Configuration > Journals** and configure each journal to use the appropriate document type. The sequence will be managed automatically.

### 4. Deprecated `attrs` and `states` Attributes
**Error:** `ParseError` - "A partir de 17.0 ya no se usan los atributos 'attrs' y 'states'"

**Solution:** Starting from Odoo 17+, the `attrs` and `states` attributes were deprecated and replaced with individual attributes (`invisible`, `readonly`, `required`, etc.) that use Python expressions.

**Changes Made in Views:**
- ✅ Converted all `attrs="{'invisible': [...]}"` to `invisible="python_expression"`
- ✅ Converted all `attrs="{'required': [...]}"` to `required="python_expression"`
- ✅ Converted all `attrs="{'readonly': [...]}"` to `readonly="python_expression"`
- ✅ Converted all `attrs="{'column_invisible': [...]}"` to `column_invisible="python_expression"`

**Changes Made in Models:**
- ✅ Removed `states={'draft': [('readonly', False)]}` from field definitions
- ✅ Moved readonly logic to views using `readonly="state != 'draft'"`

**Files Updated:**
- `models/l10n_do_dgii_report.py` - Removed `states` parameter from fields
- `views/res_company_views.xml`
- `views/res_partner_views.xml`
- `views/account_move_views.xml`
- `views/res_config_settings_views.xml`
- `views/l10n_do_dgii_report_views.xml`
- `wizard/l10n_do_dgii_report_wizard_views.xml`
- `wizard/l10n_do_config_wizard_views.xml`

**Example Conversion:**
```xml
<!-- OLD (Odoo ≤16) - View -->
<field name="field_name" attrs="{'invisible': [('country_id', '!=', %(base.do)d)]}"/>

<!-- NEW (Odoo 19) - View -->
<field name="field_name" invisible="country_id.code != 'DO'"/>
```

```python
# OLD (Odoo ≤16) - Model
name = fields.Char(readonly=True, states={'draft': [('readonly', False)]})

# NEW (Odoo 19) - Model + View
# Model:
name = fields.Char(readonly=False)

# View:
<field name="name" readonly="state != 'draft'"/>
```

## What Works Now

✅ **Module Dependencies:** All required dependencies are properly declared  
✅ **NCF Sequences:** All 10 NCF sequences are created (configured at journal level)  
✅ **NCF Document Types:** All 10 document types (01, 02, 03, 04, 07, 11, 12, 13, 14, 15)  
✅ **Account Groups:** Chart of account groups are properly defined  
✅ **Models:** All Python models (account_move, res_partner, res_company, etc.) are compatible  
✅ **Views:** All XML views are compatible  
✅ **Wizards:** Configuration and report wizards work properly  
✅ **DGII Reports:** All DGII report functionality is operational  
✅ **e-CF Functionality:** Electronic invoicing base features work

## What Needs to Be Done

### Option 1: Use Base Module Features (Recommended)
The official `l10n_do` module already provides:
- Basic chart of accounts for Dominican Republic
- Basic tax configuration
- NCF support through l10n_latam_invoice_document

You can:
1. Install the module as-is
2. Create additional accounts manually through: **Accounting > Configuration > Chart of Accounts**
3. Create additional taxes manually through: **Accounting > Configuration > Taxes**
4. Create fiscal positions through: **Accounting > Configuration > Fiscal Positions**

### Option 2: Convert Templates to Direct Records
If you want to automate the creation of accounts and taxes during module installation, you need to:

1. **For Accounts:** Replace `account.account.template` with `account.account` records
2. **For Taxes:** Replace `account.tax.template` with `account.tax` records
3. **For Fiscal Positions:** Replace `account.fiscal.position.template` with `account.fiscal.position` records

**Note:** Direct records are tied to a specific company, while templates were meant to be instantiated per company. Consider this when designing your data files.

### Option 3: Create a Configuration Wizard
Create a wizard that allows users to:
- Select which accounts to create
- Configure tax rates
- Set up fiscal positions
- This provides more flexibility than hardcoded data files

## Module Installation

To install/upgrade the module:

```bash
# Via command line
odoo-bin -u l10n_do_ext -d your_database

# Or via Odoo UI
# Apps > l10n_do_ext > Upgrade
```

## Testing Checklist

After installation, verify:
- ✅ Module installs without errors
- ✅ NCF document types are created (10 types)
- ✅ NCF sequences are created (can be viewed in Settings > Technical > Sequences)
- ✅ Configure journals to use NCF document types
- ✅ Invoice creation generates NCF numbers correctly
- ✅ Account groups appear in Chart of Accounts
- ✅ Related field `ncf` works on invoices
- ✅ DGII reports generate correctly

### How to Configure NCF on Journals

1. Go to **Accounting > Configuration > Journals**
2. Select a sales journal (e.g., "Customer Invoices")
3. In the **Advanced Settings** tab:
   - Enable "Use Documents" 
   - Select the appropriate "Document Type" (e.g., "01 - Factura de Crédito Fiscal")
   - The system will use the corresponding sequence automatically
4. Repeat for other journals as needed

## Dependencies

Required Odoo modules:
- `account` (base accounting)
- `account_edi` (electronic invoicing)
- `l10n_latam_base` (Latin America base)
- `l10n_latam_invoice_document` (provides document numbering)
- `l10n_do` (Dominican Republic base localization)

External Python dependencies:
- `qrcode` (for e-CF QR code generation)

## Additional Resources

- [Odoo 16 Migration Guide](https://www.odoo.com/documentation/16.0/developer/howtos/upgrade.html)
- [Chart of Accounts Changes in Odoo 16+](https://www.odoo.com/forum/help-1)
- DGII Official Documentation: https://dgii.gov.do

## Contact

Module Author: Juan Rosario / Consultorio developers
Website: https://www.linkedin.com/in/jrosariom/

---
**Last Updated:** October 19, 2025
**Odoo Version:** 19.0
**Module Version:** 19.0.1.0.0

