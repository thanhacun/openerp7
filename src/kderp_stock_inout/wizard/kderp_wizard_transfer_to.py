# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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

from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _


class kderp_wizard_transfer_to(osv.osv_memory):
    """
        Move products from Packing to
    """
    _name = "kderp.wizard.transfer.to"

    _columns = {
        'picking_id':fields.many2one('stock.picking','Picking'),
        'location_id':fields.many2one('stock.location','From Stock',readonly=1),
        'location_dest_id':fields.many2one('stock.location', 'To Stock',required = 1),
        'move_line':fields.one2many('kderp.wizard.move.line','wizard_transfer_id',"Details")
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(kderp_wizard_transfer_to, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking', 'stock.picking.in', 'stock.picking.out'), 'Bad context propagation'
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'location_id' in fields:
            location_dest_id = context.get('location_dest_id', False)
            res.update(location_id=location_dest_id)
        if 'move_line' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
            context['filter_by_location_id'] = context.get('location_dest_id', False)
            product_ids = [m.product_id.id for m in picking.move_lines if m.state == 'done' and m.location_dest_id.id==picking.location_dest_id.id]
            search_product = [('id','in', product_ids)]
            products_available_ids = self.pool.get('product.product').search(cr, uid, search_product, context=context)
            moves = [self._partial_move_for(cr, uid, m, context=context) for m in picking.move_lines if m.state == 'done' and m.location_dest_id.id==picking.location_dest_id.id and m.product_id.id in products_available_ids]
            res.update(move_line=moves)

        # if 'date' in fields:
        #     res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        # res['help_text'] = self.__get_help_text(cr, uid, picking_id, context=context)
        return res

    def _partial_move_for(self, cr, uid, move, context=None):
        partial_move = {
            'product_id' : move.product_id.id,
            'qty' : move.product_qty if move.state == 'assigned' or move.picking_id.type == 'in' else 0,
            'product_uom' : move.product_uom.id
            # 'location_id' : move.location_id.id,
            # 'location_dest_id' : move.location_dest_id.id,
        }
        return partial_move

    def do_partial(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor <> 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name =  'stock.picking.' + picking_type
                move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                                                    'product_id': wizard_line.product_id.id,
                                                    'product_qty': wizard_line.quantity,
                                                    'product_uom': wizard_line.product_uom.id,
                                                    'prodlot_id': wizard_line.prodlot_id.id,
                                                    'location_id' : wizard_line.location_id.id,
                                                    'location_dest_id' : wizard_line.location_dest_id.id,
                                                    'picking_id': partial.picking_id.id
                                                    },context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % (move_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
                                                                  product_currency=wizard_line.currency.id)

        # Do the partial delivery and open the picking that was delivered
        # We don't need to find which view is required, stock.picking does it.
        done = stock_picking.do_partial(
            cr, uid, [partial.picking_id.id], partial_data, context=context)
        if done[partial.picking_id.id]['delivered_picking'] == partial.picking_id.id:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.act_window',
            'res_model': context.get('active_model', 'stock.picking'),
            'name': _('Partial Delivery'),
            'res_id': done[partial.picking_id.id]['delivered_picking'],
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'context': context,
        }


    def do_transfer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor <> 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name =  'stock.picking.' + picking_type
                move_id = stock_move.create(cr,uid,{'name' : wizard_line.name,
                                                    'product_id': wizard_line.product_id.id,
                                                    'product_qty': wizard_line.quantity,
                                                    'product_uom': wizard_line.product_uom.id,
                                                    'prodlot_id': wizard_line.prodlot_id.id,
                                                    'location_id' : wizard_line.location_id.id,
                                                    'location_dest_id' : wizard_line.location_dest_id.id,
                                                    'picking_id': partial.picking_id.id
                                                    },context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % (move_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
                                                                  product_currency=wizard_line.currency.id)

        # Do the partial delivery and open the picking that was delivered
        # We don't need to find which view is required, stock.picking does it.
        done = stock_picking.do_partial(
            cr, uid, [partial.picking_id.id], partial_data, context=context)

        if done[partial.picking_id.id]['delivered_picking'] == partial.picking_id.id:
            return {'type': 'ir.actions.act_window_close'}

        return {
            'type': 'ir.actions.act_window',
            'res_model': context.get('active_model', 'stock.picking'),
            'name': _('Partial Delivery'),
            'res_id': done[partial.picking_id.id]['delivered_picking'],
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'context': context,
        }


class kderp_wizard_move_line(osv.osv_memory):
    _name = "kderp.wizard.move.line"

    _rec_name="product_id"
    _columns = {
        'wizard_transfer_id':fields.many2one("kderp.wizard.transfer.to",'Transfer ID', ondelete="CASCADE"),
        'product_id':fields.many2one('product.product','Product', required=1),
        'product_uom':fields.many2one('product.uom','Product UOM', required=1),
        'qty':fields.float('Qty', required=1)
    }