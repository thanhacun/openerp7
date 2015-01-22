from osv import osv, fields
from osv.orm import intersect
import time
import openerp.addons.decimal_precision as dp
import openerp.exceptions


class kderp_general_expense(osv.osv):
    _name='kderp.general.expense'
    _description='KDERP General Expense'
    _rec_name = 'code'
    _order = "date desc"
    _order = "code desc"
    STATE_SELECTION=[('draft','Draft'),
                   ('waiting_for_approved','Waiting for Approved'),
                   ('waiting_for_payment','Waiting for Payment'),
                   ('done','Done'),
                   ('cancel','Cancel'),
                   ('revising','Revising')]
    
    def action_ge_create_ge_supplier_payment(self, cr, uid, ids, *args):
        res = {}
        kgesp_ids=[]
        for ge in self.browse(cr, uid, ids):                                                
            payment = {
                'general_expense_id':ge.id, 
                'description':ge.description,
                'tax':ge.amount_tax,
                'amount':ge.sub_total,
                'total':ge.total,
                'date': False
                    }
            kderp_kgesp_id = self.pool.get('kderp.general.expense.supplier.payment').create(cr, uid, payment)
            kgesp_ids.append(kderp_kgesp_id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'General Expense Supplier Payment',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'kderp.general.expense.supplier.payment',
            'domain': "[('general_expense_id','in',%s)]" % ids
            }
        
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if context is None:
            context={}
        if name:
            name=name.strip()
            ctc_ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
            if not ctc_ids:
                ctc_ids = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)
            if not ctc_ids:
                ctc_ids = self.search(cr, uid,[('description', 'ilike', name)] + args, limit=limit, context=context)
            if not ctc_ids:
                check=name.replace(',','')
                if check.isdigit():
                    ctc_ids = self.search(cr, uid, [('sub_total','=',name)]+ args, limit=limit, context=context)         
        else:
            ctc_ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ctc_ids, context=context)

    def _get_payment_vat_invoices(self, cr, uid, ids,  name, args, context={}):
        if not context:
            context={}
        res={}
        for ge_obj in self.browse(cr, uid, ids, context):        
            res[ge_obj.id]=[]
            for kgesp_obj in ge_obj.supplier_payment_general_expense_code_ids:
                for ksvi in kgesp_obj.kderp_vat_invoice_ids:        
                    res[ge_obj.id].append(ksvi.id)                
        return res
  
    def _get_exrate(self, cr, uid, ids, name, args, context):
        res={}
        for ge in self.browse(cr, uid, ids):
            res[ge.id]=0
            for gcc in ge.general_expense_code_id.general_expense_code_currency_ids:
                if ge.currency_id.id==gcc.name.id:
                    res[ge.id]=gcc.rate
        return res
   
    def _sub_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for ge in self.browse(cr, uid, ids, context=context):
            res[ge.id] = {
                'sub_total': 0.0,
                }
            val = 0.0
            val1=0.0
            cur = ge.currency_id
            for line in ge.general_expense_line_ids:
                val += line.amount   
            for c in self.pool.get('account.tax').compute_all(cr, uid, ge.taxes_id, val, 1, False, False)['taxes']:
                val1 += c.get('amount', 0.0)
            
            res[ge.id]['sub_total']=cur_obj.round(cr, uid, cur, val)

            res[ge.id]['amount_tax']=cur_obj.round(cr, uid, cur, val1)
            
            res[ge.id]['total']=res[ge.id]['sub_total'] + res[ge.id]['amount_tax'] 
           
        return res
    
    def on_changevalue(self, cr, uid, ids, amount, taxes_id, currency_id):
        amount_tax = 0.0
        if taxes_id[0][2]:
            tax_obj =self.pool.get('account.tax')
            val=0.0
            tax_brs = tax_obj.browse(cr, uid,taxes_id[0][2]) 
            for c in tax_obj.compute_all(cr, uid, tax_brs, amount, 1, False, False)['taxes']:
                val += c.get('amount', 0.0)
            if currency_id:
                cur_obj=self.pool.get('res.currency')
                cur_brs=cur_obj.browse(cr, uid, currency_id)
                amount_tax=cur_obj.round(cr, uid, cur_brs, val)
            else:
                amount_tax=val            
        result={'amount_tax':amount_tax,'total':amount_tax+amount}
        return {'value':result}
    
    def onchange_type(self, cr, uid, ids,type,partner_id):#Auto fill location when change Owner
        if not partner_id:
            if type=='monthly-expense':
                return {'value':{'partner_id':1}}
            else:
                return {'value':{'partner_id':partner_id}}
        else:
            return {'value':{'partner_id':partner_id}}
        
    def _get_general_expense_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('kderp.general.expense.line').browse(cr, uid, ids, context=context):
            result[line.general_expense_id.id] = True
        return result.keys()
    
    def new_code(self,cr,uid,ids,general_expense_code_id,user_id,code=False):
        if ids:
            try:
                ids=ids[0]
            except:
                ids=ids
        else:
            ids=0   
        if not (user_id and general_expense_code_id):
            val={'value':{'code':False}}
        else:            
            if ids:
                general_expense_code_list=self.read(cr, uid,ids,['general_expense_code_id','code'])
                old_general_expense_code_id=general_expense_code_list['general_expense_code_id'][0]
                old_name=general_expense_code_list['code']
                user_id_list=self.browse(cr, uid, ids)
                old_dp_code=user_id_list.user_id.employee_id.department_id.code
            else:
                old_name=False
                old_general_expense_code_id=False
                old_dp_code=False
            if old_general_expense_code_id==general_expense_code_id and old_name and old_dp_code :
                val={'value':{'code':old_name}}
            else:  
                user_id_list=self.pool.get('res.users').browse(cr, uid, user_id).employee_id
                general_expense_list=self.pool.get("kderp.general.expense.code").read(cr,uid,general_expense_code_id,['code'])
                if user_id_list:
                    dp_code=user_id_list.department_id.code
                if not general_expense_list and user_id_list:
                    val={'value':{'code':False}}
                else:
                    general_expense_code = general_expense_list['code']
                    cr.execute("select max(substring(code from '....$') ::integer) from kderp_general_expense   \
                                where code ilike '"+general_expense_code[:3]+general_expense_code[5:7]+"%'") 
                    if cr.rowcount:
                        next_code=str(cr.fetchone()[0])
                        #raise osv.except_osv("E",next_code)
                        if next_code.isdigit():
                            next_code=str(int(next_code)+1)
                        else:
                            next_code='1'
                    else:
                        next_code='1'
                    val={'value':{'code':general_expense_code[:3]+general_expense_code[5:7]+'-'+dp_code+'-'+next_code.rjust(4,'0')}}
        return val
    
    def _get_default_ge_code_id(self,cr,uid,context={}):
        cr.execute("""select id from kderp_general_expense_code where substring(code from '....$') =(select to_char('now'::text::date::timestamp with time zone, 'YYYY'::text))
                    """)
        default_ge_code_id=False
        res = cr.fetchone()
        if res:
            default_ge_code_id = res[0]
        return default_ge_code_id
    
    _columns={
                'code':fields.char('General Expesne No.',size=16,required=True,select=True,states={'done':[('readonly',True)]}),
                'date':fields.date('G.E. Date',required=True,states={'done':[('readonly',True)]}),
                'general_expense_code_id':fields.many2one("kderp.general.expense.code", string="G.E. Code",ondelete="restrict",required=True,states={'done':[('readonly',True)]}),
                'user_id':fields.many2one('res.users','User Input',ondelete="restrict",readonly=True,required=True,states={'done':[('readonly',True)]}),
                'type': fields.selection([('others','Others'),('fixed-asset','Fixed Asset'),('prepaid','Prepaid'),('monthly-expense','Monthly Expense')],'Type',required=True,states={'done':[('readonly',True)]}),
                'general_expense_line_ids':fields.one2many("kderp.general.expense.line",'general_expense_id' ,string="G.E. Detail",states={'done':[('readonly',True)]}), 
                'parent_id':fields.many2one("kderp.general.expense",string="Belong G.E.",states={'done':[('readonly',True)]}),
                'partner_id':fields.many2one('res.partner', 'Supplier', required=True, change_default=True, select=True,states={'done':[('readonly',True)]}),
                'currency_id':fields.many2one('res.currency','Currency',required = True,states={'done':[('readonly',True)]}),
                'description':fields.text('Description',states={'done':[('readonly',True)]}),
                'advance_id':fields.many2one('kderp.advance.payment',string='Advance No.',states={'done':[('readonly',True)]}),
                'state':fields.selection(STATE_SELECTION,'Exp. Status',readonly=True,select=1,states={'done':[('readonly',True)]}),
                'supplier_payment_general_expense_code_ids':fields.one2many('kderp.general.expense.supplier.payment','general_expense_id','Supplier Payment',Type={'monthly-expense': [('readonly',True)]}, states={'done':[('readonly',True)]}),
                'supplier_vat_ids':fields.function(_get_payment_vat_invoices,string='VAT Invoices',type='one2many',relation='kderp.supplier.vat.invoice',method=True,states={'done':[('readonly',True)]}),
                'taxes_id': fields.many2many('account.tax', 'general_expense_vat_tax', 'general_expense_vat_id', 'tax_id', 'VAT (%)',states={'done':[('readonly',True)]}), 
                'exrate':fields.function(_get_exrate,string='Ex.Rate',type='float',digits_compute=dp.get_precision('Exrate')),
                'sub_total':fields.function(_sub_total, digits_compute= dp.get_precision('Sub-Total'),string='Sub-Total',type='float', method=True, multi="kderp_general_expense_total",
                                                  store={
                                                         'kderp.general.expense':(lambda self, cr, uid, ids, c={}: ids,None,50),
                                                         'kderp.general.expense.line': (_get_general_expense_line, None, 10),                                                         
                                                          }),
                'total':fields.function(_sub_total, digits_compute= dp.get_precision('Total'),string='Total',type='float', method=True, multi="kderp_general_expense_total",
                                                  store={
                                                         'kderp.general.expense':(lambda self, cr, uid, ids, c={}: ids,None,50),
                                                         'kderp.general.expense.line': (_get_general_expense_line, None, 10),                                                         
                                                         }),
                'amount_tax':fields.function(_sub_total, digits_compute= dp.get_precision('Amount-Tax'),string='Amount Tax',type='float', method=True, multi="kderp_general_expense_total",
                                                  store={
                                                         'kderp.general.expense':(lambda self, cr, uid, ids, c={}: ids,None,50),
                                                         }),
              }
    

   
    _sql_constraints = [
                            ('general_expense_no', 'unique(code)', 'General Expense Number must be unique !')
                        ]
    
    _defaults={
               'user_id':lambda obj, cr, uid, context: uid,
               'currency_id':lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id,
               'date' :fields.date.context_today,
               'state':lambda *x: 'draft',
               'general_expense_code_id':_get_default_ge_code_id
               }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'supplier_payment_general_expense_code_ids':False,
            'code':self.new_code(cr, uid, 0,self.browse(cr, uid, id,context).general_expense_code_id.id, self.browse(cr, uid, id,context).user_id.id,False)['value']['code']
    
        })
        return super(kderp_general_expense, self).copy(cr, uid, id, default, context)
    
    #Delete all line kderp general expense line
    def action_delete_all_line(self, cr, uid, ids, context):
        gel_obj=self.pool.get('kderp.general.expense.line')
        gel_ids = gel_obj.search(cr, uid,[('general_expense_id','in',ids)])
        if gel_ids:
            gel_obj.unlink(cr, uid, gel_ids)
        return True
    
    def wkf_action_draft_approved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'waiting_for_approved'})
        return True
    
    def wkf_action_approved_wfr(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'waiting_for_payment'})
        return True
    
    def wkf_action_done_wfr(self, cr, uid, ids, context=None):
        if not context:
            context = {}
            
        for ge in self.browse(cr, uid, ids, context=context):
            if ge.type =='monthly-expense':
                self.write(cr, uid, ids, {'state':'done'})
                cr.execute("""select kge.id,
                                    sum(coalesce(qramount.total,0)),
                                    coalesce(kge.sub_total,0),
                                    coalesce(qr_payment.payment_amount,0)
                                from 
                                    kderp_general_expense kge 
                                left join 
                                    (select kspe.general_expense_id as id ,sum(coalesce(kspe.amount,0))as payment_amount
                                    from kderp_general_expense_supplier_payment kspe group by kspe.general_expense_id
                                    
                                    )qr_payment on qr_payment.id=kge.id
                                left join 
                                    ( select kgem.parent_id as id ,
                                        kgem.id as general_expense_id,
                                        kgebc.id as budget_code,
                                        sum(kgel.amount) as total  
                                    from 
                                        kderp_general_expense kgem 
                                        left join 
                                        kderp_general_expense kge on kge.id =kgem.parent_id 
                                        left join 
                                        kderp_general_expense_line kgel on kgel.general_expense_id=kgem.id
                                        left join 
                                        kderp_general_expense_budget_code  kgebc on kgebc.parent_id =kgel.budget_id where kgebc.id >0
                                        group by kgem.parent_id,kgem.id ,kgebc.id 
                                    union 
                                        select parent_id  as id ,
                                        kge.id , 
                                        qr.budget_id ,
                                        sum(kgel.amount) as total 
                                    from 
                                        kderp_general_expense kge
                                    left join 
                                        kderp_general_expense_line kgel on kgel.general_expense_id=kge.id
                                        left join(
                                        select budget_id,
                                            kge.id as general_expense_id  
                                        from  
                                            kderp_general_expense_line kgel 
                                        left join 
                                            kderp_general_expense kge  on kge.id = general_expense_id
                                                 ) qr on qr.general_expense_id =kge.parent_id and qr.budget_id=kgel.budget_id
                                                 where  qr.budget_id>0
                                                 group by qr.budget_id ,kge.id ,kge.parent_id 
                                     ) qramount on qramount.id =kge.id
                                     where kge.id =(select parent_id from kderp_general_expense where id =%s) 
                                group by kge.id,qr_payment.payment_amount
                     """ % ge.id)
                for id,total,total_amount,total_amount_payment in cr.fetchall():
                    if total==total_amount and total_amount==total_amount_payment:
                        cr.execute("""Update kderp_general_expense set state ='done' where id =(select parent_id from kderp_general_expense where id =%s) """ % ge.id)
        return True
    
    def action_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'revising'})
    
    def action_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
