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

class kderp_prepaid_purchase_line(osv.osv):
    _name = 'kderp.prepaid.purchase.order.line'
    _description = 'kderp.prepaid.purchase.order.line'
    
    _columns={
              'product_id':fields.many2one('product.product','Product', required = True),
              'product_uom':fields.many2one('product.uom', 'Unit', required = True),
              'price_unit':fields.float('Price Unit', required = True),
              'name':fields.char('Description', required = True, size = 128),
              'location_id':fields.many2one('stock.location', 'Destination', required = True),
              'prepaid_order_id':fields.many2one('kderp.prepaid.purchase.order','Prepaid Order'),
              }    
    
    _defaults = {
                 #'product_id': lambda self, cr, uid, context = {}: kderp_base.get_new_value_from_tree(cr, uid, context.get('id',False), self, context.get('prepaid_order_line',[]), 'product_id', context),
                 #'product_uom': lambda self, cr, uid, context = {}: kderp_base.get_new_value_from_tree(cr, uid, context.get('id',False), self, context.get('prepaid_order_line',[]), 'product_uom', context),
                # 'location_id': lambda self, cr, uid, context = {}: kderp_base.get_new_value_from_tree(cr, uid, context.get('id',False), self, context.get('prepaid_order_line',[]), 'location_id', context),
                 #'price_unit': lambda *x: 0.0,
                 }