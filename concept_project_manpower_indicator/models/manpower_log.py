import logging
from odoo import models, fields, api, _
from markupsafe import Markup


class ManpowerLog(models.Model):
    _name = 'manpower.log'
    _description = 'Manpower Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string='Date', default=fields.Date.context_today)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env.user.employee_id)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True)
    status = fields.Selection([
        ('on_duty', 'On Duty'), 
        ('off_duty', 'Off Duty')
    ], string='Status', tracking=True)
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def write(self, vals):
        """
        Intercept the write operation to send a notification when
        an employee goes 'Off Duty'.
        """
        original_status = {log.id: log.status for log in self}
        res = super().write(vals)
        
        if 'status' in vals and vals['status'] == 'off_duty':
            for log in self:
                # Check if status actually changed to 'off_duty'
                if original_status.get(log.id) != 'off_duty' and log.employee_id:
                    log.sudo()._post_manager_inbox_notification('off_duty')
        return res

    def _post_manager_inbox_notification(self, new_status):
        """
        Posts a notification to the employee's department manager.
        """
        self.ensure_one()
        
        # Check for department
        if not self.employee_id.department_id:
            return

        # Check for manager
        manager = self.employee_id.department_id.manager_id
        if not manager:
            return
        
        # Check for manager's user and partner
        if not manager.user_id or not manager.user_id.partner_id:
            return

        partner_id = manager.user_id.partner_id.id

        # Build message
        status_text = "On Duty" if new_status == 'on_duty' else "Off Duty"
        status_color = "green" if new_status == 'on_duty' else "red"

        body = f"Dear {manager.name},<br/><br/>" \
               f"This is to inform you that employee <b>{self.employee_id.name}</b> has updated their status to: " \
               f"<span style='color:{status_color}; font-weight:bold;'>{status_text}</span>."

        # Post message to the manager's inbox
        self.message_post(
            body=Markup(body),
            partner_ids=[partner_id],
            message_type='notification',
            subtype_xmlid="mail.mt_comment"
        )
    
        return True