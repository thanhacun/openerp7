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
from datetime import date

class kderp_ge_wizard_form(osv.osv_memory):
    _name = 'kderp.ge.wizard.form'
    _description = 'GE Wizard Print GE Statement'      
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ge = self.browse(cr, uid, ids[0])  
        datas = {'ids': context.get('active_ids',[]),
                 'parameters':{
                               'pdate_start':ge.pdate_start,
                               'pdate_end':ge.pdate_end
                               }
                 }
        
        datas['model'] = 'kderp.other.expense'
        datas['title'] = 'GE Statement Form'
        
        report_name= "kderp.report.ge.statement.%s" % ge.file_type
          
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            }
     
    _columns = {                
                'pdate_start':fields.date('Start Date'),
                'pdate_end':fields.date('End Date'),
                'file_type':fields.selection([('xls','Excel File'),('pdf','PDF File')],'File Type', required=1),
                }
    _defaults={
               "pdate_start": date.today().strftime("%Y-01-01"),
               'pdate_end':date.today().strftime("%Y-12-31"),
               'file_type':'xls'
               }
kderp_ge_wizard_form()