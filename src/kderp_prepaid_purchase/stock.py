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
from openerp import tools
from bsddb.dbtables import _columns

class stock_location(osv.osv):
    _inherit = 'stock.location'
    _name = 'stock.location'
    _columns = {
                'global_stock':fields.boolean("Global?",help= "Using for HANOI and Ho Chi Minh"),
                'stock_code':fields.char("Stock Code", size=32, help='This code is very important for Global Stock, this code is using for matching stock between two server'),
                'product_details':fields.one2many('stock.location.product.detail','location_id','Details', readonly = 1)
                }
        
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns = {
        'prepaid_purchase_order_id': fields.many2one('kderp.prepaid.purchase.order', 'Purchase Order',
            ondelete='restrict', select=True),
    }

    _defaults = {
        'prepaid_purchase_order_id': False,
    }
    
class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    SELECTION_STATE = [('doing','Doing'),                       
                       ('done','Done')]
    
    
    def _get_move_from_company(self, cr, uid, ids, context=None):
        res=[]
        cr.execute('select id from stock_move where prepaid_purchase_line_id is not null and company_id is not null')
        for id in cr.fetchall():
            res.append(id[0])
        return res
    
    def _get_movecode(self, cr, uid, ids, name, args, context):
        res = {}
        for sm in self.browse(cr, uid, ids):
            if sm.prepaid_purchase_line_id:
                res[sm.id] = int(sm.company_id.location_code + str(sm.id).zfill(9))
            else:
                res[sm.id] = False
        return res
    
    _columns = {
        'prepaid_purchase_line_id': fields.many2one('kderp.prepaid.purchase.order.line',
                                                    'Prepaid Purchase Order Line', ondelete='restrict', select=True),
        'global_state':fields.selection(SELECTION_STATE, 'Global State', readonly = True, help='Using for Global Stock only', select = 1),
        'source_move_code':fields.float('Source Move Code', select = 1, digits=(10,0)),
        'move_code':fields.function(_get_movecode, type='float',  method = True,select = 1, digits=(10,0),
                                                store={
                                                     'stock.move':(lambda self, cr, uid, ids, c={}: ids, ['id','prepaid_purchase_line_id'],50),
                                                     'res.company':(_get_move_from_company,['location_code'],50)
                                                      }),
    }
    
    _defaults ={
                'global_state':'doing'
                }
    
    def init1(self, cr):
        cr.execute("""ALTER TABLE stock_move ALTER COLUMN move_code TYPE bigint;
                      ALTER TABLE stock_move ALTER COLUMN source_move_code TYPE bigint""")
        
    def _check_product_id(self, cr, uid, ids, context=None):
        """
            Kiem tra product id and purchase_line_id
        """
        if not context:
            context={}
        for sm in self.browse(cr, uid, ids, context=context):
            res = True
            if sm.product_id:
                if sm.purchase_line_id and sm.prepaid_purchase_line_id:
                    res = False
                elif sm.purchase_line_id:            
                    if sm.purchase_line_id.product_id.id !=  sm.product_id.id:
                        res = False
                elif sm.prepaid_purchase_line_id:
                    if sm.prepaid_purchase_line_id.product_id.id !=  sm.product_id.id:
                        res = False
        return res
    
    _constraints = [(_check_product_id, 'KDERP Warning, Please Product and Purchase Line', ['purchase_line_id','product_id'])]

stock_move()

class stock_location_product_detail(osv.osv):
    _auto = False
    _name = 'stock.location.product.detail'
    _description = 'List of product Available in Stock'
    
    _columns  = {
                 'location_id':fields.many2one('stock.location', 'Stock'),
                 'product_id':fields.many2one('product.product', 'Product'),
                 'product_uom':fields.many2one('product.uom', 'Uom'),
                 'price_unit':fields.float('Price Unit', digits=(16,2)),
                 'quantity':fields.float('Qty.', digits=(16,2)),
                 'allocated_qty':fields.float('Allocated Qty.', digits=(16,2)),
                 'available_qty':fields.float('Available Qty.', digits=(16,2)),
                 'move_code':fields.char('Move Code', size=12),            
                 'origin':fields.char('Origin', size=64)
                 }
    
    def init(self,cr):
        vwName = 'stock_location_product_detail'
        checkView1 = 'vwstock_move_remote'
        cr.execute("""SELECT 1  FROM   information_schema.views where table_name = '%s'""" % checkView1)
        if cr.rowcount:        
            tools.drop_view_if_exists(cr, vwName)
            cr.execute("""
                        Create or replace view %s as 
                            ---***********STOCK IN ***************************
                            Select
                                row_number() over (order by location_id,product_id) as id,
                                *
                            from
                                (--Stock In Local
                                Select 
                                    sl.id as location_id,
                                    smi.product_id,
                                    smi.product_qty as quantity,
                                    sum(coalesce(smo.product_qty,0)) as allocated_qty,
                                    smi.product_qty - sum(coalesce(smo.product_qty,0)) as available_qty,
                                    smi.price_unit,
                                    smi.product_uom,
                                    smi.move_code,    
                                    smi.origin    
                                from
                                    stock_location sl
                                left join
                                    stock_move smi on sl.id = smi.location_dest_id and state = 'done' and smi.global_state <> 'done'
                                left join
                                    stock_move smo on smi.move_code = smo.source_move_code and sl.id != smo.location_dest_id and smi.product_uom = smo.product_uom
                                where
                                    smi.move_code is not null
                                group by
                                    sl.id,
                                    smi.product_id,
                                    smi.product_qty,
                                    smi.price_unit,
                                    smi.product_uom,
                                    smi.move_code,    
                                    smi.origin
                                Union
                                --Stock In Remote @ from View
                                Select 
                                    sl.id as location_id,
                                    pp.id as product_id,
                                    smi.product_qty as quantity,
                                    sum(coalesce(smo.product_qty,0)) as allocated_qty,
                                    smi.product_qty - sum(coalesce(smo.product_qty,0)) as available_qty,
                                    smi.price_unit,
                                    pu.id as product_uom,
                                    smi.move_code,
                                    smi.origin
                                from
                                    stock_location sl
                                left join
                                    vwstock_move_remote smi on sl.stock_code = stock_destination and global_state <> 'done'
                                left join
                                    product_product pp on product_code = pp.default_code
                                left join
                                    product_uom pu on product_uom = pu.name
                                left join
                                    vwstock_move_remote smo on smi.move_code = smo.source_move_code and coalesce(sl.stock_code,'') != coalesce(smo.stock_destination,'') and smi.product_uom = smo.product_uom
                                where
                                    smi.move_code is not null
                                Group by
                                    sl.id,
                                    pp.id,
                                    smi.product_qty,
                                    smi.price_unit,
                                    pu.id,
                                    smi.move_code,
                                    smi.origin
                               ) vwstockinout""" % vwName)