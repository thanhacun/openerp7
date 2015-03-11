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

class stock_location(osv.osv):
    _inherit = 'stock.location'
    _name = 'stock.location'
    _columns = {
                'global_stock':fields.boolean("Global", "Using for HANOI and Ho Chi Minh")
                }
    
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns = {
        'prepaid_purchase_order_id': fields.many2one('kderp.prepaid.purchase.order', 'Purchase Order',
            ondelete='restrict', select=True),
    }

    _defaults = {
        'prepaid_purchase_order_id': False,
    }
    
class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    _columns = {
        'prepaid_purchase_line_id': fields.many2one('kderp.prepaid.purchase.order.line',
            'Prepaid Purchase Order Line', ondelete='restrict', select=True),
    }
    
    def _check_product_id(self, cr, uid, ids, context=None):
        """
            Kiem tra product id and purchase_line_id
        """
        if not context:
            context={}
        for sm in self.browse(cr, uid, ids, context=context):
            res = True
            if sm.product_id:
                if sm.purchase_line_id and sm.prepaid_purchase_line_id:
                    res = False
                elif sm.purchase_line_id:            
                    if sm.purchase_line_id.product_id.id !=  sm.product_id.id:
                        res = False
                elif sm.prepaid_purchase_line_id:
                    if sm.prepaid_purchase_line_id.product_id.id !=  sm.product_id.id:
                        res = False
        return res
    
    _constraints = [(_check_product_id, 'KDERP Warning, Please Product and Purchase Line', ['purchase_line_id','product_id'])]

stock_move()