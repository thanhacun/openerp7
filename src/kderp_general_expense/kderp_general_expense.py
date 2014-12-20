from openerp.osv import fields, osv
import time
from openerp.tools.translate import _

class account_budget_post(osv.osv):
    """
        Inherit Budget add new some field, using for Budget Code
    """
    _name = 'account.budget.post'
    _inherit = 'account.budget.post'
    
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

class kderp_other_expense(osv.osv):
    """
    Customize Other Expense suiteable with general expense
    """
    _name = 'kderp.other.expense'
    _inherit = 'kderp.other.expense'

    EXPENSE_TYPE_SELECTION =(
                    ('expense', 'Expense'),
                    ('monthly_expense','Recognize Expense'),
                    ('prepaid', 'Prepaid'),
                    ('fixed_asset', 'Fixed Asset (With Depreciation)'))

    ALLOCATE_SELECTION =(
                    ('PE','Job Expense'),
                    ('GE','General Expense'),
                    ('PGE','Job & General Expense'))
    
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
            return filter(lambda x: x[0] <> 'GE', self.ALLOCATE_SELECTION)
        
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
            koel_ids = koel_obj.search(cr, uid, [('belong_expense_id','=',id)])
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
    
    STATE_SELECTION=[('draft','Draft'),
                   ('waiting_for_payment','Waiting for Payment'),
                   ('paid','Paid'),
                   ('done','Completed'),
                   ('revising','Expense Revising'),
                   ('cancel','Expense Canceled')]
    _columns = {
                'allocated_date':fields.date('Allocated Date', states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}),
                'expense_type':fields.selection(EXPENSE_TYPE_SELECTION, 'Exp. Type', required = True, states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},
                                                help="""Expense: Allocated direct to Job/General have payment\nRecognize Expense: Recognize allocated to Job/General from Fixed Asset, Prepaid without payment\nPrepaid, Fixed Asset for management and don't allocated"""),
                'allocated_to':fields.selection(_get_allocated_selection, 'Allocate To', required = True, states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}, select = 1),
                'link_asset_id':fields.many2one('kderp.asset.management', 'Asset', states={'done':[('readonly',True)]}),
                #'belong_expense_id':fields.many2one('kderp.other.expense', 'Belong to', states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},
                #                                    domain=[('expense_type','in',('prepaid','fixed_asset')),('state','not in',('draft','cancel','done'))]),
                'section_incharge_id':fields.many2one('hr.department','Section In Charges', domain=[('general_incharge','=',True)],  select = 1, states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}),#General Affair or General Coordination Section
                'related_expense_ids':fields.function(_get_related,string='Related',type='one2many',relation='kderp.other.expense.line', readonly=True),
                
                'sections':fields.function(_get_sections,string='Sections',size=256
                                         ,type='char', method=True,
                                          store={
                                                  'kderp.other.expense.line': (_get_expense_from_detail, ['section_id'], 10)
                                                 }),
                'state':fields.selection(STATE_SELECTION,'Exp. Status',readonly=True,select=1),
                'state_depend':fields.function(_get_state,selection=STATE_SELECTION,type='selection', string='Exp. Status',multi="_get_state"),
                'state_recognize':fields.function(_get_state,selection=STATE_SELECTION,type='selection', string='Exp. Status',multi="_get_state")
                }

    _defaults = {
                'allocated_to': lambda self, cr, uid, context={}:'GE' if context.get('general_expense',False) else 'PE',
                'expense_type': lambda self, cr, uid, context={}:'expense',
                'account_analytic_id': _get_job,
                'section_incharge_id': _get_section_incharge,
                }
    
    def onchange_expensetype(self, cr, uid, ids, type, partner_id):#Auto fill location when change Owner
        res = {}
        if not partner_id and type=='monthly_expense':
            res = {'partner_id': self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.id}    
        return {'value': res}
    
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
    
    _columns = {
                'section_id':fields.many2one('hr.department','Alloc. Section', select = 1),
                'belong_expense_id':fields.many2one('kderp.other.expense', 'Belong to', domain=[('expense_type','in',('prepaid','fixed_asset')),('state','not in',('draft','cancel','done'))]),
                'description':fields.related('expense_id','description', string='Desc.', type='char', size=128, store=False)
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
    _constraints = [(_check_job_budget, 'Please check you Job and Budget you have just modify (No Budget Job) !', ['account_analytic_id','budget_id'])]