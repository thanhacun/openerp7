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

class StockMove(osv.osv):
    _inherit = 'stock.move'
    _name="stock.move"

    def _get_qty_inout(self, cr, uid, ids, name, args, context):
        if not context:
            context = {}
        res = {}
        location_ids = context.get('location_ids', False)
        if type(location_ids) == type(1):
            location_ids = [location_ids]
        elif type(location_ids) != type([]):
            location_ids = []
        if not location_ids:
            location_obj = self.pool.get('stock.location')
            location_ids = location_obj.search(cr, uid, [('general_stock','=',True)])
        for sm in self.browse(cr, uid, ids, context):
            #If stock source -> Negative number (In case move negative pls consider later)
            if sm.location_id.id in location_ids:
                res[sm.id] = - sm.product_qty
            else:
                res[sm.id] = sm.product_qty
        return res

    _columns ={
        'qty_inout':fields.function(_get_qty_inout,type='float',string='Qty. In/Out'),
        'purchase_id':fields.related('purchase_line_id','order_id',type='many2one',string='PO. No.',relation='purchase.order'),
        'remarks':fields.char("Remarks", size=128, states={'done': [('readonly', True)]})
    }

    _defaults = {
       'location_id':lambda self, cr, uid, context = {}: context.get('location_id',False) if context else False,
       'location_dest_id':lambda self, cr, uid, context = {}: context.get('location_dest_id',False) if context else False
        }

