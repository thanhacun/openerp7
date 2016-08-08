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
from openerp import netsvc

from openerp.tools.translate import _

warning_job_po = {'title': 'Purchase with Job Completed/Closed/Cancelled','message':"You're editing a Job already Completed/Closed/Cancelled"}
warning_job_po_all = "This Order created after related Job were Closed !"

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    def check_date_closed(self, cr, uid, min_date):
        res = {}
        if min_date:
            ap_obj = self.pool.get('account.period')
            curr_period_ids = ap_obj.find(cr, uid)
            if curr_period_ids:
                curr_period_obj = ap_obj.browse(cr, uid, curr_period_ids[0])
                if min_date <= curr_period_obj.date_start:
                    res['title'] = 'Date Closed'
                    res['message'] = "You're editing a record with some document have date already closed"
        return res

    def new_code(self, cr, uid, ids, job_id, order_type, name=False, jobChange = False):
        res = super(purchase_order, self).new_code(cr, uid, ids, job_id, order_type, name)
        if job_id and jobChange:
            job_obj = self.pool.get('account.analytic.account').browse(cr, uid, job_id)
            if job_obj.state!='doing':
                warning = res.get('warning',{})
                warning['title'] = warning.get('title','') + ("\n" if warning.get('title','') else "") +  warning_job_po['title']
                warning['message'] = warning.get('message','') +  ("\n" if warning.get('message','') else "") +  warning_job_po['message']
                res['warning'] = warning
            if ids and self.pool.get('res.users').browse(cr, uid, uid).location_user=='hanoi':
                min_date = False
                for po in self.browse(cr, uid, ids):
                    for vatinv in po.supplier_vat_ids:
                        if not min_date or min_date > vatinv.date:
                            min_date = vatinv.date
                if min_date:
                    new_warning = self.check_date_closed(cr, uid, min_date)
                    if new_warning:
                        warning = res.get('warning', {})
                        warning['title'] = warning.get('title', '') + ("\n / " if warning.get('title', '') else "") + \
                                           new_warning['title']
                        warning['message'] = warning.get('message', '') + ("\n" if warning.get('message', '') else "") + \
                                             new_warning['message']
                        res['warning'] = warning
        return res

    # Them truong hop khi thay doi Supplier thi neu co hop dong chung thi se thay doi hop dong chung va ngay hop dong chung
    def onchange_partner_id(self, cr, uid, ids, partner_id, date=False, order_ref = False, job_id = False, order_details = [], discount_amount = 0, taxes_id = False):
        # TODO
        # Onchange Value, onchange new Code

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

        #FIXME Please consider Calculator Amount from Line
        #TODO DNT Vu Add check Order ref and Supplier, Job Warning if exists
        filterAll = [('state','!=','cancel'),('origin','ilike',order_ref)]
        filterAll += [('id','!=', ids[0])] if ids else []
        message = ''

        if order_ref and job_id and order_details:
            def getAmount(orderLine):
                #FIXME If using currency for rounding
                res = {}
                val = 0
                for line in orderLine:
                   val += line['price_unit'] * line['plan_qty']

                for tax in self.pool.get('account.tax').browse(cr, uid, taxes_id[0][2]):
                    if tax.type=='percent':
                        val += (val - discount_amount)*tax.amount
                    elif tax.type=='fixed':
                        val += tax.amount
                val = val - discount_amount
                return val
            from kderp_base import kderp_base

            lineAmount = kderp_base.get_list_value_from_tree(cr, uid, ids, 'purchase.order.line', order_details, ['price_unit','plan_qty'])
            amountTotal = getAmount(lineAmount)
            #Same Job, Quotation and Amount
            poDomain = [('account_analytic_id','=',job_id),('amount_total','=', amountTotal)] + filterAll
            po_ids = self.search(cr, uid, poDomain)
            if po_ids:
                 message = _("Can not input this quotation, please check Job, Quotation and Amount may be exists")
            else:
                #Same Quotation, Amount and different Job
                poDomain = [('account_analytic_id','!=',job_id),('amount_total','=', amountTotal)] + filterAll
                po_ids = self.search(cr, uid, poDomain)
                if po_ids:
                    message = _("Please check Job, Quotation and Amount may be exists")
        if not message and order_ref and partner_id:
            poDomain = [('partner_id','=', partner_id),('origin','ilike',order_ref)]  + filterAll
            po_ids = self.search(cr, uid, poDomain)
            if po_ids:
                message = _("Please check Supplier, Quotation may be exists")
        if message:
            po_no = [po['name'] for po in self.read(cr, uid, po_ids,['name'])]
            res['warning'] = {'title':'KDERP Warning','message': message + ", ".join(po_no)}
        return res

    def _get_warning(self, cr, uid, ids, name, args, context):
        res = {}
        for po in self.browse(cr, uid, ids):
            if po.account_analytic_id.state != 'doing' and po.account_analytic_id.date and po.date_order > po.account_analytic_id.date:
                res[po.id] = warning_job_po_all
            else:
                res[po.id] = ""
                for pol in po.order_line:
                    if pol.account_analytic_id.state != 'doing' and pol.account_analytic_id.date and po.date_order > pol.account_analytic_id.date:
                        res[po.id] = warning_job_po_all
                        break
        return res
    _columns={
                'purchase_general_contract_id':fields.many2one('kderp.purchase.general.contract','G.C. No.',states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}),
                'warning_message':fields.function(_get_warning, method=True, string='Warning', type='char', size = 256),
            }

    def _check_duplicate_po_id(self, cr, uid, ids, context=None):
        """
            Kiem tra xem po co bi nhap trung hay khong
        """
        for po in self.browse(cr, uid, ids, context=context):
            if po.state not in ('draft','cancel'):
                return True
            else:
                jobID = po.account_analytic_id.id
                orderRef = po.origin
                PartnerID = po.partner_id.id
                flds = ['amount_tax','amount_untaxed','discount_percent','final_price','amount_total']
                def getAmount():
                    #FIXME If using currency for rounding
                    res = {}
                    AmountTotal = 0
                    for line in po.order_line:
                       AmountTotal += line.price_unit * line.plan_qty
                    for tax in po.taxes_id:
                        if tax.type=='percent':
                            AmountTotal += (AmountTotal - po.discount_amount)*tax.amount
                        elif tax.type=='fixed':
                            AmountTotal += tax.amount
                    AmountTotal = AmountTotal - po.discount_amount
                    return AmountTotal
                AmountTotal = getAmount()

                filterAll = [('state','!=','cancel'),('origin','ilike',orderRef)]
                filterAll += [('id','not in', ids)] if ids else []
                poDomain = [('account_analytic_id','=',jobID),('amount_total','=',AmountTotal)] + filterAll
                po_ids = self.search(cr, uid, poDomain)
                if po.name.upper().find('PO')>=0 and len(po_ids)>=1:
                    poDomain = [('account_analytic_id','=',jobID),('amount_total','=',AmountTotal),('name','ilike','PO%'),('id','in',po_ids)] + filterAll
                    po_ids = self.search(cr, uid, poDomain)
                    if len(po_ids)>=1:
                        return False
                elif len(po_ids)>=1:
                    return False
        return True
    _constraints = [(_check_duplicate_po_id, "KDERP Warning, Can't input this PO please check Quotation, Job", ['origin','account_analytic_id','discount_amount','taxes_id','order_line','state'])]

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

class purchase_order_line(osv.osv):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'

    def onchange_job(self, cr, uid, ids, order_id):
        res = {}
        if order_id and self.pool.get('res.users').browse(cr, uid, uid).location_user=='hanoi':
            min_date = False
            po = self.pool.get('purchase.order').browse(cr, uid, order_id)
            for vatinv in po.supplier_vat_ids:
                if not min_date or min_date > vatinv.date:
                    min_date = vatinv.date
            if min_date:
                warn = self.pool.get('purchase.order').check_date_closed(cr, uid, min_date)
                if warn:
                    res['warning']  = warn
        return res
