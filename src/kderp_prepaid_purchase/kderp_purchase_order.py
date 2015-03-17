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
import time
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import netsvc, SUPERUSER_ID

class purchase_order(osv.osv):
    """
        Add new field Purchase Order
    """
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _description = 'KDERP Purchase Order'
     
    _columns={
              'allocate_order':fields.boolean("Allocate Order") 
              }
    
    def action_create_received_picking(self, cr, uid, ids, context = {}):
        picking_id = self.action_picking_create(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state':'done'})
        return picking_id    
    
    #Stock Picking and MoveArea
    def date_to_datetime(self, cr, uid, userdate, context=None):
        """ Convert date values expressed in user's timezone to
        server-side UTC timestamp, assuming a default arbitrary
        time of 12:00 AM - because a time is needed.
    
        :param str userdate: date string in in user time zone
        :return: UTC datetime string for server-side use
        """
        from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
        # TODO: move to fields.datetime in server after 7.0
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATE_FORMAT)
        if context and context.get('tz'):
            tz_name = context['tz']
        else:
            tz_name = self.pool.get('res.users').read(cr, SUPERUSER_ID, uid, ['tz'])['tz']
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date + relativedelta(hours=12.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    
    def _prepare_order_picking(self, cr, uid, order, context=None):
        return {
            'name': self.pool.get('stock.picking').get_newcode(cr, uid, 'int', context),
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'partner_id': order.partner_id.id,
            'invoice_state': 'none', 
            'type': 'in',
            'purchase_order_id': order.id,
            #'company_id': order.company_id.id,
            'move_lines' : [],
        }
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        price_unit = order_line.price_unit
#        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
#            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            #'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order_line.location_id.id,
            'location_dest_id': order_line.location_dest_id.id,
            'picking_id': picking_id,
            'partner_id': order.partner_id.id,
            #'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'type':'in',
            'purchase_id': order_line.id,
            #'company_id': order.company_id.id,
            'price_unit': price_unit,
            'source_move_code':order_line.move_code
        }     
    
    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Creates pickings and appropriate stock moves for given order lines, then
        confirms the moves, makes them available, and confirms the picking.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: purchase order to which the order lines belong
        :param list(browse_record) order_lines: purchase order line records for which picking
                                                and moves should be created.
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if omitted.
        :return: list of IDs of pickings used/created for the given order lines (usually just one)
        """
        if not picking_id:
            picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
        todo_moves = []
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for order_line in order_lines:
            if not order_line.product_id:
                continue
            if order_line.product_id.type in ('product', 'consu'):
                move = stock_move.create(cr, uid, self._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context))
                #if order_line.move_dest_id and order_line.move_dest_id.state != 'done':
                #    order_line.move_dest_id.write({'location_id': order.location_id.id})
                todo_moves.append(move)
        stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves)
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return [picking_id]

    def action_picking_create(self, cr, uid, ids, context=None):
        picking_ids = []
        for order in self.browse(cr, uid, ids):
            picking_ids.extend(self._create_pickings(cr, uid, order, order.order_line, None, context=context))

        # Must return one unique picking ID: the one to connect in the subflow of the purchase order.
        # In case of multiple (split) pickings, we should return the ID of the critical one, i.e. the
        # one that should trigger the advancement of the purchase workflow.
        # By default we will consider the first one as most important, but this behavior can be overridden.
        return picking_ids[0] if picking_ids else False
purchase_order()

class purchase_order_line(osv.osv):
    """
        Add new field link Prepaid Order to Purchase Order Line
    """
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'
    
    _columns = {
                'prepaid_purchase_order_line_id':fields.many2one('kderp.prepaid.purchase.order.line', 'Prepaid Order Line', ondelete='restrict'),
                'move_code':fields.integer('Move Code', readonly = 1),
                'location_id':fields.many2one('stock.location', 'From Stock', readonly = 1),
                'location_dest_id':fields.many2one('stock.location', 'To Stock', readonly = 1),
                }
    