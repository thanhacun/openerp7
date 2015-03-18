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

class kderp_prepaid_purchase_order_line_detail(osv.osv):
    _auto = False
    _name = 'kderp.prepaid.purchase.order.line.detail'
    _description = 'kderp.prepaid.purchase.order.line.detail'    

    _columns={
              'prepaid_order_line_id':fields.many2one('kderp.prepaid.purchase.order.line','Desc.', required = True),
              'prepaid_order_id':fields.related('prepaid_order_line_id', 'prepaid_order_id', string='Prepaid Order', type='many2one', relation='kderp.prepaid.purchase.order'),
              'product_id':fields.related('prepaid_order_line_id', 'product_id', string='Product', type='many2one', relation='product.product'),
              'po_number':fields.char('Order No.', size  = 16),
              'move_description':fields.char('Note', size = 256),
              'allocated_qty':fields.float('Allocated Qty', digit=(16,2)),
              'product_uom':fields.char('Unit', size = 6),              
              'date':fields.date('Date')
              }
        
    def init(self, cr):
        from openerp import tools
        vwName = self.__class__.__name__
        tools.drop_view_if_exists(cr, vwName)        
        sqlCommand = """Create or replace view %s as 
                            Select 
                                ('1' || row_number() over (order by kppol.id)::text)::integer as id,                                
                                kppol.id as prepaid_order_line_id,
                                smo.origin as po_number,
                                aaa.code as move_description,
                                smo.product_qty as allocated_qty,
                                pu.name as product_uom,
                                smo.date
                            from 
                                kderp_prepaid_purchase_order_line kppol
                            left join
                                kderp_prepaid_purchase_order kppo on kppol.prepaid_order_id = kppo.id
                            left join
                                stock_move sm on kppo.name = sm.origin and sm.state='done' and kppol.product_id = sm.product_id
                            left join
                                stock_move smo on sm.move_code = smo.source_move_code and smo.state='done'
                            left join
                                purchase_order_line pol on smo.purchase_line_id = pol.id
                            left join
                                product_uom pu on smo.product_uom = pu.id
                            left join
                                account_analytic_account aaa on pol.account_analytic_id = aaa.id
                            where
                                coalesce(smo.id,0)>0
                            union all
                            Select 
                                ('2' || row_number() over (order by kppol.id)::text)::integer as id,
                                kppol.id as prepaid_order_line_id,
                                vsmo.origin as po_number,
                                move_description,
                                vsmo.product_qty as allocated_qty,
                                vsmo.product_uom,
                                vsmo.date
                            from 
                                kderp_prepaid_purchase_order_line kppol
                            left join
                                kderp_prepaid_purchase_order kppo on kppol.prepaid_order_id = kppo.id
                            left join
                                stock_move sm on kppo.name = sm.origin and sm.state='done' and kppol.product_id = sm.product_id
                            left join
                                vwstock_move_remote vsmo on sm.move_code = vsmo.source_move_code
                            where
                                coalesce(vsmo.product_qty,0)>0""" % vwName
        cr.execute(sqlCommand)