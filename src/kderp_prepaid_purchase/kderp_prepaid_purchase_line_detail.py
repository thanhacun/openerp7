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
    
    def check_access_rights(self, cr, uid, operation, raise_exception=True): # no context on purpose.
        self.pool.get('kderp.link.server').check_server_connection(cr, uid, [], {})                
        return super(kderp_prepaid_purchase_order_line_detail, self).check_access_rights(cr, uid, operation, raise_exception)
    
    _columns={
              'prepaid_order_line_id':fields.many2one('kderp.prepaid.purchase.order.line','Desc.', required = True),
              'prepaid_order_id':fields.related('prepaid_order_line_id', 'prepaid_order_id', string='Prepaid Order', type='many2one', relation='kderp.prepaid.purchase.order'),
              'product_id':fields.related('prepaid_order_line_id', 'product_id', string='Product', type='many2one', relation='product.product'),
              'po_number':fields.char('Order No.', size  = 16),
              'move_description':fields.char('Note', size = 256),
              'allocated_qty':fields.float('Allocated Qty', digit=(16,2)),
              'requesting_qty':fields.float('Requesting Qty', digit=(16,2)),
              'product_uom':fields.char('Unit', size = 6),              
              'date':fields.date('Date'),
              }
        
    def init(self, cr):
        checkView1 = 'vwstock_move_remote'
        cr.execute("""SELECT 1  FROM  information_schema.views where table_name = '%s'""" % checkView1)
        if cr.rowcount:
            from openerp import tools
            vwName = self.__class__.__name__
            tools.drop_view_if_exists(cr, vwName)        
            sqlCommand = """Create or replace view %s as 
                                Select 
                                    ('1' || row_number() over (order by kppol.id)::text)::integer as id,
                                    kppol.id as prepaid_order_line_id,
                                    smo.origin as po_number,
                                    aaa.code as move_description,
                                    case when smo.state = 'confirmed' then 0 else smo.product_qty end as allocated_qty,
                                    case when smo.state = 'confirmed' then smo.product_qty else 0 end as requesting_qty,
                                    pu.name as product_uom,
                                    smo.date
                                from 
                                    kderp_prepaid_purchase_order_line kppol
                                left join
                                    kderp_prepaid_purchase_order kppo on kppol.prepaid_order_id = kppo.id
                                left join
                                    stock_move sm on sm.state in ('done','assigned') and kppol.id = prepaid_purchase_line_id
                                left join
                                    stock_move smo on sm.move_code = smo.source_move_code and smo.state in ('confirmed','done','assigned')
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
                                    case when vsmo.state = 'confirmed' then 0 else vsmo.product_qty end as allocated_qty,
                                    case when vsmo.state = 'confirmed' then vsmo.product_qty else 0 end as requesting_qty,
                                    vsmo.product_uom,
                                    vsmo.date
                                from 
                                    kderp_prepaid_purchase_order_line kppol
                                left join
                                    kderp_prepaid_purchase_order kppo on kppol.prepaid_order_id = kppo.id
                                left join
                                    stock_move sm on sm.state in ('done','assigned') and kppol.id = prepaid_purchase_line_id
                                left join
                                    vwstock_move_remote vsmo on sm.move_code = vsmo.source_move_code
                                where
                                    coalesce(vsmo.product_qty,0)>0""" % vwName
            cr.execute(sqlCommand)