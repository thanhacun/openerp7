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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class kderp_contract_history(osv.osv):
    """History of Amount Contract, Create new history manual with Date, Amount, Currency """
    _name = 'kderp.contract.history'

    def create_history(self, cr, uid, contract_id):
        res = False
        if contract_id:
            ctc_obj = self.pool.get('kderp.contract.client').browse(cr, uid, contract_id)

            import datetime
            for ctcsc in ctc_obj.contract_summary_currency_ids:
                list_history = {'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                                'amount': ctcsc.amount,
                                'tax_amount': ctcsc.tax_amount,
                                'subtotal': ctcsc.subtotal,
                                'name': ctcsc.name.id,
                                # 'tax_id': [[6, False, [tid.id for tid in ctcsc.tax_id]]],
                                'contract_id': contract_id
                                }
                res = self.create(cr, uid, list_history)
        return res

    _order = "date desc"

    _columns = {
                'name':fields.many2one('res.currency','Currency',required = True),
                'contract_id':fields.many2one('kderp.contract.client','Contract',required=True),
                'amount':fields.float('Amount',digits_compute= dp.get_precision('Amount')),
                'tax_amount':fields.float('VAT',digits_compute= dp.get_precision('Amount')),
                'subtotal':fields.float('Total',digits_compute= dp.get_precision('Amount')),
                'date':fields.date('Date')
             }