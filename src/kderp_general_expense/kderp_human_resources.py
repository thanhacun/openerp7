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

class hr_department(osv.osv):
    _name = "hr.department"
    _inherit = "hr.department"
    
    def _get_parent_hr(self, cr, uid, hr_ids, context=None):
        res = []
        for hr_obj in self.browse(cr, uid, hr_ids):
            res.append(hr_obj.id)
            child_ids_list =[]
            for child_obj in hr_obj.child_ids:
                child_ids_list.append(child_obj.id)
            if child_ids_list:
                child_ids = self._get_parent_hr(cr, uid, child_ids_list)
                for child_id in child_ids:
                    res.append(child_id)
        return res

    def _get_expense_ids(self, cr, uid, ids, name, arg, context={}):
        if not context:
            context = {}
        res = {}
        koet_obj = self.pool.get('kderp.other.expense.line')
        for id in ids:
            section_ids = tuple(set(self._get_parent_hr(cr, uid, [id], context)))
            res[id] = koet_obj.search(cr, uid, [('section_id','in', section_ids)]) 
            
        return res
        
            
    _columns={
              'general_incharge':fields.boolean('G.E. In Charges'),
              #'expense_ids':fields.one2many('kderp.other.expense.line','section_id','Expenses'),
              'expense_ids':fields.function(_get_expense_ids, type='one2many', relation='kderp.other.expense.line',
                                            string='Expenses'),
              
              }
hr_department()