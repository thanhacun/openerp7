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

#
# Inherit of picking to add the link to the PO
#
class stock_picking_in(osv.osv):
    _inherit = ['stock.picking.in','stock.picking']
    _name = 'stock.picking.in'

    PICKING_TYPE = 'in'
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):            
            vals['name'] = self.pool.get('stock.picking').get_newcode(cr, user, 'in', context)
        new_id = super(stock_picking_in, self).create(cr, user, vals, context)
        return new_id

    def _get_received_by_id(self, cr, uid, context={}):
        res_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid),('department_id','=','S1420')])
        return res_ids[0] if res_ids else False
        
    STOCK_PICKING_IN_STATE = [('draft', 'Waiting for ROA'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Waiting for Delivery'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),]

    _columns = {
        'name': fields.char('Packing No.', size=16, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]},required=True),

        'state':fields.selection(STOCK_PICKING_IN_STATE,'State', readonly=1),

        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',states={'done':[('readonly', True)], 'cancel':[('readonly',True)]},
                    ondelete='set null', select=True, required=True),
        'location_id': fields.many2one('stock.location', 'Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Keep empty if you produce at the location where the finished products are needed." \
                                                            "Set a location if you produce at a fixed location. This can be a partner location " \
                                                            "if you subcontract the manufacturing operations.", select=True, required=True),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Location where the system will stock the finished products.", select=True, required=True),
    }

    _defaults = {
                'name': lambda self, cr, uid, context ={}: self.pool.get('stock.picking').get_newcode(cr, uid, self.PICKING_TYPE),
                'received_by_uid': _get_received_by_id,
                'purchase_id': lambda self, cr, uid, context: context.get('order_id', False) or context.get('purchase_id', False),
                }