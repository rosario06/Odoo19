# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """

    _name = "hr.contract"
    _description = "Employee Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Contract Reference', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Position')
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date')
    wage = fields.Monetary(string='Wage', required=True, help="Basic Salary of the employee")
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                    default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    company_id = fields.Many2one('res.company', string='Company', 
                                   default=lambda self: self.env.company)

    struct_id = fields.Many2one("hr.payroll.structure", string="Salary Structure")
    schedule_pay = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("semi-annually", "Semi-annually"),
            ("annually", "Annually"),
            ("weekly", "Weekly"),
            ("bi-weekly", "Bi-weekly"),
            ("bi-monthly", "Bi-monthly"),
        ],
        string="Scheduled Pay",
        index=True,
        default="monthly",
        help="Defines the frequency of the wage payment.",
    )
    resource_calendar_id = fields.Many2one(
        'resource.calendar', string='Working Schedule',
        required=True, help="Employee's working schedule."
    )

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by
                 hierachy (parent=False first, then first level children and
                 so on) and without duplicates
        """
        # TODO: remove, too simple and not used
        return self.struct_id.get_structure_with_parents()
