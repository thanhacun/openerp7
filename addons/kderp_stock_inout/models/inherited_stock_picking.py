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

from openerp.osv import fields, osv, orm
from openerp import tools

#
# Inherit of picking to add Info to Picking In
#
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def onchange_location(self, cr, uid, ids, loc_id, loc_source):
        res = {}
        if loc_id:
            loc_obj = self.pool.get('stock.location').browse(cr, uid, loc_id)
            rDomain = [('id', '!=', loc_id)]
            if not loc_obj.general_stock: #If Not General Warehouse filter General Stock only
                 rDomain += [('general_stock','=',True)]
            field_domain = 'location_dest_id' if loc_source else 'location_id'
            res =   {'domain':{field_domain:rDomain}}
        return res


    def action_confirm(self, cr, uid, ids, context=None):
        """Inherit method from stock
            Check user click received picking
            Warehouse manager and storekeeper manage destination can click
            @return: action_move from stock
        """
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.type == 'internal':
                ru_obj = self.pool.get('res.users')
                storekeeper_ids = [stu.id for stu in pick.location_id.storekeeper_ids]
                storekeeper_ids.append(pick.location_id.stock_manager_id.id)
                if not ru_obj.has_group(cr, uid, 'kderp_stock.kderp_warehouse_manager') and uid not in storekeeper_ids:
                    raise osv.except_osv("KDERP Warning", "Only Warehouse manager and Storekeepers manage warehouse (%s) can approve" % pick.location_id.name)
        return super(stock_picking, self).action_confirm(cr, uid, ids, context=None)

    def action_move(self, cr, uid, ids, context=None):
        """Inherit method from stock
            Check user click received picking
            Warehouse manager and storekeeper manage destination can click
            @return: action_move from stock
        """
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.type == 'internal':
                ru_obj = self.pool.get('res.users')
                storekeeper_ids = [stu.id for stu in pick.location_dest_id.storekeeper_ids]
                storekeeper_ids.append(pick.location_dest_id.stock_manager_id.id)
                if not ru_obj.has_group(cr, uid, 'kderp_stock.kderp_warehouse_manager') and uid not in storekeeper_ids:
                    raise osv.except_osv("KDERP Warning",
                                         "Only Warehouse manager and Storekeepers manage warehouse (%s) can approve" % pick.location_dest_id.name)
        return super(stock_picking,self).action_move(cr, uid, ids, context=None)