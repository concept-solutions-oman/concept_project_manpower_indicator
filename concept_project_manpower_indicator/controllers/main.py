from odoo import http, _
from odoo.http import request
from datetime import datetime

class ProjectManpowerController(http.Controller):

    @http.route('/project_manpower/get_status', type='json', auth='user')
    def get_status(self, **kw):
        employee = request.env.user.employee_id
        is_started = False

        if employee:
            log = request.env['manpower.log'].search([
                ('employee_id', '=', employee.id),
                ('status', '=', 'on_duty'),
                ('end_time', '=', False)
            ], order='start_time desc', limit=1)
            is_started = bool(log)
                
        return {'is_started': is_started}

    @http.route('/project_manpower/start_work', type='json', auth='user')
    def start_work(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return {'status': 'error', 'message': _('Your user account is not linked to an employee.')}

        existing_log = request.env['manpower.log'].search([
            ('employee_id', '=', employee.id),
            ('end_time', '=', False),
            ('status', '=', 'on_duty')
        ], limit=1)
        
        if existing_log:
             return {'status': 'error', 'message': _('You are already On Duty.')}

        log = request.env['manpower.log'].create({
            'employee_id': employee.id,
            'start_time': datetime.now(),
            'status': 'on_duty',
        })

        # --- On-Duty Notification Commented Out As Requested ---
        # if log:
        #     log.sudo()._post_manager_inbox_notification('on_duty')
        # --- End of Commented Logic ---

        return {'status': 'started'}

    @http.route('/project_manpower/stop_work', type='json', auth='user')
    def stop_work(self, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return {'status': 'error', 'message': _('Your user account is not linked to an employee.')}

        log = request.env['manpower.log'].search([
            ('employee_id', '=', employee.id),
            ('end_time', '=', False),
            ('status', '=', 'on_duty') 
        ], order='start_time desc', limit=1)
        
        if not log:
            log = request.env['manpower.log'].search([
                ('employee_id', '=', employee.id),
                ('end_time', '=', False),
            ], order='start_time desc', limit=1)

            if not log:
                return {'status': 'error', 'message': _('No active On Duty session found to stop.')}

        # This 'write' call will be intercepted by the 'write'
        # method in 'manpower.log.py' to send the 'off_duty' notification.
        log.write({
            'end_time': datetime.now(),
            'status': 'off_duty',
        })
        return {'status': 'stopped'}

    @http.route('/project_manpower/get_all_users_status', type='json', auth='user')
    def get_all_users_status(self, **kw):
        # 1. Get all logs that are currently 'On Duty'
        active_logs = request.env['manpower.log'].sudo().search([
            ('status', '=', 'on_duty'),
            ('end_time', '=', False)
        ])
        on_duty_emp_ids = active_logs.mapped('employee_id.id')

        # 2. Get all active employees in the company
        employees = request.env['hr.employee'].sudo().search([('active', '=', True)])
        
        result = []
        for emp in employees:
            result.append({
                'id': emp.id,
                'name': emp.name,
                'department': emp.department_id.name if emp.department_id else 'Employee Profile',
                'is_started': emp.id in on_duty_emp_ids
            })
            
        return result