# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

listofreport = [('accepted.orders','Accepted Orders'),('working.process','Working Process')]
class wizard_kderp_job_contract_area_summary(osv.osv_memory):
    _name = 'wizard.kderp.job.contract.area.summary'
    _description = 'Job Contract Area Summary Wizard'
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        formData = self.browse(cr, uid, ids[0])

        nameofreport = formData.nameofreport

        datas = {'ids': context.get('active_ids',[])}

        titleofreport = 'Summary of %s' % dict(listofreport)[nameofreport]
        # datas['model'] = 'account.analytic.account'
        datas['parameters'] = {'pdateinput': formData.month}
        datas['title'] = titleofreport
        
        report_name= "kderp.report.summary.of.%s.xls" % nameofreport
          
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            'context': context,
            'name': titleofreport,
            'nodestroy': True,
            'target': 'new'
            }

    def _get_month_list(self, cr, uid, context):
        res = []
        cr.execute("""Select
                        Distinct
                        kcc.registration_date - extract(day from kcc.registration_date)::integer + 1,
                        to_char(kcc.registration_date,'Mon-YYYY')
                    from
                        account_analytic_account aaa
                    left join
                        kderp_contract_job_area kjca on aaa.id = job_id
                    left join
                        kderp_contract_client kcc on contract_id = kcc.id
                    where
                        aaa.state not in ('cancel','closed') and kcc.registration_date is not null
                    Order by
                        kcc.registration_date - extract(day from kcc.registration_date)::integer + 1 desc""")
        for dt, my in cr.fetchall():
            res.append((dt, my))
        return res

    _columns = {                
                'month':fields.selection(_get_month_list, 'Month', required=True),
                'nameofreport':fields.selection(listofreport, 'Report', required=True),
                }