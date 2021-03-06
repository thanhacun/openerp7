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


import jasper_reports

from openerp import pooler

def kderp_summary_cable_talking_from_stock(cr, uid, ids, data, context):
    if not context:
        context={}
    #Check if print from Purchase find Job IDs in Purchase
    if context.get('active_model','')=='kderp.prepaid.purchase.order':        
        ids = pooler.get_pool(cr.dbname).get('kderp.prepaid.purchase.order.line.detail').search(cr, uid, [('prepaid_order_id','in',ids)])
    return {'ids': ids,                        
            }
jasper_reports.report_jasper(
   'report.kderp.summary.of.cable.quantity.talking.from.storage.xls',
   'kderp.prepaid.purchase.order.line.detail',
   parser = kderp_summary_cable_talking_from_stock
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
