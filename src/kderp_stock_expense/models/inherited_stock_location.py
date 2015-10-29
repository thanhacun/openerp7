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

from openerp.osv import fields, osv as models


class StockLocation(models.Model):
    """
        Inherit stock location, customize for Kinden Vietnam
    """
    _inherit = 'stock.location'
    _name = 'stock.location'

    def _get_products_list(self, cr, uid, ids, name, args, context = {}):
        """ Return product using for stock in current period
        """
        res = {}
        pp_obj = self.pool.get('product.product')
        for location_id in ids:
            pr_ids = pp_obj.find_product_in_period(cr, uid, location_id, context)
            res[location_id] = pr_ids
        return res

    # Fields declaration
    _columns = {
                'product_ids':fields.function(_get_products_list,type='one2many',relation='product.product',string="Products")
                }