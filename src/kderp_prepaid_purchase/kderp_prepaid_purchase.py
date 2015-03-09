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
from kderp_base import kderp_base
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class kderp_prepaid_purchase_order(osv.osv):
    _name = 'kderp.prepaid.purchase.order'
    _description = 'KDERP Prepaid Purchase Order'
    
    def name_get(self, cr, uid, ids, context=None):
        if not context: context={}
        res=[]
        for record in self.browse(cr, uid, ids):
            name = "%s - %s" % (record.code, record.name)  
            res.append((record['id'], name))
        return res
       
    SELECTION_STATE = [('draft','Draft'),
                       ('approved','Approved')]
    
    def onchange_date(self, cr, uid, ids, oldno, date):
        val = {}
        if not oldno and date:
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
                                    kderp_prepaid_purchase_order.code
                                FROM 
                                    kderp_prepaid_purchase_order
                                WHERE
                                    length(kderp_prepaid_purchase_order.code::text)=
                                    ((SELECT 
                                    length(prefix || suffix) + padding AS length
                                    FROM 
                                    ir_sequence
                                    WHERE 
                                    ir_sequence.code::text = 'kderp_prepaid_order_code'::text LIMIT 1))
                                ) cnewcode ON cnewcode.code::text ~~ (isq.prefix || to_char(DATE '%s',  suffix || lpad('_',padding,'_'))) and isq.code::text = 'kderp_prepaid_order_code'::text  
                            WHERE isq.active and isq.code::text = 'kderp_prepaid_order_code') wnewcode
                        GROUP BY 
                            pattern, 
                            name,
                            seq_code,
                            prefix,
                            padding""" %(date,date,date,date))
            res = cr.fetchone()
            if res:
                val={'code':res[0]}
        
        return {'value':val}
    
    _order="date desc, name desc"
    _columns={
              'code':fields.char('Code', required = True, size=16, select=1, readonly = True, states={'draft':[('readonly', False)]}),
              'name':fields.char('Description', required = True, size=64, readonly = True, states={'draft':[('readonly', False)]}),
              'date':fields.date('Order Date', select = 1, required = True, readonly = True, states={'draft':[('readonly', False)]}),
              
              'partner_id':fields.many2one('res.partner', 'Supplier', ondelete='restrict', required=True, readonly = True, states={'draft':[('readonly', False)]} , change_default=True),
              'address_id':fields.many2one('res.partner', 'Address', ondelete='restrict', required=True, readonly = True, states={'draft':[('readonly', False)]}),
              
              'prepaid_order_line':fields.one2many('kderp.prepaid.purchase.order.line', 'prepaid_order_id', readonly = True, states={'draft':[('readonly', False)]}),
              
              'state':fields.selection(SELECTION_STATE, 'State', readonly = True) 
              
              }
    
    _defaults = {
                 'date': lambda *a: time.strftime('%Y-%m-%d'),
                 'state': lambda *x: 'draft',
                 'partner_id':lambda self, cr, uid, context={}: context.get('partner_id',False)
                 }
    
    _sql_constraints=[('kderp_prepaid_purchase_code_unique','unique(code)','Prepaid Purchase Code must be unique !')]
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        if not partner_id:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
                }}
        supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        return {'value': {'address_id': supplier.id or False }}
    
kderp_prepaid_purchase_order()

class kderp_prepaid_purchase_order_line(osv.osv):
    _name = 'kderp.prepaid.purchase.order.line'
    _description = 'kderp.prepaid.purchase.order.line'
    
    def onchange_product_id(self, cr, uid, ids, product_id, qty, uom_id, price_unit, context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}
  
        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res
  
        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        
        product = product_product.browse(cr, uid, product_id, context)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
        if not name:
            dummy, name = product_product.name_get(cr, uid, product_id, context,from_obj='pol')[0]
            if product.description_purchase:
                name = product.description_purchase
        res['value'].update({'name': name})
  
        # - set a domain on product_uom
#        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}
  
        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id
  
        res['value'].update({'product_uom': uom_id})
  
        # - determine product_qty and date_planned based on seller info 
        qty = qty or 1.0
        
        if qty:
            res['value'].update({'product_qty': qty})
  
        return res   
  
    _columns={
              'product_id':fields.many2one('product.product','Product', required = True),
              'product_uom':fields.many2one('product.uom', 'Unit', required = True, digits=(16,2)),
              'product_qty':fields.float("Quantity", required = True),
              'price_unit':fields.float('Price Unit', required = True, digits_compute=dp.get_precision('Amount')),
              'name':fields.char('Description', required = True, size = 128),
              'location_id':fields.many2one('stock.location', 'Destination', required = True),
              'prepaid_order_id':fields.many2one('kderp.prepaid.purchase.order','Prepaid Order'),
              }    
    
    _defaults = {
                 'product_id': lambda self, cr, uid, context = {}: kderp_base.get_new_value_from_tree(cr, uid, context.get('id',False), self, context.get('prepaid_order_line',[]), 'product_id', context),
                 'product_uom': lambda self, cr, uid, context = {}: kderp_base.get_new_value_from_tree(cr, uid, context.get('id',False), self, context.get('prepaid_order_line',[]), 'product_uom', context),
                 'location_id': lambda self, cr, uid, context = {}: kderp_base.get_new_value_from_tree(cr, uid, context.get('id',False), self, context.get('prepaid_order_line',[]), 'location_id', context),
                 'price_unit': lambda *x: 0.0,
                 }