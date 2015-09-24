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

import time
from openerp.osv import fields, osv, orm
from openerp import netsvc

from openerp.tools.translate import _

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _description = 'Purchase Order'
    
    # Them truong hop khi thay doi Supplier thi neu co hop dong chung thi se thay doi hop dong chung va ngay hop dong chung
    def onchange_partner_id(self, cr, uid, ids, partner_id, date=False):
        res = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if not partner_id:
            return res
        
        cr.execute("""Select 
                            id
                    from 
                        kderp_purchase_general_contract 
                    where 
                        partner_id=%s and date=(select max(date) from kderp_purchase_general_contract where partner_id=%s)""" % (partner_id,partner_id))
        
        res_sql = cr.fetchone()
        purchase_general_contract_id = res_sql[0] if res_sql else False
     
        res['value']['purchase_general_contract_id'] = purchase_general_contract_id        
        return res
                     
    _columns={
                'purchase_general_contract_id':fields.many2one('kderp.purchase.general.contract','G.C. No.',states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}),                
            }
    
    #Check Done for Workflow
    def check_done(self, cr, uid, ids, *args):
        res = True
        for po in self.browse(cr, uid, ids):
            if not(po.total_request_amount==po.total_vat_amount and po.total_vat_amount==po.total_payment_amount and po.total_payment_amount==po.amount_total):
                return False
        return res
    
    #Return ids for trigger workflow
    def get_ksp_ids_from_po(self, cr, uid, ids, *args):
        res = {}
        for po in self.browse(cr, uid, ids):
            for ksp in po.supplier_payment_ids:
                res[ksp.id] = True
        return res.keys()
    
    def get_kspp_ids_from_po(self, cr, uid, ids, *args):
        res = {}
        for po in self.browse(cr, uid, ids):
            for kspvat in po.supplier_vat_ids:            
                res[kspvat.id] = True
        return res.keys()
    
    def get_kspvat_ids_from_po(self, cr, uid, ids, *args):
        res = {}
        for po in self.browse(cr, uid, ids):
            for ksp in po.supplier_payment_ids:
                for kspp in ksp.payment_ids:
                    res[kspp.id] = True
        return res.keys()
    
    def action_cancel(self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids):
            for ksp in po.supplier_payment_ids:
                if ksp.state not in ('draft','cancel'):
                    raise osv.except_osv("KDERP Warning","Please Cancel all Request of Payment Related, before you cancel this PO.")
            for sm in po.received_details:
                if sm.state not in ('draft','cancel'):
                    raise osv.except_osv("KDERP Warning","Can't cancel this purchase. Please check Packing list")
                
        self.write(cr, uid, ids, {'state':'cancel'})
        wf_service = netsvc.LocalService("workflow")
        for po_id in ids:
            try:
                wf_service.trg_delete(uid, 'purchase.order', po_id, cr)
            except:
                continue
        return True
    
purchase_order()