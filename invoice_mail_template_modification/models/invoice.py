# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

import base64
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_and_print(self):
        """Timesheet report added in invoice email"""
        res = super(AccountMove, self).action_send_and_print()
        template_id = self.env['mail.template'].search([('id', '=', res.get('context').get('default_mail_template_id'))])
        template_id.sudo().attachment_ids = [(5, 0, 0)]
        if self.timesheet_ids:
            report = self.env['ir.actions.report']._render_qweb_pdf('hr_timesheet.timesheet_report', res_ids=self.timesheet_ids.ids)
            timesheet_report = base64.b64encode(report[0])
            timesheet_values = {'name': 'Timesheets of ' + self.name, 'type': 'binary', 'datas': timesheet_report,
                                'store_fname': timesheet_report, 'mimetype': 'application/pdf'}
            timesheet_report_id = self.env['ir.attachment'].sudo().create(timesheet_values)
            template_id.sudo().attachment_ids = [(6, 0, [timesheet_report_id.id])]
        return res
