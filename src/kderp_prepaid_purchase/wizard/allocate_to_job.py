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

import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class kderp_order_allocate_to_job_select(osv.osv_memory):
    _name = "kderp.order.allocate.to.job.select"
    _rec_name = 'prepaid_ref'
    _description = "Allocated Stock Order to Job"
    
    def _get_prepaid_order(self, cr, uid, context):        
        stock_location_id = context.get('location_id', 0)
        cr.execute("""Select distinct origin from stock_location_product_detail where location_id=%s and origin is not null order by origin""" % stock_location_id)
        res = []
        for ppo_no in cr.fetchall():
            code = str(ppo_no[0])
            res.append((code, code))
        return res
    
    _columns = {
                'prepaid_ref':fields.selection(_get_prepaid_order,'Prepaid Ref.', required = True)
                }
    
    def open_stock_allocated(self, cr, uid, ids, context):
        if not context:
            context = context    
        return {
            'type': 'ir.actions.act_window',
            'res_model':'kderp.stock.order.allocate.to.job',
            'name': _('Allocate to Job'),
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }
    
class kderp_stock_move_allocate_to_job_line(osv.TransientModel):

    _name = "kderp.stock.move.allocate.to.job.line"
    _rec_name = 'product_id'
    _columns = {        
        'product_id':fields.many2one('product.product','Product', required = True),
        'product_uom':fields.many2one('product.uom', 'Unit', required = True, digits=(16,2)),
        'product_qty':fields.float("Quantity", required = True),
        'price_unit':fields.float('Price Unit', required = True, readonly = True, digits_compute=dp.get_precision('Amount')),
        'name':fields.char('Description', required = True, size = 128),
        #'location_id':fields.many2one('stock.location', 'Source', required = True, domain = [('usage','=','internal')]),
        'location_dest_id':fields.many2one('stock.location', 'To Stock', required = True, domain = [('usage','=','internal')]),
        'move_code':fields.float('Move Code'),
        'wizard_id' : fields.many2one('kderp.stock.order.allocate.to.job', string="Wizard", ondelete='CASCADE'),
        'account_anlytic_id': fields.many2one('account.analytic.account', 'Job', ondelete='CASCADE'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, name, qty, uom_id, price_unit, context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}
  
        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res
  
        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        
        product = product_product.browse(cr, uid, product_id, context)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
        if not name:
            dummy, name = product_product.name_get(cr, uid, product_id, context,from_obj='pol')[0]
            if product.description_purchase:
                name = product.description_purchase
        res['value'].update({'name': name})
  
        # - set a domain on product_uom
#        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}
  
        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id
  
        res['value'].update({'product_uom': uom_id})
  
        # - determine product_qty and date_planned based on seller info 
        qty = qty or 1.0
        
        if qty:
            res['value'].update({'product_qty': qty})
  
        return res

class kderp_stock_to_order_allocate_to_job(osv.osv_memory):
    _name = "kderp.stock.order.allocate.to.job"
    _rec_name = 'date'
    _description = "Allocated Stock Order to Job"

    _columns = {
        'date': fields.datetime('Date', required=True),
        'stock_location_id':fields.many2one('stock.location', 'From Stock'),
        'location_dest_id':fields.many2one('stock.location', 'To Stock'),
        'description':fields.char('Description', size=128, required = True),
        'partner_id':fields.many2one('res.partner', 'Supplier', ondelete='restrict', required=True),
        'address_id':fields.many2one('res.partner', 'Address', ondelete='restrict', required=True),
        'product_details' : fields.one2many('kderp.stock.move.allocate.to.job.line', 'wizard_id', 'Product Moves'),
        'account_anlytic_id': fields.many2one('account.analytic.account', 'Job', required=True, ondelete='CASCADE'),
    }
    
    def _allocate_line_for(self, cr, uid, pd, context=None):
        pol = {
            'product_id': pd.product_id.id,
            'price_unit':pd.price_unit,
            'product_uom':pd.product_uom.id,
            'product_qty':pd.quantity,
            'name': pd.product_description,
            'product_uom': pd.product_uom.id,
            'move_code': pd.move_code
        }
        return pol
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(kderp_stock_to_order_allocate_to_job, self).default_get(cr, uid, fields, context=context)
        stock_location_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not stock_location_ids or len(stock_location_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.location'), 'Bad context propagation'        
        stock_location_id, = stock_location_ids

        stl = self.pool.get(active_model).browse(cr, uid, stock_location_id, context=context)
        vat_code = False
#         for pd in stl.product_details:
#             if pd.vat_code:
#                 vat_code = pd.vat_code
#                 break
        cr.execute("""Select vat_code from stock_location_product_detail where location_id=%s and coalesce(vat_code,'')<>'' limit 1""" % stock_location_id)
        if cr.rowcount:
            vat_code = cr.fetchone()[0]
             
        if vat_code:
            rp_ids = self.pool.get('res.partner').search(cr, uid, [('vat_code','ilike', vat_code)], limit=1)
            partner_id = rp_ids[0] if rp_ids else False
            if 'partner_id':
                res.update(partner_id=partner_id)
            if 'address_id' and vat_code:
                res.update(address_id=partner_id)
                
        if 'description' in fields:
            res.update(description='Allocated material from stock to Job')        
        if 'stock_location_id' in fields:
            res.update(stock_location_id=stock_location_id)
        if 'product_details' in fields:
            ppo_lines = [self._allocate_line_for(cr, uid, pd, context=context) for pd in stl.product_details if pd.origin == context.get('prepaid_ref','')]
            res.update(product_details=ppo_lines)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res

    def _product_cost_for_average_update(self, cr, uid, move):
        """Returns product cost and currency ID for the given move, suited for re-computing
           the average product cost.

           :return: map of the form::

                {'cost': 123.34,
                 'currency': 42}
        """
        # Currently, the cost on the product form is supposed to be expressed in the currency
        # of the company owning the product. If not set, we fall back to the picking's company,
        # which should work in simple cases.
        product_currency_id = move.product_id.company_id.currency_id and move.product_id.company_id.currency_id.id
        picking_currency_id = move.picking_id.company_id.currency_id and move.picking_id.company_id.currency_id.id
        return {'cost': move.product_id.standard_price,
                'currency': product_currency_id or picking_currency_id or False}

    def _partial_move_for(self, cr, uid, move, context=None):
        partial_move = {
            'product_id' : move.product_id.id,
            'quantity' : move.product_qty if move.state == 'assigned' or move.picking_id.type == 'in' else 0,
            'product_uom' : move.product_uom.id,
            'prodlot_id' : move.prodlot_id.id,
            'move_id' : move.id,
            'location_id' : move.location_id.id,
            'location_dest_id' : move.location_dest_id.id,
            'currency': move.picking_id and move.picking_id.company_id.currency_id.id or False,
        }
        if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
            partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
