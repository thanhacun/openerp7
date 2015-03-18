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

class kderp_job_wizard_balance_sheet_form(osv.osv_memory):
    _name = 'kderp.job.wizard.balance.sheet.form'
    _description = 'Job Wizard Print Balance Detail'      
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        code_budget = ""
        jwbs = self.browse(cr, uid, ids[0])
        for bg in jwbs.pcodebudget:
            code_budget += "," + bg.code
            
        datas = {'ids': context.get('active_ids',[]),
                 'parameters':{
                               'pCodeBudget': code_budget,
                               }
                 }
        
        datas['model'] = 'account.analytic.account'
        datas['title'] = 'Balance Budget Detail Form'
        
        report_name= "kderp.report.balance.sheet.detail.new.%s" % jwbs.file_type
          
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            }
     
    _columns = {                
                'pcodebudget':fields.many2many('account.budget.post','balance_detail_budgets','budget_id','detail_id','Code Budget'),
                'file_type':fields.selection([('xls','Excel File'),('pdf','PDF File')],'File Type', required=1),
                }
    _defaults={
               'file_type':'pdf'
               }
kderp_job_wizard_balance_sheet_form()