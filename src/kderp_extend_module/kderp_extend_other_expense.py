from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import openerp.addons.decimal_precision as dp
class kderp_other_expense(osv.osv):
    _name = 'kderp.other.expense'
    _inherit= 'kderp.other.expense'      
    
    def action_expense_create_payment(self, cr, uid, ids, *args):
        res = False
        #for o in self.browse(cr, uid, ids):
        for o in self.read(cr, uid, ids,['amount_total',
                                         'expense_line',
                                         'tax_amount',
                                         'currency_id',
                                         'account_analytic_id',
                                         'description'
                                         ]):        
            if o['rop_ids']:
                self.write(cr, uid, ids, {'state':'delivered','exp_status':'waiting'})
                wf_service = netsvc.LocalService("workflow")
                try:
                    wf_service.trg_delete(uid, self._name, o['id'], cr)
                except:
                    a = True
                return True
                #raise osv.except_osv('Warning','Request of payment already exist')
            payment_details = []
            adv_amount = 0.0
            retention_amount = 0.0
            adv = 0.0
            retention = 0.0
            progress = 0.0
            for po_term in self.pool.get('kdvn.po.payment.term.line').read(cr,uid,o['order_payment_term_ids'],['type','value_amount']):
                if po_term['type']=='adv':
                    adv_amount = po_term['value_amount']*o['amount_total2']/100
                    adv = po_term['value_amount']
                elif po_term['type']=='re':
                    retention_amount = po_term['value_amount']*o['amount_total2']/100
                    retention = po_term['value_amount']
                else:                    
                    progress = po_term['value_amount']
            for po_term in self.pool.get('kdvn.po.payment.term.line').read(cr,uid,o['order_payment_term_ids'],['type','value_amount','name']):
                if po_term['type']!='p':
                    this_tax_amount = 0.0
                    this_progress_amount = 0.0
                    if po_term['type']=='adv':
                        this_retention_amount = 0.0
                        this_adv_amount = adv_amount
                    else:
                        this_adv_amount = 0.0
                        this_retention_amount = retention_amount
                else:
                    #progress = po_term['value_amount']
                    this_tax_amount = o['tax_amount']*po_term['value_amount']/100.0
                    this_progress_amount = o['amount_total2']*po_term['value_amount']/100.0
                    this_adv_amount = - adv_amount*progress/100.0
                    this_retention_amount = - retention_amount*progress/100.0
                payment_details = []
                cr.execute("Select\
                                pol.project_id,\
                                kdvn_budget_id,\
                                abp.name as budget_name,\
                                sum(price_subtotal2)\
                            from \
                                purchase_order_line pol\
                            left join\
                                product_product pp on product_id = pp.id\
                            left join\
                                account_budget_post abp on kdvn_budget_id = abp.id\
                            where order_id=%s\
                            group by\
                                pol.project_id,\
                                kdvn_budget_id,\
                                budget_name" % (o['id']))
                for project_id,budget_id,budgetname,amount in cr.fetchall():
                #self.pool.get('purchase.order.line').read(cr,uid,o['order_line'],['product_id','project_id','product_uom','price_subtotal2','name']):
                    #pr_id = budget_id
                    #prj_id = o.project_id.id
                    #raise osv.except_osv("E","%s-%s-%s" %(adv,retention,progress))
                    payment_details.append(self.payment_detail_create(project_id,budget_id,budgetname,amount,po_term['type'],adv,retention,progress))

                if o['notes']:
                    new_description = o['notes']
                else:
                    new_description = ""
                cr.execute("""SELECT uid
                              FROM res_groups_users_rel 
                                  where gid in( select id from res_groups where name ='KDERP - Supplier Payment Read Only Bankstransfer')
                            and uid =%s
                            """%(uid))
                if cr.rowcount !=0:  
                    payment_type='cash'     
                else:
                    payment_type='bank'                      
                payment = {
                    'paymentno':'',
                    'payment_type':payment_type,
                    'amount':this_progress_amount,
                    'tax_amount':this_tax_amount,
                    'advanced_amount':this_adv_amount,
                    'retention_amount':this_retention_amount,
                    'tax_per':int(o['tax_per']) or 0,
                    'supplier_id': o['partner_id'][0],
                    'currency_id': o['currency_id'][0],
                    'detail_ids': payment_details,
                    'order_id':o['id'], # For KDVN,
                    'project_id':o['project_id'][0],
                    'description':new_description#po_term['name'] + "\n"+  o['notes']
                    }
                #raise osv.except_osv("E",payment)
                kdvn_rop_id = self.pool.get('kdvn.request.of.payment').create(cr, uid, payment)
                self.write(cr, uid, ids, {'state':'delivered','exp_status':'waiting'})
                wf_service = netsvc.LocalService("workflow")
                try:
                    wf_service.trg_delete(uid, self._name, o['id'], cr)
                except:
                    a = True
                #    wf_service.trg_create(uid, 'purchase.order', p_id, cr)
        #return kdvn_rop_id  
    
kderp_other_expense()

