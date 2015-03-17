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
                'default_project_stock':fields.boolean("Default Project Stock"),
                
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
                res[sm.id] = int(sm.company_id.location_code + str(sm.id))
            else:
                res[sm.id] = False
        return res
    
    _columns = {
        'prepaid_purchase_line_id': fields.many2one('kderp.prepaid.purchase.order.line',
                                                    'Prepaid Purchase Order Line', ondelete='restrict', select=True),
        'global_state':fields.selection(SELECTION_STATE, 'Global State', readonly = True, help='Using for Global Stock only', select = 1),
        'source_move_code':fields.integer('Source Move Code', select = 1),
        'move_code':fields.function(_get_movecode, type='integer',  method = True,select = 1,
                                                store={
                                                     'stock.move':(lambda self, cr, uid, ids, c={}: ids, ['id','prepaid_purchase_line_id'],50),
                                                     'res.company':(_get_move_from_company,['location_code'],50)
                                                      }),
    }
    
    _defaults ={
                'global_state':'doing'
                }
    
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
                 'move_code':fields.integer('Move Code'),            
                 'origin':fields.char('Origin', size=64),
                 'vat_code':fields.char('VAT Code', size=32),
                 'product_description':fields.char('Desc.', size=256),
                 }
    
    def init(self,cr):
        vwName = 'stock_location_product_detail'
        checkView1 = 'vwstock_move_remote'
        cr.execute("""SELECT 1  FROM  information_schema.views where table_name = '%s'""" % checkView1)
        if cr.rowcount:        
            tools.drop_view_if_exists(cr, vwName)
            tools.drop_view_if_exists(cr, 'vwcombine_stock_move')
            cr.execute("""Create or replace view vwcombine_stock_move as 
                        Select 
                                sl.id as location_id,
                                sm.product_id,
                                sm.product_qty as quantity,
                                sm.price_unit,
                                sm.product_uom,
                                sm.move_code,
                                sm.source_move_code,
                                sm.origin,
                                rp.vat_code,
                                sm.name as product_description        
                            from
                                stock_location sl
                            left join
                                stock_move sm on (sl.id = sm.location_dest_id or sl.id=sm.location_id) and state = 'done' and sm.global_state <> 'done'
                            left join
                                res_partner rp on sm.partner_id = rp.id
                            where
                                sm.move_code is not null or sm.source_move_code is not null
                            group by
                                sl.id,
                                sm.id,
                                sm.product_qty,
                                sm.price_unit,
                                sm.product_uom,
                                sm.move_code,    
                                sm.origin,
                                rp.vat_code,
                                sm.name
                        Union
                            Select 
                                sl.id as location_id,
                                pp.id as product_id,
                                sm.product_qty as quantity,
                                sm.price_unit,
                                pu.id as product_uom,
                                sm.move_code,
                                sm.source_move_code,
                                sm.origin,
                                sm.vat_code,
                                sm.product_description
                            from
                                stock_location sl
                            left join
                                vwstock_move_remote sm on (sl.stock_code = stock_destination or sl.stock_code = stock_source) and global_state <> 'done'
                            left join
                                product_product pp on product_code = pp.default_code
                            left join
                                product_uom pu on product_uom = pu.name
                            where
                                sm.move_code is not null or sm.source_move_code is not null
                            Group by
                                sl.id,
                                pp.id,
                                sm.product_qty,
                                sm.price_unit,
                                pu.id,
                                sm.move_code,
                                sm.origin,
                                sm.vat_code,
                                sm.product_description,
                                sm.source_move_code
            """)
            cr.execute("""
                        Create or replace view %s as 
                            ---***********STOCK IN ***************************
                            Select
                                row_number() over (order by location_id,product_id) as id,
                                *
                            from
                                (Select 
                                    sl.id as location_id,
                                    smi.product_id,
                                    smi.quantity as quantity,
                                    sum(coalesce(smo.quantity,0)) as allocated_qty,
                                    smi.quantity - sum(coalesce(smo.quantity,0)) as available_qty,
                                    smi.price_unit,
                                    smi.product_uom,
                                    smi.move_code,    
                                    smi.origin,
                                    smi.vat_code,
                                    smi.product_description
                                from
                                    stock_location sl
                                left join
                                    vwcombine_stock_move smi on sl.id = smi.location_id 
                                left join
                                    vwcombine_stock_move smo on smi.move_code = smo.source_move_code and smo.move_code is null and smi.product_uom = smo.product_uom and sl.id = smo.location_id
                                where
                                    smi.move_code is not null
                                group by
                                    sl.id,
                                    smi.product_id,
                                    smi.quantity,
                                    smi.price_unit,
                                    smi.product_uom,
                                    smi.move_code,
                                    smi.origin,
                                    smi.vat_code,
                                    smi.product_description
                               ) vwstockinout""" % vwName)