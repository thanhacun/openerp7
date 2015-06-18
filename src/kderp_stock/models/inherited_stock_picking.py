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
from json.decoder import _CONSTANTS

#
# Inherit of picking to add the link to the PO
#

class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):            
            vals['name'] = self.pool.get('stock.picking').get_newcode(cr, user, 'int', context)
        new_id = super(stock_picking_in, self).create(cr, user, vals, context)
        return new_id
    
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def init(self,cr):
        #cr.execute("""Update wkf set on_create=False where on_create=True and osv='stock.picking';""")
        pass
    
    def get_newcode(self, cr, uid, type = 'internal', context = {} ):
        if not context:
            context = {}
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
        
    def update_stock_received(self,cr, uid, ids, *args):
        self.write(cr,uid,ids,{'state':'done'})
        return True    
    
    _columns = {
        'check_payment':fields.many2one('kderp.supplier.payment', 'Supplier Payment'),
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',
            ondelete='set null', select=True, required=True),
        'received_date':fields.date('Received Date'),
    }

    _defaults = {
                 'purchase_id': lambda self, cr, uid, context: context.get('order_id', False),
                }