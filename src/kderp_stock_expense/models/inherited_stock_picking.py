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

from openerp.osv import fields, osv, orm

#
# Inherit of picking to add Info to Picking In
#
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def action_confirm(self, cr, uid, ids, context=None):
        """Inherit method from Stock Inout
            Create PO Internal when transfer product between internal stock
            @return: action_confirm from stock inout
        """
        res = super(stock_picking, self).action_confirm(cr, uid, ids, context=None)
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.type == 'internal':
                context = context or {}
                job_out_id = pick.location_id.account_analytic_id.id if pick.location_id.account_analytic_id else False
                job_in_id = pick.location_dest_id.account_analytic_id.id if pick.location_dest_id.account_analytic_id else False
                kme_obj = self.pool.get('kderp.moving.expense')
                if (job_in_id or job_out_id):
                    import time
                    kme_dict = {'date_order': time.strftime('%Y-%m-%d')}
                    kme_dict['allocate_order'] = True
                    kme_dict['from_job_id'] = job_out_id
                    kme_dict['to_job_id'] = job_in_id
                    kme_dict['name'] = "Moving expense"
                    kmel_dict = {}
                    for sm in pick.move_lines:
                        budget_id = sm.product_id.budget_id.id
                        if not kmel_dict.get(budget_id, {}):
                            kmel_dict[budget_id] = {'budget_id': sm.product_id.budget_id.id,
                                                'amount': sm.product_qty * sm.price_unit,
                                                'move_ids': [(6,0, [sm.id])]
                                                }
                        else:
                            kmel_dict[budget_id]['amount'] += sm.product_qty * sm.price_unit
                            kmel_dict[budget_id]['move_ids'][0][2].append(sm.id)
                    kme_dict['detail_ids'] = [(0, False, kmel_dict[budget_id]) for budget_id in kmel_dict.keys()]
                    new_kme_id = kme_obj.create(cr, uid, kme_dict)
                    # kme_obj.write(cr, uid, [new_kme_id], {'state': 'done'})
        return res