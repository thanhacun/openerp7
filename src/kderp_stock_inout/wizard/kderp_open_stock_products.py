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

from openerp.osv import fields, osv

class wizard_kderp_open_stock_proudcts(osv.osv_memory):
    """This model is Wizard model, using for select """
    _name = "kderp.open.stock.products"

    _columns = {
        'stock_ids':fields.many2many('stock.location',"kderp_open_stock_open_products",'open_product_id','location_id',string="Stocks",help='Please select Job Stock or General Stock, not allow select Job and General Stock one time'),
        'from_date':fields.date('From Date'),
        'to_date':fields.date('To Date')
    }

    def open_products(self, cr, uid, ids, context):
        #TODO later add domain (only product using for stock) 'domain': "[('id','=',%s)]" % expense_ida

        if not context:
            context = {}
        open_form_data = self.browse(cr, uid, ids[0],context)

        context['tree_view_ref'] = 'kderp_stock_inout.view_kderp_product_for_stock_tree'
        context['from_date'] = open_form_data.from_date
        context['to_date'] = open_form_data.to_date
        import ipdb
        ipdb.set_trace()
        context['location'] = [stock.id for stock in open_form_data.stock_ids]

        return {
                    'type': 'ir.actions.act_window',
                    'name': "Products",
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'context': context,
                    'res_model': 'product.product',
                    'domain': [('default_code','=','10220163')]
                    }