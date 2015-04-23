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


class StockLocation(models.Model):
    """
        Inherit stock location, customize for Kinden Vietnam
    """
    _inherit = 'stock.location'
    _name = 'stock.location'
    
    # Fields declaration
    _columns = {
                'stock_manager_id':fields.many2one('res.users', 'Stock Manager', ondelete='restrict'),
                'storekeeper_ids':fields.many2many('res.users', 'storekeeper_user_rel', 'stock_id', 'user_id', ondelete='restrict'),
                'job_related_ids':fields.many2many('account.analytic.account', 'jobs_stock_rel', 'stock_id', 'account_analytic_id', ondelete='restrict'),
                }