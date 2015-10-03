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
from openerp import netsvc


import time
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _name="stock.move"

    _defaults = {
       'location_id':lambda self, cr, uid, context = {}: context.get('location_id',False) if context else False,
       'location_dest_id':lambda self, cr, uid, context = {}: context.get('location_dest_id',False) if context else False
   }
