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

#Add Job to Stock move using for Moving Expense
class StockMove(osv.osv):
    _inherit = 'stock.move'
    _name="stock.move"

    def _check_job_stock(self, cr, uid, ids, context):
        for sm in self.browse(cr, uid, ids):
            if sm.from_analytic_id and sm.location_id:
                job_source_ids = [job.id for job in sm.location_id.job_related_ids]
                if sm.from_analytic_id.id not in job_source_ids:
                    return False
            if sm.to_analytic_id and sm.location_dest_id:
                job_dest_ids = [job.id for job in sm.location_dest_id.job_related_ids]
                if sm.to_analytic_id.id not in job_dest_ids:
                    return False
        return True

    _columns ={
                'from_analytic_id':fields.many2one('account.analytic.account',"From Job", readonly=True, ondelete="restrict",states={'draft': [('readonly', False)]}),
                'to_analytic_id':fields.many2one('account.analytic.account',"To Job", readonly=True, ondelete="restrict",states={'draft': [('readonly', False)]}),
                'expense_state':fields.selection((('internal','Internal'),('public','Public')),'Expense Status', readonly= 1, help='Internal: Expense not yet moved expense, Public: Expenes will move to job'),
                'budget_id':fields.related('product_id','budget_id', string='Budget', type='many2one',relation='account.budget.post')
                }
    _constraints = [(_check_job_stock, "KDERP Warning, Please Warehouse and Job, job and warehouse must be related", ['from_analytic_id','to_analytic_id','location_id','location_dest_id'])]