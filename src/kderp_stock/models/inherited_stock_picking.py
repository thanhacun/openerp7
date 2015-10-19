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
from openerp import netsvc

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def get_newcode(self, cr, uid, type = 'internal', context = {} ):
        if not context:
            context = {}
        if not type:
            type = context.get('picking_type', 'internal')

        type = 'int' if type == 'internal' else type
        cr.execute("""SELECT
                        replace(prefix,'$',location_code) || to_char(current_date,replace(suffix,'I','"I"')) ||lpad((max(substring(coalesce(sp.name, replace(prefix,'$',location_code) || to_char(current_date,replace(suffix,'I','"I"')) || lpad('0',padding,'0')) from length(replace(prefix,'$',location_code) || to_char(current_date,replace(suffix,'I','"I"')))+1 for padding)::integer) + 1)::text, padding, '0')
                    FROM
                        (select case when location_code = '4' then 'H' else 'S' end as location_code from res_company limit 1) vwcompany
                    left join
                        ir_sequence isq on 1=1
                    left join
                         stock_picking sp on sp.name ilike replace(isq.prefix,'$',location_code) || to_char(current_date,replace(suffix,'I','"I"')) || lpad('_',padding,'_')
                    WHERE
                        isq.code ilike 'kderp_stock_picking_code_%%%s'
                    group by
                        isq.id,
                        location_code""" % type)
        new_code = cr.fetchone()
        return new_code[0] if new_code else False

    #Fuction Get id of view when open Picking In, Out, or Move (internal)
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context:
            context = {}
        picking_id = context.get('picking_id',False)
        if picking_id:
            picking_type = self.read(cr, uid, picking_id, ['type'])['type']
            if picking_type and not view_id:
                views_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','kderp.stock.picking.%s.%s' % (picking_type,view_type))])
                if views_ids:
                    view_id = views_ids[0]
        elif context.get('picking_type', False) and not view_id:
                picking_type = context.get('picking_type', False)
                views_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','kderp.stock.picking.%s.%s' % (picking_type,view_type))])
                if views_ids:
                    view_id = views_ids[0]

        return super(stock_picking, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)

    def create(self, cr, user, vals, context=None):
        if not context:
            context = {}
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('stock.picking').get_newcode(cr, user, context.get('picking_type','internal'), context)
        new_id = super(stock_picking, self).create(cr, user, vals, context)
        return new_id

    def action_cancel_draft(self, cr, uid, ids, context=None):
        """ Revise picking status.
        @return: True
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")

        for pick in self.browse(cr, uid, ids, context=context):
            ids2 = [move.id for move in pick.move_lines]
            self.pool.get('stock.move').action_cancel_draft(cr, uid, ids2, context)
            wf_service.trg_delete(uid, 'stock.picking', pick.id, cr)
            wf_service.trg_create(uid, 'stock.picking', pick.id, cr)
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

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
                'check_payment':fields.many2one('kderp.supplier.payment', 'Supplier Payment'),
                'received_date':fields.date('Received Date'),

                'state':fields.selection(STOCK_PICKING_IN_STATE,'State', readonly=1),

                #Set location required
                'location_id': fields.many2one('stock.location', 'Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Keep empty if you produce at the location where the finished products are needed." \
                                                            "Set a location if you produce at a fixed location. This can be a partner location " \
                                                            "if you subcontract the manufacturing operations.", select=True, required=True),
                'location_dest_id': fields.many2one('stock.location', 'Dest. Location', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="Location where the system will stock the finished products.", select=True, required=True),


                'storekeeper_incharge_id':fields.many2one('hr.employee','Storekeeper In Charge', required=True, readonly=1, states={'draft':[('readonly', False)]}),
                }

    _defaults = {
                'storekeeper_incharge_id': _get_received_by_id,
                'name': lambda self, cr, uid, context ={}: self.pool.get('stock.picking').get_newcode(cr, uid, False, context),
                'type': lambda self, cr, uid, context ={}: 'internal' if not context else context.get('picking_type','internal')
                }

    def update_stock_received(self,cr, uid, ids, *args):
        self.write(cr,uid,ids,{'state':'done'})
        return True

    def update_stock_draft(self,cr, uid, ids, *args):
        self.write(cr,uid,ids,{'state':'draft'})
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        pickings = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        todo = []
        for picking in pickings:
            if picking.purchase_id:
                if not picking.purchase_id.state in ('waiting_for_delivery','waiting_for_payment','done','revising'):
                    raise osv.except_osv("KDERP Warning", """Can't receive this picking because purchase belong not yet approved""")
            for r in picking.move_lines:
                if r.state == 'draft':
                    todo.append(r.id)
        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_confirm(cr, uid, todo, context=context)
        return True