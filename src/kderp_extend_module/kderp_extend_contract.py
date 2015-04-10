# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class kderp_contract_client(osv.osv):
    _name='kderp.contract.client'
    _description='KDERP Contract to Client'
    _inherit = 'kderp.contract.client'
    
    def action_open_contract_state(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'uncompleted'})
        return True
        
    def action_contract_cancelled(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'availability':'cancelled'})
        return True
    
    def action_contract_inused(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'availability':'inused'})
        return True
    
    def onchange_reg_date(self, cr, uid, ids,registration_date,revise_date):
        val={}
        if not revise_date and self.pool.get('res.users').browse(cr, uid, uid, {}).location_user=='hanoi':
            val={'revise_date':registration_date}
        return {'value':val}
    
    def onchange_client_id(self, cr, uid, ids, client_id):
        if not client_id:
            val={}
        else:
            rp_obj=self.pool.get('res.partner').browse(cr, uid, client_id)
            invoice=False
            invoice_address_id=False
            address_id=False
            
            last_address_id=False
                        
            for rpl in rp_obj.child_ids:
                if rpl.type=='invoice':
                    invoice_address_id=rpl.id
                    invoice=True
                if rpl.type=='default':
                    if not invoice:
                        invoice_address_id=rpl.id
                    address_id = rpl.id
                last_address_id=rpl.id
            if not address_id and last_address_id:
                address_id=last_address_id
                invoice_address_id=last_address_id if not invoice_address_id else invoice_address_id
            elif not address_id:
                address_id=rp_obj.id
                invoice_address_id=rp_obj.id if not invoice_address_id else invoice_address_id
            val={'address_id':address_id,'invoice_address_id':invoice_address_id}
        return {'value':val}
    
    def _get_job_issued_from_from_client_payment(self, cr, uid, ids, context=None):
        res=[]
        for kcp in self.pool.get('account.invoice').browse(cr,uid,ids):
            res.append(kcp.contract_id.id)
        return list(set(res))
    
    def _get_job_issued_from_vat_allocated(self, cr, uid, ids, context=None):
        res=[]
        for kpvi in self.pool.get('kderp.payment.vat.invoice').browse(cr,uid,ids):
            res.append(kpvi.payment_id.contract_id.id)
        return list(set(res))
    
    def _get_issued(self, cr, uid, ids, name, args, context=None):
        res={}
        kcc_ids=",".join(map(str,ids))
        cr.execute("""select kcc.id ,sum(coalesce(kpvi.amount-(kpvi.amount*0.1),0)),sum(coalesce(kpvi.amount*0.1,0)),sum(coalesce(kpvi.amount,0))
                    from 
                        kderp_contract_client kcc
                    left join 
                        account_invoice ai on kcc.id = ai.contract_id 
                       
                    left join 
                         kderp_payment_vat_invoice kpvi on ai.id =kpvi.payment_id
                    where
                        kcc.id in (%s)
                    group by kcc.id""" %(kcc_ids))
        for kcc_id,issued_amount,issued_vat,issued_total in cr.fetchall():
            res[kcc_id]={'issued_amount':issued_amount,
                         'issued_vat':issued_vat,
                         'issued_total':issued_total,
                         }
                         
                       
            
        return res
    def _get_value_from_contract_info(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        c_ids = ",".join(map(str,ids))
        cr.execute("""select 
                            kccl.id,
                            rc.name,
                            coalesce( kccu.amount,0)
                        from 
                            kderp_contract_client kccl
                        left join 
                            kderp_contract_currency kccu on kccl.id = kccu.contract_id  and default_curr = true
                        left join 
                            res_currency rc on kccu.name = rc.id
                        where 
                            kccl.id in (%s)
                        group by
                            kccl.id, rc.name, kccu.amount""" % (c_ids))
        for id, cur_contract_info, amount_contract_info in cr.fetchall():
            res[id]={'cur_contract_info':cur_contract_info,
                     'amount_contract_info':amount_contract_info,
                    }
        return res

    AVAILABILITY_SELECTION = [('inused',"IN USE"),("cancelled","CANCELLED")]
    
    _columns={
                'revise_date': fields.date('Rev. Date'),
                'availability':fields.selection(AVAILABILITY_SELECTION,'Availability',readonly=True),
                'remark':fields.char('Remark',size=128),
                'cur_contract_info':fields.function(_get_value_from_contract_info,type='char',
                                            size='8',method=True,string='Currency',
                                            multi='_get_value_from_contract_info',
                                             ),
                'amount_contract_info':fields.function(_get_value_from_contract_info,type='float',
                                            method=True,string='Amount',
                                            multi='_get_value_from_contract_info',
                                             ),
                 'issued_amount':fields.function(_get_issued,type='float',digits_compute=dp.get_precision('Budget'), method=True,string='VAT Issued',multi='_get_kcc_issued_vat',
                                                 store={
                                                        'account.invoice':(_get_job_issued_from_from_client_payment,None,35),
                                                        'kderp.payment.vat.invoice':(_get_job_issued_from_vat_allocated,None,35),
                                                       
                                                      }),
              'issued_vat':fields.function(_get_issued,type='float',digits_compute=dp.get_precision('Budget'), method=True,string='VAT Issued',multi='_get_kcc_issued_vat',
                                                 store={
                                                        'account.invoice':(_get_job_issued_from_from_client_payment,None,35),
                                                        'kderp.payment.vat.invoice':(_get_job_issued_from_vat_allocated,None,35),
                                                       
                                                      }),
              'issued_total':fields.function(_get_issued,type='float',digits_compute=dp.get_precision('Budget'), method=True,string='VAT Issued',multi='_get_kcc_issued_vat',
                                                 store={
                                                        'account.invoice':(_get_job_issued_from_from_client_payment,None,35),
                                                        'kderp.payment.vat.invoice':(_get_job_issued_from_vat_allocated,None,35),
                                                       
                                                      }),                        
              }
    _defaults={
               'availability':lambda *x: 'inused',
               }
kderp_contract_client()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

