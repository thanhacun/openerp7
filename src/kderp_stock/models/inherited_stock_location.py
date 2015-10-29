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
from openerp.osv import fields, osv as models, expression
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

    def _get_default_belong_location(self, cr, uid, context = {}):
        #WH001-> Hanoi, WH002 -> Hai Phong, WH003 - HCM
        location_dict = {'hanoi': 'W001','haiphong': 'W002', 'hcm': 'W003'}
        location_user = self.pool.get('res.users').browse(cr, uid, uid).location_user
        location_ids = location_dict.get(location_user, False) and self.pool.get('stock.location').search(cr, uid, [('code','=',location_dict.get(location_user, False))])
        return (location_ids and location_ids[0]) or False

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

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if args is None:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('name', operator, name)]
        else:
            domain = [('name', operator, name)]
        ids = self.search(cr, user, expression.AND([domain, args]), limit=limit, context=context) or self.search(cr, user, args+[('code', operator, name)], limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        context = context or {}
        res = []
        for sl in self.browse(cr, uid, ids):
            stock_name = "%s - %s" % (sl.code, sl.name) if 'show_title' not in context else sl.complete_name
            res.append((sl.id,stock_name))
        return res

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        context = context or {}
        if not context.get('show_all', False):
            args += [('state','!=','closed')]
        return super(StockLocation, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def close_warehouse(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'closed'})

    def lock_warehouse(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'locked'})

    def open_warehouse(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state':'open'})

    # Fields declaration
    STOCK_STATES = (('open','Open'),
                    ('locked','Locked'),
                    ('closed','Closed'))
    _columns = {
                'state':fields.selection(STOCK_STATES, 'State', readonly=1, states={'locked':[('readonly', True)], 'closed':[('readonly',True)]}),
                'code':fields.char('Code', required = True, size=8,help=EXPLAIN_WAREHOUSE_NO, states={'locked':[('readonly', True)], 'closed':[('readonly',True)]}),
                'name': fields.char('Warehouse Name', size=64, required=True, translate=False, states={'locked':[('readonly', True)], 'closed':[('readonly',True)]}),
                'complete_name': fields.function(_complete_name, type='char', size=256, string="Location Name",
                                    store={'stock.location': (_get_sublocations, ['name', 'location_id'], 10)}),
                'usage': fields.selection([('supplier', 'Supplier Location'), ('view', 'View'), ('internal', 'Internal Location'), ('customer', 'Customer Location'), ('inventory', 'Inventory'), ('procurement', 'Procurement'), ('production', 'Production'), ('transit', 'Transit Location for Inter-Companies Transfers')], 'Warehouse Type', required=True,states={'locked':[('readonly', True)], 'closed':[('readonly',True)]},
                     help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                           \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                           \n* Internal Location: Physical locations inside your own warehouses,
                           \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                           \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                           \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                           \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                          """, select = True),

                'location_id': fields.many2one('stock.location', 'Belong to Warehouse', select=True, ondelete='restrict', help='Belong to Warehouse',states={'locked':[('readonly', True)], 'closed':[('readonly',True)]}),
                'child_ids': fields.one2many('stock.location', 'location_id', 'Contains'),
                'parent_left': fields.integer('Left Parent', select=1),
                'parent_right': fields.integer('Right Parent', select=1),

                'general_stock':fields.boolean("General Stock?",help="Warehouse using quantity with period", states={'locked':[('readonly', True)], 'closed':[('readonly',True)]}),
                
                'stock_manager_id':fields.many2one('res.users', 'Warehouse Manager', ondelete='restrict', states={'locked':[('readonly', True)], 'closed':[('readonly',True)]}),
                'storekeeper_ids':fields.many2many('res.users', 'storekeeper_user_rel', 'stock_id', 'user_id', ondelete='restrict', states={'locked':[('readonly', True)], 'closed':[('readonly',True)]}),
                'job_related_ids':fields.many2many('account.analytic.account', 'jobs_stock_rel', 'stock_id', 'account_analytic_id', ondelete='restrict',states={'locked':[('readonly', True)], 'closed':[('readonly',True)]})
                }
    _defaults = {
        'code':get_newcode,
        'location_id':_get_default_belong_location,
        'state': 'open'
    }
    _sql_constraints = [("_unique_warehouse_code","unique(code)","KDERP Warning: Warehouse code must be unique")]
    # FIXME: Later remove this init method, this method using for recreate Parent Left, right
    # def init(self, cr):
    #     cr.execute("""Alter table stock_location drop column parent_left;
    #                   Alter table stock_location drop column parent_right;""")