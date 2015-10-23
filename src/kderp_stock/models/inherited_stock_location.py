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

# 1 : imports of python lib
# 2 :  imports of openerp
import openerp
from openerp.osv import fields, osv as models
from openerp.tools.translate import _

EXPLAIN_WAREHOUSE_NO = _("""Warehouse Number:
                            W(L)XXXX,
                            W: Warehouse,
                            (L) Location H: Hanoi, P: Hai Phong, S: Ho Chi Minh,
                            XXXX is increase number with four number """)

class StockLocation(models.Model):
    """
        Inherit stock location, customize for Kinden Vietnam
    """
    _inherit = 'stock.location'
    _name = 'stock.location'

    #Get new code for Warehouser
    def get_newcode(self, cr, uid, context = {} ):
        """() -> NEw code string """
        if not context:
            context = {}

        # Please consider later when location user global (location code)
        cr.execute("""SELECT
                        replace(prefix,'$',location_code) || lpad((max(substring(coalesce(sp.code, replace(prefix,'$',location_code) || lpad('0',padding,'0')) from length(replace(prefix,'$',location_code))+1 for padding)::integer) + 1)::text, padding, '0')
                    FROM
                        (select
                                case when location_user = 'hcm' then 'S' else
                                    case when location_user = 'haiphong' then 'P' else 'H' end end as location_code from res_users ru where ru.id = %d ) vwcompany
                    left join
                        ir_sequence isq on 1=1
                    left join
                         stock_location sp on sp.code ilike replace(isq.prefix,'$',location_code) || lpad('_',padding,'_')
                    WHERE
                        isq.code = 'kderp_stock_warehouse_code'
                    group by
                        isq.id,
                        location_code""" % (uid))
        new_code = cr.fetchone()
        return new_code[0] if new_code else False

    #Copy from Original module
    def _complete_name(self, cr, uid, ids, name, args, context=None):
        """ Forms complete name of location from parent location to child location.
        @return: Dictionary of values
        """
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            names = [m.name]
            parent = m.location_id
            while parent:
                names.append(parent.name)
                parent = parent.location_id
            res[m.id] = ' / '.join(reversed(names))
        return res

    def _get_sublocations(self, cr, uid, ids, context=None):
        """ return all sublocations of the given stock locations (included) """
        return self.search(cr, uid, [('id', 'child_of', ids)], context=context)

    def name_get(self, cr, uid, ids, context=None):
        context = context or {}
        res = []
        for sl in self.browse(cr, uid, ids):
            stock_name = "%s - %s" % (sl.code, sl.name) if 'show_title' not in context else sl.complete_name
            res.append((sl.id,stock_name))
        return res

    # Fields declaration
    _columns = {
                'code':fields.char('Code', required = True, size=8,help=EXPLAIN_WAREHOUSE_NO),
                'name': fields.char('Warehouse Name', size=64, required=True, translate=True),
                'complete_name': fields.function(_complete_name, type='char', size=256, string="Location Name",
                                    store={'stock.location': (_get_sublocations, ['name', 'location_id'], 10)}),
                'usage': fields.selection([('supplier', 'Supplier Location'), ('view', 'View'), ('internal', 'Internal Location'), ('customer', 'Customer Location'), ('inventory', 'Inventory'), ('procurement', 'Procurement'), ('production', 'Production'), ('transit', 'Transit Location for Inter-Companies Transfers')], 'Warehouse Type', required=True,
                     help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                           \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                           \n* Internal Location: Physical locations inside your own warehouses,
                           \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                           \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                           \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                           \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                          """, select = True),

                'location_id': fields.many2one('stock.location', 'Belong to Warehouse', select=True, ondelete='cascade'),
                'child_ids': fields.one2many('stock.location', 'location_id', 'Contains'),
                'parent_left': fields.integer('Left Parent', select=1),
                'parent_right': fields.integer('Right Parent', select=1),

                'general_stock':fields.boolean("General Stock?",help="Warehouse using quantity with period"),
                
                'stock_manager_id':fields.many2one('res.users', 'Warehouse Manager', ondelete='restrict'),
                'storekeeper_ids':fields.many2many('res.users', 'storekeeper_user_rel', 'stock_id', 'user_id', ondelete='restrict'),
                'job_related_ids':fields.many2many('account.analytic.account', 'jobs_stock_rel', 'stock_id', 'account_analytic_id', ondelete='restrict')
                }
    _defaults = {
        'code':get_newcode
    }
    _sql_constraints = [("_unique_warehouse_code","unique(code)","KDERP Warning: Warehouse code must be unique")]
    # FIXME: Later remove this init method, this method using for recreate Parent Left, right
    # def init(self, cr):
    #     cr.execute("""Alter table stock_location drop column parent_left;
    #                   Alter table stock_location drop column parent_right;""")