kderp_general_expense()

class kderp_general_expense_line(osv.osv):
    _name='kderp.general.expense.line'
    _description='KDERP General Expense Detail'
    _order="budget_id desc"
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        #If want to set limit please sea search product
        if not args:
            args = []
        if name:
            ids=[]
            if not ids:
                ids = self.search(cr, user, [('general_expense_id',operator,name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('budget_id',operator,name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('description','ilike',name)]+ args, limit=limit, context=context)
            if not ids:
                check=name.replace(',','')
                if check.isdigit():
                    ids = self.search(cr, user, [('amount','=',name)]+ args, limit=limit, context=context)            
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    _columns={
                'general_expense_id':fields.many2one("kderp.general.expense", string="General Expense",ondelete="restrict"), 
                'description':fields.char('Description',size=128),
                'budget_id':fields.many2one("kderp.general.expense.budget.code", string="Budget",ondelete="restrict",required=True,context={'gec_id':0}), 
                'amount':fields.float('Amount',required=True),    
                'asset_id':fields.many2one('kderp.asset.management','Asset',ondelete="restrict",),   
              }
    
    _defaults={
                'general_expense_id':lambda obj, cr, uid, context: context.get('general_expense_id',False),
                }
    
    def open_general_expense_line(self, cr, uid, ids, context=None):
        return {
            "type": "ir.actions.act_window",
            "name": "General Expense Budget Line",
            "res_model": 'kderp.general.expense.line',
            "res_id": ids[0] if ids else False,
            "view_type": "form",
            "view_mode": "form",
            "target":"current",
            'context':context,
            'nodestroy': True,
            'domain': "[('id','in',%s)]" % ids
        } 
kderp_general_expense_line()


