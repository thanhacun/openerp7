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

from openerp.osv import fields, osv
from json.decoder import _CONSTANTS

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    _columns = {
        #'product_id': fields.related('purchase_line_id','product_id', select=True, type="many2one", relation="product.product", string="Product",store=True),
                
        'purchase_line_id': fields.many2one('purchase.order.line',
            'Purchase Order Line', ondelete='restrict', select=True),
        'name': fields.char('Description', select=True),
        'date': fields.datetime('Date', select=True, help="Move date: scheduled date until move is done, then date of actual move processing", states={'done': [('readonly', True)]}),
        'date_expected': fields.datetime('Scheduled Date', states={'done': [('readonly', True)]}, select=True, help="Scheduled date for the processing of this move"),
        'location_id': fields.many2one('stock.location', 'Source Location', select=True,states={'done': [('readonly', True)]}),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location',states={'done': [('readonly', True)]}, ),
    }
    def _check_product_id(self, cr, uid, ids, context=None):
        """
            Kiem tra product id and purchase_line_id
        """
        if not context:
            context={}
        for sm in self.browse(cr, uid, ids, context=context):
            if sm.purchase_line_id and sm.product_id:
                if sm.purchase_line_id.product_id.id !=  sm.product_id.id:
                    return False
        return True
    
    _constraints = [(_check_product_id, 'KDERP Warning, Please Product and Purchase Line', ['purchase_line_id','product_id'])]
    
    def purchase_order_line_change(self, cr, uid, ids, order_line_id):        
        if not order_line_id:
            return {'value': {
                              'product_uos':False,
                              'product_id':False,
                              'product_uom':False}}
       
        for pol in self.pool.get('purchase.order.line').browse(cr,uid,[order_line_id]):
            if pol.product_id: 
                product_id = pol.product_id.id
            else:
                product_id=False
            prod_uom_po = pol.product_uom.id
            result={'value':{
            'product_id': product_id,
            'product_uom': prod_uom_po
            }}
        return result
stock_move()