from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp import netsvc

class account_budget_post(osv.osv):
    """
        Inherit Budget add new some field, using for Budget Code
    """
    _name = 'account.budget.post'
    _inherit = 'account.budget.post'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
            
        job_id = context.get('job_id', False) 
        if job_id:
            general_expense = context.get('general_expense', False)          
            budget_ids = []
            cr.execute("""select 
                            budget_id
                        from 
                            kderp_budget_data
                        where 
                            account_analytic_id=%s
                        Union
                        Select 
                            id
                        from
                            account_budget_post abp
                        where
                            general_expense = %s and nofilter""" % (job_id, general_expense))
            for budget_id in cr.fetchall():
                budget_ids.append(budget_id[0])
            args.append((('id', 'in', budget_ids)))
        return super(account_budget_post, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=False)

    _columns = {
                'general_expense':fields.boolean("General Expense?", help = 'Check if budget using for General Expense'),
                'nofilter':fields.boolean("Filter?")
                }
    
    _defaults = {
                'general_expense': lambda self, cr, uid, context={}:context.get('general_expense',False),
                 }

class account_analytic_account(osv.osv):
    """
        Inherit Job (Account Analytic Account) add new some field, using for General Expense
    """
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    
    _columns = {
                'general_expense':fields.boolean("General Expense?")
                }
    
    _defaults = {
                 'general_expense': lambda self, cr, uid, context={}:context.get('general_expense',False),
                 'code': lambda self, cr, uid, context={}:self.pool.get('ir.sequence').get(cr, uid, 'kderp.general.expense.code')[:-1] if context.get('general_expense',False) else ""
                 }
    
    #Fuction get ID de mo Yearly G.E hay Jpb tu GE vaf GE payment
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context:
            context = {} 
        job_id = context.get('job_id',False) 
        if job_id:
            aaa_obj = self.pool.get('account.analytic.account')
            ge_type = aaa_obj.read(cr, uid,job_id, ['general_expense'])['general_expense'] 
            if ge_type and not view_id:
                views_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','view.account.analytic.kderp.yearlybudget.%s' % view_type)])
                if views_ids:
                    view_id = views_ids[0]   
        else:
