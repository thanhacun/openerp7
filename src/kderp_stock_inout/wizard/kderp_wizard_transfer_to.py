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
        'location_dest_id':fields.many2one('stock.location', 'To Stock',required = 1, domain=[('usage','in',('customer','supplier','internal'))]),
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
            context['location_ids'] = [context.get('location_dest_id', False)]
            product_ids = [m.product_id.id for m in picking.move_lines if m.state == 'done' and m.location_dest_id.id==picking.location_dest_id.id]
            search_product = [('id','in', product_ids)]
            pp_obj = self.pool.get('product.product')
            products_available_ids = pp_obj.search(cr, uid, search_product, context=context)
            pp_list = pp_obj.read(cr, uid, products_available_ids, ['qty_available'], context = context)
            pp_dict = {pp['id']: pp['qty_available'] for pp in pp_list if pp['qty_available']>0}

            moves = [self._transfer_move_for(cr, uid, m, context = context, pp_dict = pp_dict) for m in picking.move_lines if m.state == 'done' and m.location_dest_id.id==picking.location_dest_id.id and m.product_id.id in pp_dict]
            res.update(move_line=moves)

        # if 'date' in fields:
        #     res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        # res['help_text'] = self.__get_help_text(cr, uid, picking_id, context=context)
        return res

    def _transfer_move_for(self, cr, uid, move, context = {}, pp_dict = {}):
        product_id = move.product_id.id
        #FIX ME: If using many product uom (convert product UOM)
        qty = move.product_qty if pp_dict[product_id] >= move.product_qty else pp_dict[product_id]
        transfer_move = {
            'product_id' : product_id,
            'qty' : qty,
            'product_uom' : move.product_uom.id,
            'remarks': move.remarks,
            'location_id' : move.location_dest_id.id
        }
        return transfer_move

    def do_transfer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        assert len(ids) == 1, 'Transfer packing processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        transfer = self.browse(cr, uid, ids[0], context=context)
        if transfer.location_id.id == transfer.location_dest_id.id:
            raise osv.except_osv("KDERP Warning",'Please check Destination Warehouse, Source and destination Warehouse must be different')
        picking_dict = {'customer-internal':'in',
                        'supplier-internal':'in',
                        'internal-internal':'internal',
                        'internal-supplier':'out',
                        'internal-customer':'out'}
        import time
        picking_type = picking_dict[transfer.location_id.usage + "-" +  transfer.location_dest_id.usage]

        transfer_data = {'date': time.strftime("%Y-%m-%d"),
                         'type':picking_type,
                         'location_id':transfer.location_id.id,
                         'location_dest_id':transfer.location_dest_id.id
                         }
        ctx['picking_type'] = picking_type

        for wizard_line in transfer.move_line:
            location_dest_id = (wizard_line.location_dest_id and wizard_line.location_dest_id.id) or transfer.location_dest_id.id
            location_id = wizard_line.location_id.id
            if location_dest_id==location_id:
                raise osv.except_osv("KDERP Warning",'Please check Destination Warehouse, Source and destination Warehouse must be different')

            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            #Quantiny must be Positive
            if wizard_line.quantity <= 0:
                raise osv.except_osv(_('KDERP Warning!'), _('Please provide proper Quantity.'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            # qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)
            #
            # if line_uom.factor and line_uom.factor <> 0:
            #     if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
            #         raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))

            #Check rounding Quantity.ex.
            #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
            #partial delivery: 253g
            #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
            # initial_uom = wizard_line.move_id.product_uom
            # #Compute the quantity for respective wizard_line in the initial uom
            # qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
            # without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
            # if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
            #     raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))

        return {
            'type': 'ir.actions.act_window',
            'res_model': context.get('active_model', 'stock.picking'),
            'name': _('Stock Move'),
            'res_id': transfer.id,
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'context': context,
        }


class kderp_wizard_move_line(osv.osv_memory):
    _name = "kderp.wizard.move.line"

    _rec_name="product_id"
    _columns = {
        'wizard_transfer_id':fields.many2one("kderp.wizard.transfer.to",'Transfer ID', ondelete="CASCADE"),
        'location_id':fields.many2one('stock.location', 'Source Warehouse', required = 1),
        'location_dest_id':fields.many2one('stock.location', 'Dest. Warehouse', domain=[('usage','!=','view')]),
        'product_id':fields.many2one('product.product','Product', required=1),
        'product_uom':fields.many2one('product.uom','Product UOM', required=1),
        'remarks':fields.char('Remarks',size=256),
        'qty':fields.float('Qty', required=1),
    }