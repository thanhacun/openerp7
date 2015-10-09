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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
import logging

class product_product(osv.osv):
    """
        Add Qty info to Product
    """
    _inherit = "product.product"
    _name = 'product.product'

    def view_header_get(self, cr, user, view_id, view_type, context=None):
        if context is None:
            context = {}
        res = super(product_product, self).view_header_get(cr, user, view_id, view_type, context)
        if res: return res
        if (context.get('active_id', False)) and (context.get('active_model') == 'stock.location'):
            return _('Products: ')+self.pool.get('stock.location').browse(cr, user, context['active_id'], context).name
        return res

    def get_product_available(self, cr, uid, ids, context=None):
        """ Finds whether product is available or not in particular warehouse.
        @return: Dictionary of values
        """
        if context is None:
            context = {}

        location_obj = self.pool.get('stock.location')
        stock_period_obj = self.pool.get('kderp.stock.period')
        
        states = context.get('states',[])
        what = context.get('what',())
        if not ids:
            ids = self.search(cr, uid, [])
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = location_obj.search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = location_obj.search(cr, uid, [('general_stock','=',True)])
            if not location_ids:
                return res
        #Check if select general stock and job stock
        cr.execute("""Select DISTINCT COALESCE(general_stock, False) from stock_location where id in (%s)""" % ",".join(map(str, location_ids)))
        if cr.rowcount>1:
            raise osv.except_osv("KDERP Warning", "Can't select general stock with job stock !, you can select general stock or Job Stock")
        general_stock_selected = cr.fetchone()[0]

        logger = logging.getLogger(__name__)
        logger.info("Stock Locaiton %s" % location_ids)
            #REmove unsed copy from Original
            #wids = warehouse_obj.search(cr, uid, [], context=context)
            #if not wids:

            #    return res
            #for w in warehouse_obj.browse(cr, uid, wids, context=context):
            #    location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        # import ipdb
        # ipdb.set_trace()
        if context.get('compute_child',True):
            child_location_ids = location_obj.search(cr, uid, [('id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids

        # this will be a dictionary of the product UoM by product id
        product2uom = {}
        uom_ids = []
        for product in self.read(cr, uid, ids, ['uom_id'], context=context):
            product2uom[product['id']] = product['uom_id'][0]
            uom_ids.append(product['uom_id'][0])
        # this will be a dictionary of the UoM resources we need for conversion purposes, by UoM id
        uoms_o = {}
        for uom in self.pool.get('product.uom').browse(cr, uid, uom_ids, context=context):
            uoms_o[uom.id] = uom

        results = []
        results2 = []
        # results3 = [] #In Opening
        # results4 = [] #Out Opening
        import ipdb
        ipdb.set_trace()
        # FIXME: If need using Date with time
        from_date = context.get('from_date',False)
        to_date = context.get('to_date',False) if context.get('to_date',False) else time.strftime("%Y-%m-%d %H:%M:%S")


        # Find nearest period closed
        pre_closed_info = stock_period_obj.find_pre_period_closed(cr, uid, from_date)
        pre_period_closed = pre_closed_info['pre_period_id']
        from_date_opening = pre_closed_info['from_date']

        # Get from_date if not available From Date = (Min Date in stock move else next date of previous closed)
        from_date = from_date_opening if not from_date else from_date

        if general_stock_selected and pre_period_closed:
            # In case for General Stock have Period :)
            if from_date_opening != from_date:
                where_opening_date = "where date >= '%s' and date<'%s'" % (from_date_opening, from_date)
            else:
                where_opening_date = ''
        else:
            # In case for General Stock not have Period :)
            where_opening_date = "where date < '%s' " % from_date

        if where_opening_date and context.get('opening_qty', False) and from_date<>from_date_opening:
            sqlCommand = """
                            Select
                                sum(product_qty), product_id, product_uom
                            FROM
                                stock_move sm
                            %s and location_dest_id in (%s) and product_id in (%s)
                            group by
                                product_id, product_uom
                         """ % (where_opening_date,
                                ",".join(map(str, location_ids)),
                                ",".join(map(str, ids))
                                )

            cr.execute(sqlCommand)
            results = cr.fetchall()
            sqlCommand = """
                            Select
                                sum(product_qty), product_id, product_uom
                            FROM
                                stock_move sm
                            %s and location_id in (%s) and product_id in (%s)
                            group by
                                product_id, product_uom
                         """ % (where_opening_date,
                                ",".join(map(str, location_ids)),
                                ",".join(map(str, ids))
                                )
            cr.execute(sqlCommand)
            results2 = cr.fetchall()

        date_str = False
        date_values = False
        where = [tuple(location_ids),tuple(ids),tuple(states)]
        if from_date and to_date:
            date_str = "date>=%s and date<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))

        # TODO: perhaps merge in one query.
        if 'in' in what:
            # all moves from a location out of the set to a location in the set
            #
            cr.execute("""select
                                    sum(product_qty), product_id, product_uom
                              from stock_move
                              where
                                    location_dest_id IN %s
                                    and product_id IN %s
                                    and state IN %s """  + (date_str and 'and '+ date_str + ' ' or '')  + """ group by product_id,product_uom""", tuple(where))
            results.extend(cr.fetchall())

        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id IN %s '\
                'and product_id  IN %s '\
                'and state in %s ' + (date_str and 'and '+date_str+' ' or '') + ' ' +
                'group by product_id,product_uom',tuple(where))
            results2.extend(cr.fetchall())

        #In Case get Opening Qty lookup on StockPeriodClosed
        if context.get('opening_qty', False) and pre_period_closed:
            product_str_ids = ",".join(map(str, ids))
            location_str_ids = ",".join(map(str, location_ids))
            sqlCommand = """Select
                                sum(product_qty),
                                product_id,
                                product_uom
                            FROM
                                kderp_stock_period_closed
                            where
                                location_id in (%s) and
                                product_id in (%s) and
                                stock_period_id =  %s
                            group by
                                product_id,
                                product_uom""" % (location_str_ids,
                                                  product_str_ids,
                                                  pre_period_closed)
            cr.execute(sqlCommand)
            results.extend(cr.fetchall())

        # Get the missing UoM resources
        uom_obj = self.pool.get('product.uom')
        uoms = map(lambda x: x[2], results) + map(lambda x: x[2], results2)
        if context.get('uom', False):
            uoms += [context['uom']]
        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o
                
        #TOCHECK: before change uom of product, stock move line are in old uom.
        context.update({'raise-exception': False})
        # Count the incoming quantities
        #FROM QTY TO
        for amount, prod_id, prod_uom in results:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                     uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] += amount
        # Count the outgoing quantities
        for amount, prod_id, prod_uom in results2:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                    uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] -= amount
        return res

    def _get_product_availableqty(self, cr, uid,ids, fld_names, args, context):
        res = {}
        for product in self.browse(cr, uid, ids):
            res[product.id] = product.opening_qty + product.in_qty + product.out_qty
        return res

    def _get_product_qty_info(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ @INPUT: location_id, from and to Date in context
            Can't lookup Outgoing, incoming... Please see orignal
        """

        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            if f == 'opening_qty':
                c['opening_qty'] = 1
            if f =='qty_available':
                c.update({ 'states': ('done',), 'what': ('in', 'out'),'opening_qty':1 })

            if f == 'virtual_available':
                c.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out'),'opening_qty':1})

            if f in ('in_qty'):
                c.update({ 'states': ('done',), 'what': ('in', 'internal') })
            if f in ('out_qty'):
                c.update({ 'states': ('done',), 'what': ('out', 'internal') })
            if f == 'incoming_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('in','internal') })
            if f == 'outgoing_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('out','internal') })
            stock = self.get_product_available(cr, uid, ids, context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
        return res

    _columns = {
        'opening_qty': fields.function(_get_product_qty_info, type='float',string = 'Opening Qty.',multi='get_qty_available',select=1),
        'in_qty': fields.function(_get_product_qty_info, type='float', select=1, string = 'In Qty.', multi='get_qty_available'),
        'out_qty': fields.function(_get_product_qty_info,  type='float', string = 'Out Qty.', multi='get_qty_available'),
        'qty_available': fields.function(_get_product_qty_info, multi='get_qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand',
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location with 'internal' type."),
        'virtual_available': fields.function(_get_product_qty_info, multi='get_qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Forecasted Quantity',
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored in this location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        #From Original
        'incoming_qty': fields.function(_get_product_qty_info, multi='get_qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Incoming',
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "arriving to the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location with 'internal' type."),
        'outgoing_qty': fields.function(_get_product_qty_info, multi='get_qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Outgoing',
            help="Quantity of products that are planned to leave.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods leaving this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods leaving the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "leaving the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods leaving any Stock "
                 "Location with 'internal' type."),
    }

    def fields_view_get1(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(product_product,self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if context is None:
            context = {}
        if ('location' in context) and context['location']:
            location_info = self.pool.get('stock.location').browse(cr, uid, context['location'])
            fields=res.get('fields',{})
            if fields:
                if location_info.usage == 'supplier':
                    if fields.get('virtual_available'):
                        res['fields']['virtual_available']['string'] = _('Future Receptions')
                    if fields.get('qty_available'):
                        res['fields']['qty_available']['string'] = _('Received Qty')

                if location_info.usage == 'internal':
                    if fields.get('virtual_available'):
                        res['fields']['virtual_available']['string'] = _('Future Stock')

                if location_info.usage == 'customer':
                    if fields.get('virtual_available'):
                        res['fields']['virtual_available']['string'] = _('Future Deliveries')
                    if fields.get('qty_available'):
                        res['fields']['qty_available']['string'] = _('Delivered Qty')

                if location_info.usage == 'inventory':
                    if fields.get('virtual_available'):
                        res['fields']['virtual_available']['string'] = _('Future P&L')
                    if fields.get('qty_available'):
                        res['fields']['qty_available']['string'] = _('P&L Qty')

                if location_info.usage == 'procurement':
                    if fields.get('virtual_available'):
                        res['fields']['virtual_available']['string'] = _('Future Qty')
                    if fields.get('qty_available'):
                        res['fields']['qty_available']['string'] = _('Unplanned Qty')

                if location_info.usage == 'production':
                    if fields.get('virtual_available'):
                        res['fields']['virtual_available']['string'] = _('Future Productions')
                    if fields.get('qty_available'):
                        res['fields']['qty_available']['string'] = _('Produced Qty')
        return res

product_product()