#             #raise osv.except_osv("No",context)
            if context.get('general_expense', False) and not view_id:
                views_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','view.account.analytic.kderp.yearlybudget.%s' % view_type)])
                if views_ids:
                    view_id = views_ids[0]                
        return super(account_analytic_account, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
    
class kderp_other_expense(osv.osv):
    """
    Customize Other Expense suitable with general expense
    """
    _name = 'kderp.other.expense'
    _inherit = 'kderp.other.expense'

    EXPENSE_TYPE_SELECTION =(
                    ('expense', 'Expense'),                    
                    ('prepaid', 'Prepaid'),
                    ('fixed_asset', 'Fixed Asset (With Depreciation)'),
                    ('monthly_expense','---Allocated Expense---'),)

    ALLOCATE_SELECTION =(
                    ('PE','Job Expense'),
                    ('GE','General Expense'),
                    ('PGE','Job & General Expense'))

    def check_and_submit_monthly_expense(self, cr, uid, ids, cron_mode=True, context=None):
        if not context:
            context = {}
        if not ids:
            ids = self.search(cr, uid, [('expense_type','=','monthly_expense'),('state','=','draft'),('date','<=', time.strftime('%Y-%m-%d'))])
            self.action_draft_to_waiting_for_payment(cr, uid, ids, context = context)
        return True
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context:
            context = {}
        if context.get('general_expense', False) and not view_id:
            views_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','view.kderp.other.expense.ge.%s' % view_type)])
            if views_ids:
                view_id = views_ids[0]             
        return super(kderp_other_expense, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
    
    def _get_allocated_selection(self, cr, uid, context):
        if not context:
            context = {}
            
        if context.get('general_expense', False):
            return filter(lambda x: x[0] <> 'PE', self.ALLOCATE_SELECTION)
        else:
            return filter(lambda x: x[0] <>'GE', self.ALLOCATE_SELECTION)
        
    def _get_expense_type_selection(self, cr, uid, context):
        if not context:
            context = {}   
        if context.get('general_expense', False):
            return filter(lambda x: x[0] <> '', self.EXPENSE_TYPE_SELECTION)
        else:
            return filter(lambda x: (x[0] <> 'prepaid' and x[0] <> 'fixed_asset'), self.EXPENSE_TYPE_SELECTION) 
            
    #Get defaults values
    def _get_job(self, cr, uid, context={}):
        if not context:
            context={}
        if context.get('account_analytic_id', False):
            res = context.get('account_analytic_id',False)
        elif context.get('general_expense',False):
            strcurrent_time =  time.strftime('%Y-%m-%d')
            job_ids = self.pool.get('account.analytic.account').search(cr, uid, [('date_start','<=',strcurrent_time),('date','>=',strcurrent_time),('general_expense','=',True)])
            res = job_ids[-1] if job_ids else False
        else:
            res = False
        return res
    
    def _get_section_incharge(self, cr, uid, context={}):
        if not context:
            context={}
        if context.get('general_expense',False):
            user = self.pool.get('res.users').browse(cr, uid, uid)            
            if user.employee_id.department_id.general_incharge:
                return user.employee_id.department_id.id
        return False

    #Fields Functions        
    def _get_related(self, cr, uid, ids, field_name, arg, context={}):
        koel_obj = self.pool.get('kderp.other.expense.line')
        res = {}
        for id in ids:
            koel_ids = koel_obj.search(cr, uid, [('belong_expense_id','=',id),('expense_id.state','!=','cancel')])
            related_ids = set(koel_ids)
            res[id] = list(related_ids)
        return res
    
    def _get_sections(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for exp in self.browse(cr, uid, ids):
            sections = []
            for line in exp.expense_line:
                if line.section_id:
                    sections.append(str(line.section_id.name))
                    sections = list(set(sections))
            res[exp.id]=", ".join(sections)
        return res
    
    def _get_state(self, cr, uid, ids, name, arg, context = {}):
        if not context:
            context = {}
        res = {}
        for koe in self.browse(cr, uid, ids, context):
            res[koe.id] = {'state_depend':koe.state,
                           'state_recognize':koe.state}
        return res
    
    def _get_expense_from_detail(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('kderp.other.expense.line').browse(cr, uid, ids, context=context):
            result[line.expense_id.id] = True
        return result.keys()
    
    #Get remaining
    def _get_remaining_amount(self, cr, uid, ids, name, args, context = {}):
        if not context:
            context = {}
        res = {}
        for koe in self.browse(cr, uid, ids, context = {}):
            recognized_amount = 0
            allocated_date = False
            allocating_date = False
            allocating_begin_date = False
            if koe.expense_type in ('prepaid', 'fixed_asset'):
                for re_exp in koe.related_expense_ids:
                    if not allocating_begin_date:
                        allocating_begin_date = re_exp.expense_id.date
                    else:
                        if allocating_begin_date > re_exp.expense_id.date:
                            allocating_begin_date = re_exp.expense_id.date
                            
                    if not allocating_date:
                            allocating_date = re_exp.expense_id.date                            
                    else:
                            if allocating_date < re_exp.expense_id.date:
                                allocating_date = re_exp.expense_id.date                    
                    
                    if re_exp.expense_id.state not in ('draft', 'cancel'):
                        recognized_amount += re_exp.amount
                        if not allocated_date:                    
                            allocated_date = re_exp.expense_id.date
                        else:
                            if allocated_date < re_exp.expense_id.date:
                                allocated_date = re_exp.expense_id.date                                                    
                                                                                                                                     
            res[koe.id] = {'recognized_amount': recognized_amount,
                           'remaining_amount': koe.amount_untaxed - recognized_amount,
                           'current_allocated_date': allocated_date,
                           'allocating_begin_date': allocating_begin_date,
                           'allocating_date': allocating_date
                           }
        return res
    
    def _get_expense_remaining(self, cr, uid, ids, context = {}):
        if not context:
            context = {}
        res = {}
        for koe in self.browse(cr, uid, ids, context = {}):
            res[koe.id] = True
            for koel in koe.expense_line:
                if koel.belong_expense_id:
                    res[koel.belong_expense_id.id] = True
        return res.keys()
        
    def _get_expense_from_expl(self, cr, uid, ids, context = {}):
        if not context:
            context = {}
        res = {}
        koel_obj = self.pool.get('kderp.other.expense.line')
        for koel in koel_obj.browse(cr, uid, ids, context = {}):
            if koel.expense_id:
                res[koel.expense_id.id] = True
            if koel.belong_expense_id:
                res[koel.belong_expense_id.id] = True
        return res.keys()
    
    def action_open_allocated_expense(self, cr, uid, ids, *args):
        interface_string = 'Allocated Expense'
        if ids:
            expense_ids = []
            cr.execute("""select
                           distinct( koel.expense_id)
                        from 
                            kderp_other_expense_line koel 
                        where koel.belong_expense_id = (%s)""" % ids[0])
            for expense_id  in cr.fetchall():
                expense_ids.append(expense_id[0])
            return {
                    'type': 'ir.actions.act_window',
                    'name': interface_string,
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'context': {},
                    'res_model': 'kderp.other.expense',
                    'domain': "[('id','in',%s)]" % expense_ids
                    }
        else:
            return True
        
    STATE_SELECTION=[('draft','Draft'),
                   ('waiting_for_payment','Waiting for Payment'),
                   ('paid','Paid'),
                   ('done','Completed'),
                   ('revising','Expense Revising'),
                   ('cancel','Expense Canceled')]
    
    _columns = {
                #'allocated_date':fields.date('Allocated Date', states={'paid':[('readonly', True)], 'done':[('readonly',True)], 'cancel':[('readonly',True)]}),
                'expense_type':fields.selection(_get_expense_type_selection, 'Exp. Type', required = True, states={'paid':[('readonly', True)], 'done':[('readonly',True)], 'cancel':[('readonly',True)]},
                                                help="""Expense: Allocated direct to Job/General have payment\nRecognize Expense: Recognize allocated to Job/General from Fixed Asset, Prepaid without payment\nPrepaid, Fixed Asset for management and don't allocated"""),
                'allocated_to':fields.selection(_get_allocated_selection, 'Allocate To', required = True, states={'paid':[('readonly', True)], 'done':[('readonly',True)], 'cancel':[('readonly',True)]}, select = 1),
                
                'link_asset_id':fields.many2one('kderp.asset.management', 'Asset', states={'done':[('readonly', True)], 'paid':[('readonly', True)]}),                
                
                'section_incharge_id':fields.many2one('hr.department','Section In Charges', domain=[('general_incharge','=',True)],  select = 1, states={'paid':[('readonly', True)], 'done':[('readonly',True)], 'cancel':[('readonly',True)]}),#General Affair or General Coordination Section
                'related_expense_ids':fields.function(_get_related,string='Related',type='one2many',relation='kderp.other.expense.line', readonly=True),
                
                'sections':fields.function(_get_sections,string='Sections',size=256
                                         ,type='char', method=True,
                                          store={
                                                  'kderp.other.expense.line': (_get_expense_from_detail, ['section_id'], 10)
                                                 }),
                'state':fields.selection(STATE_SELECTION,'Exp. Status',readonly=True,select=1),
                'state_depend':fields.function(_get_state,selection=STATE_SELECTION,type='selection', string='Exp. Status',multi="_get_state"),
                'state_recognize':fields.function(_get_state,selection=STATE_SELECTION,type='selection', string='Exp. Status',multi="_get_state"),
                
                'expense_line_pending':fields.one2many('kderp.other.expense.line','expense_id','Details', states={'paid':[('readonly', True)], 'done':[('readonly',True)], 'cancel':[('readonly',True)]}),
                'expense_line_ge':fields.one2many('kderp.other.expense.line','expense_id','Details', states={'paid':[('readonly', True)], 'done':[('readonly',True)], 'cancel':[('readonly',True)]}),
                
                'recognized_amount':fields.function(_get_remaining_amount,type='float',string='Allocated Amount',method=True,multi='_get_remaining',
                                                    store={
                                                           'kderp.other.expense':(_get_expense_remaining, ['state','expense_type','date','currency_id'], 15),
                                                           'kderp.other.expense.line':(_get_expense_from_expl, ['belong_expense_id','amount','expense_id'], 15),
                                                           }),
                'remaining_amount':fields.function(_get_remaining_amount,type='float',string='Remaining Amount',method=True,multi='_get_remaining',
                                                    store={
                                                           'kderp.other.expense':(_get_expense_remaining, ['state','expense_type','date','currency_id'], 15),
                                                           'kderp.other.expense.line':(_get_expense_from_expl, ['belong_expense_id','amount','expense_id'], 15),
                                                           }),
                'current_allocated_date':fields.function(_get_remaining_amount,type='date',string='Allocated to date',method=True,multi='_get_remaining',
                                                    store={
                                                           'kderp.other.expense':(_get_expense_remaining, ['state','expense_type','date'], 15),
                                                           'kderp.other.expense.line':(_get_expense_from_expl, ['belong_expense_id','amount','expense_id'], 15),
                                                           }),
                'allocating_date':fields.function(_get_remaining_amount,type='date',string='Allocating to date',method=True,multi='_get_remaining',
                                                    store={
                                                           'kderp.other.expense':(_get_expense_remaining, ['state','expense_type','date'], 15),
                                                           'kderp.other.expense.line':(_get_expense_from_expl, ['belong_expense_id','amount','expense_id'], 15),
                                                           }),
                'allocating_begin_date':fields.function(_get_remaining_amount,type='date',string='Allocated Start Date',method=True,multi='_get_remaining',
                                                    store={
                                                           'kderp.other.expense':(_get_expense_remaining, ['state','expense_type','date'], 15),
                                                           'kderp.other.expense.line':(_get_expense_from_expl, ['belong_expense_id','amount','expense_id'], 15),
                                                           }),
                'number_of_month':fields.integer("Allocated Months", readonly=True, help='Number of months expense will be allocated automatically. This field use for automatically create Allocation Sheet'),
                }

    _defaults = {
                'allocated_to': lambda self, cr, uid, context={}:'GE' if context.get('general_expense',False) else 'PE',
                'expense_type': lambda self, cr, uid, context={}:'expense' ,
                'account_analytic_id': _get_job,
                'section_incharge_id': _get_section_incharge,
                }
    
    def onchange_expensetype(self, cr, uid, ids, type, partner_id, taxes_id):#Auto fill location when change Owner
        value = {}
        if type == 'monthly_expense' and taxes_id:
            value['taxes_id'] = [] 
        if not partner_id and type=='monthly_expense':
            value.update({'partner_id': self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.id})
        return {'value': value}
    
    def onchange_section_incharges(self, cr, uid, ids,allocated_to,section_incharge_id):#Auto fill location when change Owner
        value = {}
        if allocated_to == 'PGE':
            user = self.pool.get('res.users').browse(cr, uid, uid)            
            if user.employee_id.department_id.general_incharge:
                value.update({'section_incharge_id':user.employee_id.department_id.id})
        return {'value': value}
    
    def action_draft_to_waiting_for_payment(self, cr, uid, ids, context=None):
        if not context:
            context = {}
    
        period_obj = self.pool.get('account.period')
        for exp in self.browse(cr, uid, ids, context=context):
            if not exp.expense_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a Expense without any Expense Details.'))
            else:
                state = 'done' if exp.expense_type == 'monthly_expense' else 'waiting_for_payment'
                
                period_id = exp.period_id and exp.period_id.id or False
                if not period_id:
                    period_ids = period_obj.find(cr, uid, exp.date, context)
                    period_id = period_ids and period_ids[0] or False
                self.write(cr, uid, [exp.id], {'state' : state, 'period_id':period_id})
                if exp.expense_type != 'monthly_expense':
                    result = self.action_expense_create_supplier_payment_expense(cr, uid, ids)
        return True

class kderp_other_expense_line(osv.osv):
    _name = 'kderp.other.expense.line'
    _inherit = 'kderp.other.expense.line'
    
    AllOCATED_STATE_SELECTION =[('draft','Draft'),
                                ('done','Completed'),
                                ('revising','Expense Revising'),
                                ('cancel','Expense Canceled')]

    def _get_budget(self, cr, uid, context = {}):
        res = False
        bg_code = context.get('budget_code', False)
        if bg_code:
            bg_ids = self.pool.get('account.budget.post').search(cr, uid, [('code','=',bg_code)])
            res = bg_ids[0] if bg_ids else False
        return res
    
    _columns = {
                'section_id':fields.many2one('hr.department','Alloc. Section', select = 1),
                'belong_expense_id':fields.many2one('kderp.other.expense', 'Fixed Asset/Prepaid', domain=[('expense_type','in',('prepaid','fixed_asset')),('state','not in',('draft','cancel','done'))]),
                'description':fields.related('expense_id','description', string='Desc.', type='char', size=128, store=False),
                'date':fields.related('expense_id', 'date', string='Date', type='date', store = False),
                'state':fields.related('expense_id','state',string='State',selection=AllOCATED_STATE_SELECTION,type='selection',store =False)
                }
    
    _defaults ={
               'budget_id':_get_budget
               }
    
    def _check_job_budget(self, cr, uid, ids, context=None):
        job_budget_list=[]
        for kel in self.browse(cr, uid, ids):
            if kel.account_analytic_id.general_expense and kel.budget_id.nofilter:
                continue 
            job_id = kel.account_analytic_id.id
            budget_id=kel.budget_id.id
            job_budget_list.append((job_id,budget_id))
        if job_budget_list:
            job_budget_list=",".join(map(str,job_budget_list))
            cr.execute("""Select id from kderp_budget_data where (account_analytic_id,budget_id) in (%s)""" % job_budget_list)
            if cr.rowcount:
                return True
            else:
                return False
        return True
    
    def action_submit(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        koe_ids=[]
        expense_id =self.browse(cr, uid, ids[0]).expense_id.id
        koe_ids.append(expense_id)
        self.pool.get('kderp.other.expense').action_draft_to_waiting_for_payment(cr, uid, koe_ids, context)
        return True
    
    def action_open_related_exp(self, cr, uid, ids, *args):
        context = filter(lambda arg: type(arg) == type({}), args)
        if not context:
            context = {}
        else:
            context = context[0]
        context['general_expense'] = True
        
        expense_id = self.browse(cr, uid, ids[0]).expense_id.id
        interface_string = 'General Expense'
        if expense_id:
            return {
                    'type': 'ir.actions.act_window',
                    'name': interface_string,
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'context': context,
                    'res_model': 'kderp.other.expense',
                    'domain': "[('id','=',%s)]" % expense_id
                    }
        else:
            return True
        
    _constraints = [(_check_job_budget, 'Please check you Job and Budget you have just modify (No Budget Job) !', ['account_analytic_id','budget_id'])]
