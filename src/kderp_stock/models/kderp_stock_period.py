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

# 1 : imports of python lib
# 2 :  imports of openerp
import openerp
from openerp.osv import fields, osv as models, osv, expression
from openerp.tools.translate import _

class StockPeriodYear(models.Model):
    """
        Stock Year
    """
    _name = 'kderp.stock.period.year'
    SY_STATE = [('open','Open'),
                ('closed','Closed')]
    # Fields declaration
    _columns = {
                'name':fields.char("Stock Year", size=16, required = True, states = {'open':[('readonly', False)]}, readonly = 1),
                'from_date':fields.date("From", required = True, states = {'open':[('readonly', False)]}, readonly = 1),
                'to_date':fields.date("To", required = True, states = {'open':[('readonly', False)]}, readonly = 1),
                'state':fields.selection(SY_STATE, 'State', required = True, readonly = 1),
                'stock_period_ids':fields.one2many('kderp.stock.period','stock_year_id','Stock Periods', states = {'open':[('readonly', False)]}, readonly = 1)
                }
    _defaults = {
                 'state':'open'
                 }
    
    _order = "from_date, id"

    def _check_duration(self, cr, uid, ids, context=None):
        obj_fy = self.browse(cr, uid, ids[0], context=context)
        if obj_fy.to_date < obj_fy.from_date:
            return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe start date of a Stock Period Year must precede its end date.', ['from_date','to_date'])
    ]

    def create_period3(self, cr, uid, ids, context=None):
        return self.create_period(cr, uid, ids, context, 3)
    
    def create_period6(self, cr, uid, ids, context=None):
        return self.create_period(cr, uid, ids, context, 6)

    def create_period(self, cr, uid, ids, context=None, interval=12):
        period_obj = self.pool.get('kderp.stock.period')
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        for spy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(spy.from_date, '%Y-%m-%d')
            period_obj.create(cr, uid, {
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'start_date': ds,
                    'stop_date': ds,
                    'opening_closing': True,
                    'stock_year_id': spy.id,
                })
            while ds.strftime('%Y-%m-%d') < spy.to_date:
                de = ds + relativedelta(months=interval, days=-1)

                if de.strftime('%Y-%m-%d') > spy.to_date:
                    de = datetime.strptime(spy.to_date, '%Y-%m-%d')

                period_obj.create(cr, uid, {
                    'name': ds.strftime('%m/%Y'),
                    'start_date': ds.strftime('%Y-%m-%d'),
                    'stop_date': de.strftime('%Y-%m-%d'),
                    'stock_year_id': spy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    def find(self, cr, uid, dt=None, exception=True, context=None):
        res = self.finds(cr, uid, dt, exception, context=context)
        return res and res[0] or False

    def finds(self, cr, uid, dt=None, exception=True, context=None):
        if context is None: context = {}
        if not dt:
            dt = fields.date.context_today(self,cr,uid,context=context)
        args = [('from_date', '<=' ,dt), ('to_date', '>=', dt)]        
        ids = self.search(cr, uid, args, context=context)
        
        if not ids:
            if exception:
                raise osv.except_osv(_('Error!'), _('There is no fiscal year defined for this date.\nPlease create one from the configuration of the accounting menu.'))
            else:
                return []
        return ids

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if args is None:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('name', operator, name)]
        else:
            domain = [('name', operator, name)]
        ids = self.search(cr, user, expression.AND([domain, args]), limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)    
    
class StockPeriod(models.Model):
    """
        Stock Period. Using closing quantity for a Warehouse
    """
    _name = 'kderp.stock.period'
    
    SP_STATE = [('open','Open'),
                ('closed','Closed')]
    
    # Fields declaration
    _columns = {
                'name':fields.char("Period Name", size=16, required = True, states = {'open':[('readonly', False)]}, readonly = 1),
                'start_date':fields.date("Start of Period", required = True, states = {'open':[('readonly', False)]}, readonly = 1),
                'stop_date':fields.date("End of Period", required = True, states = {'open':[('readonly', False)]}, readonly = 1),
                'opening_closing':fields.boolean("Opening/Closing", states = {'open':[('readonly', False)]}, readonly = 1),
                
                'state':fields.selection(SP_STATE, 'State', required = True, readonly = 1),
                'stock_year_id':fields.many2one('kderp.stock.period.year','Stock year', states = {'open':[('readonly', False)]}, readonly = 1),
                }
    _defaults = {
                 'state':'open'
                 }
    
    _order = "start_date, opening_closing desc"    

    def _check_duration(self,cr,uid,ids,context=None):
        obj_period = self.browse(cr, uid, ids[0], context=context)
        if obj_period.stop_date < obj_period.start_date:
            return False
        return True

    def _check_year_limit(self,cr,uid,ids,context=None):
        for obj_period in self.browse(cr, uid, ids, context=context):
            if obj_period.opening_closing:
                continue

            if obj_period.stock_year_id.to_date < obj_period.stop_date or \
               obj_period.stock_year_id.to_date < obj_period.start_date or \
               obj_period.stock_year_id.from_date > obj_period.start_date or \
               obj_period.stock_year_id.from_date > obj_period.stop_date:
                return False

            pids = self.search(cr, uid, [('stop_date','>=',obj_period.start_date),('start_date','<=',obj_period.stop_date),('opening_closing','=',False),('id','<>',obj_period.id)])
            if pids:                
                return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe duration of the Period(s) is/are invalid.', ['date_stop','start_date']),
        (_check_year_limit, 'Error!\nThe period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the stock fiscal year.', ['date_stop','start_date'])
    ]

    def next(self, cr, uid, period, step, context=None):
        ids = self.search(cr, uid, [('start_date','>',period.start_date)])
        if len(ids)>=step:
            return ids[step-1]
        return False

    def find(self, cr, uid, dt=None, context=None):
        if context is None: context = {}
        if not dt:
            dt = fields.date.context_today(self, cr, uid, context=context)
        args = [('start_date', '<=' ,dt), ('stop_date', '>=', dt)]
        
        result = []
        #WARNING: in next version the default value for account_periof_prefer_normal will be True
        if context.get('stock_period_prefer_normal'):
            # look for non-special periods first, and fallback to all if no result is found
            result = self.search(cr, uid, args + [('opening_closing', '=', False)], context=context)
        if not result:
            result = self.search(cr, uid, args, context=context)
        if not result:
            raise osv.except_osv(_('Error!'), _('There is no stock period defined for this date: %s.\nPlease create one.')%dt)
        return result

    def action_draft(self, cr, uid, ids, *args):
        mode = 'draft'
        for period in self.browse(cr, uid, ids):
            if period.stock_year_id.state == 'done':
                raise osv.except_osv(_('Warning!'), _('You can not re-open a period which belongs to closed stock fiscal year'))
        #cr.execute('update account_journal_period set state=%s where period_id in %s', (mode, tuple(ids),))
        cr.execute('update stock_period set state=%s where id in %s', (mode, tuple(ids),))
        return True

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        
        domain = [('name', operator, name)]        
        ids = self.search(cr, user, expression.AND([domain, args]), limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)

    def build_ctx_periods(self, cr, uid, period_from_id, period_to_id):
        if period_from_id == period_to_id:
            return [period_from_id]
        period_from = self.browse(cr, uid, period_from_id)
        period_date_start = period_from.start_date
        
        period_to = self.browse(cr, uid, period_to_id)
        period_date_stop = period_to.stop_date

        if period_date_start > period_date_stop:
            raise osv.except_osv(_('Error!'), _('Start period should precede then end period.'))

        # /!\ We do not include a criterion on the company_id field below, to allow producing consolidated reports
        # on multiple companies. It will only work when start/end periods are selected and no fiscal year is chosen.

        #for period from = january, we want to exclude the opening period (but it has same date_from, so we have to check if period_from is special or not to include that clause or not in the search).
        if period_from.opening_closing:
            return self.search(cr, uid, [('start_date', '>=', period_date_start), ('stop_date', '<=', period_date_stop)])
        return self.search(cr, uid, [('start_date', '>=', period_date_start), ('stop_date', '<=', period_date_stop), ('opening_closing', '=', False)])