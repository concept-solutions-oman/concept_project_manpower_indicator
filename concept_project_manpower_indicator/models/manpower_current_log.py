from odoo import models, fields, tools

class ManpowerCurrentStatus(models.Model):
    _name = 'manpower.current.status'
    _description = 'Current Manpower Status (Sales Only)'
    _auto = False
    _check_company_auto = False

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    status = fields.Selection([
        ('on_duty', 'On Duty'),
        ('off_duty', 'Off Duty'),
    ], string='Current Status', readonly=True)
    start_time = fields.Datetime(string='Start Time', readonly=True)
    end_time = fields.Datetime(string='End Time', readonly=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)

    def init(self):
        
        # Safely drop the view if it already exists before recreating it
        tools.drop_view_if_exists(self.env.cr, 'manpower_current_status')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW manpower_current_status AS (
                WITH latest_log AS (
                    SELECT DISTINCT ON (employee_id)
                        id,
                        employee_id,
                        status,
                        start_time,
                        end_time,
                        date
                    FROM manpower_log
                    ORDER BY employee_id, start_time DESC
                )
                SELECT
                    emp.id AS id,
                    emp.id AS employee_id,
                    emp.department_id AS department_id,
                    CASE
                        WHEN l.status = 'on_duty' AND l.end_time IS NULL THEN 'on_duty'
                        ELSE 'off_duty'
                    END AS status,
                    l.start_time,
                    l.end_time,
                    l.date
                FROM hr_employee emp
                LEFT JOIN latest_log l ON emp.id = l.employee_id
                WHERE emp.active = TRUE
            );
        """)
