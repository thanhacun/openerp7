# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2013 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
import time

class MovingExpense(osv.osv):
    """
        Allocate expense In/Out for a Job when moving material between stock
    """
    _name = 'kderp.moving.expense'

    def _get_newcode_moving(self, cr, uid, context):
        date = time.strftime("%Y-%m-%d")
        cr.execute("""SELECT
                        wnewcode.pattern ||
                        btrim(to_char(max(substring(wnewcode.code::text, length(wnewcode.pattern) + 1,padding )::integer) + 1,lpad('0',padding,'0'))) AS newcode
                    from
                        (
                        SELECT
                        isq.name,
                        isq.code as seq_code,
                        isq.prefix || to_char(DATE '%s', suffix || lpad('_',padding,'_')) AS to_char,
                        CASE WHEN cnewcode.code IS NULL
                        THEN isq.prefix::text || to_char(DATE '%s', suffix || lpad('0',padding,'0'))
                        ELSE cnewcode.code
                        END AS code,
                        isq.prefix::text || to_char(DATE '%s', suffix) AS pattern,
                        padding,
                        prefix
                        FROM
                            ir_sequence isq
                        LEFT JOIN
                        (SELECT
                            code
                        FROM
                            kderp_moving_expense
                        WHERE
                            length(code::text)=
                            ((SELECT
                            length(prefix || suffix) + padding AS length
                            FROM
                              ir_sequence
                            WHERE
                            ir_sequence.code::text = 'kderp.moving.expense.code'::text LIMIT 1))
                        ) cnewcode ON cnewcode.code::text ~~ (isq.prefix || to_char(DATE '%s',  suffix || lpad('_',padding,'_')))
                        WHERE isq.code::text = 'kderp.moving.expense.code'::text AND isq.active) wnewcode
                    GROUP BY
                        pattern,
                        name,
                        seq_code,
                        prefix,
                        padding;""" % (date, date, date, date))
        res = cr.fetchone()
        return res[0] if res else False

    def _check_job_budget(self, cr, uid, ids, context=None):
        job_budget_list = {}
        for kme in self.browse(cr, uid, ids):
            from_job_id = kme.from_job_id.id if kme.from_job_id else False
            to_job_id = kme.to_job_id.id if kme.to_job_id else False
            for kmel in kme.detail_ids:
                budget_id = kmel.budget_id.id
                if from_job_id:
                    job_budget_list[(from_job_id,budget_id)] = True
                if to_job_id:
                    job_budget_list[(to_job_id, budget_id)] = True
        if not job_budget_list:
            return True
        job_budget_list_find =",".join(map(str,job_budget_list.keys()))
        cr.execute("""Select id from kderp_budget_data where (account_analytic_id,budget_id) in (%s)""" % job_budget_list_find)
        if cr.rowcount >= len(job_budget_list.keys()):
            return True
        else:
            return False

    MOVING_STATE = (('draft', 'Draft'),
                    ('waiting', 'Waiting for Approval'),
                    ('done', 'Done'),
                    ('cancel', 'Cancelled'),
                    ('revising','Revising'))
    _columns = {
        'code':fields.char("No.", size = 9, required = 1, states = {'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'name':fields.char("Desc.", size = 64, required = 1, states = {'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'notes':fields.char("Notes", size = 128),
        'date':fields.date("Date", required = 1, states = {'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'from_job_id':fields.many2one('account.analytic.account', 'From (↓)', ondelete='restrict', states = {'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'to_job_id': fields.many2one('account.analytic.account', 'To (↑)', ondelete='restrict', states = {'done':[('readonly', True)], 'cancel':[('readonly', True)]}),

        'detail_ids': fields.one2many('kderp.moving.expense.line','moving_expense_id', 'Details', states = {'done':[('readonly', True)], 'cancel':[('readonly', True)]}),

        'state':fields.selection(MOVING_STATE, 'Status', readonly = 1, required=True, select = True)
    }
    _sql_constraints = [
                        ('moving_expense_unique_no', 'unique(code)', 'Moving Expense Number must be unique !'),
                        ('job_must_beinput', 'check((coalesce(from_job_id,0)+coalesce(to_job_id,0))>0)','Please check Job!\nFrom Job or To Job must be input'),
                        ('job_must_input_different', 'check(from_job_id<>to_job_id)','Please check Job!\n From and To job must be different'),
                        ]

    _constraints = [(_check_job_budget, 'Please check you Job and Budget you have just modify (No Budget Job) !',
                     ['from_job_id', 'to_job_id', 'detail_ids'])]

    _defaults = {
        'state': 'draft',
        'date': time.strftime("%Y-%m-%d"),
        'code':_get_newcode_moving
    }

    def write(self, cr, uid, ids, vals, context=None):
        new_obj = super(MovingExpense, self).write(cr, uid, ids, vals, context=context)

        if 'state' in vals or 'from_job_id' in vals or 'to_job_id' in vals or 'detail_ids' in vals or 'date' in vals:
            expense_budget_line_obj = self.pool.get('kderp.expense.budget.line')
            kve_link_dicts = expense_budget_line_obj.create_update_expense_budget_line(cr, uid, ids, 'kderp.moving.expense',
                                                                                      'moving_expense_id')
        self.pool.get('ir.rule').clear_cache(cr, uid)
        return new_obj

    def action_submit(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'waiting'})

    def action_cancel(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'cancel'})

    def action_revise(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'draft'})

    def action_approved(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'done'})

    def action_open(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'revising'})

    def action_close(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'revising'})


class MovingExpenseLine(osv.osv):
    """
        Moving Expense detail
    """
    _name = 'kderp.moving.expense.line'

    _columns = {
        'moving_expense_id': fields.many2one('kderp.moving.expense','Moving Expense', required = 1, ondelete='restrict'),
        'budget_id': fields.many2one('account.budget.post','Budget', required = 1, ondelete='restrict'),
        'amount': fields.float("Amount", required=True, digits_compute=dp.get_precision('Amount')),
        'move_ids':fields.many2many('stock.move', "move_line_stock_move_rel", "moving_expense_line_id", "move_id", "Detail Stock Moves")
    }
    _sql_constraints = [
        ('moving_expense_budget_unique_no', 'unique(moving_expense_id, budget_id)', 'Moving Expense Number & Budget must be unique !')]

    def _check_job_budget(self, cr, uid, ids, context=None):
        job_budget_list = {}
        for kmel in self.browse(cr, uid, ids):
            budget_id = kmel.budget_id.id
            if kmel.moving_expense_id.from_job_id:
                job_id = kmel.moving_expense_id.from_job_id.id
                job_budget_list[(job_id,budget_id)] = True
            if kmel.moving_expense_id.to_job_id:
                job_id = kmel.moving_expense_id.to_job_id.id
                job_budget_list[(job_id, budget_id)] = True

        if not job_budget_list:
            return True

        job_budget_list=",".join(map(str,job_budget_list.keys()))
        cr.execute("""Select id from kderp_budget_data where (account_analytic_id,budget_id) in (%s)""" % job_budget_list)
        if cr.rowcount:
            return True
        else:
            return False
    _constraints = [(_check_job_budget, 'Please check you Job and Budget you have just modify (No Budget Job) !',
                     ['moving_expense_id', 'budget_id'])]