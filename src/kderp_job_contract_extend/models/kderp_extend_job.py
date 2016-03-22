# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc

class account_analytic_account(osv.osv):
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'
    
    _columns={
                'control_area_id':fields.many2one('kderp.control.area','Control Area', ondelete='restrict'),
                'control_area_percent': fields.float('%'),
                'support_area_id': fields.many2one('kderp.control.area','Support Area', ondelete='restrict'),
                'support_area_percent': fields.float('%'),
              }
account_analytic_account()