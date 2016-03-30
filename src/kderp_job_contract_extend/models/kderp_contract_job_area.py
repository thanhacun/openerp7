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
from openerp import tools
from kderp_extend_job import CONTROL_TYPE_SELECTION

import openerp.addons.decimal_precision as dp

class kderp_contract_job_area(osv.osv):
    _auto = False
    _name = 'kderp.contract.job.area'
    _description = 'KDERP Contract & Job Area Percentage'

    _rec_name = "job_id"

    _columns={
                'contract_id':fields.many2one('kderp.contract.client','Contract', required=True, ondelete="restrict"),
                'job_id': fields.many2one('account.analytic.account', 'Job', required=True, ondelete="restrict"),
                'area_id': fields.many2one('kderp.control.area', 'Area', required=True, ondelete="restrict"),
                'currency_id': fields.many2one('res.currency', 'Cur.', required=True, ondelete="restrict"),
                'control_support':fields.selection(CONTROL_TYPE_SELECTION, 'Type', required=True),
                'area_per':fields.float("%", required=True),
                'amount':fields.float("Amount", required=True, digits_compute= dp.get_precision('Amount'))
              }

    def init(self, cr):
        vwName = self.__class__.__name__
        tools.drop_view_if_exists(cr, vwName)
        cr.execute("""Create or replace view %s as Select
                        row_number() Over (order by contract_id, account_analytic_id, currency_id, currency_id, area_id, control_support) as id,
                        contract_id,
                        account_analytic_id as job_id,
                        area_id,
                        currency_id,
                        amount_currency*area_per/100.0 as amount,
                        control_support,
                        area_per
                    from
                        kderp_quotation_contract_project_line kcqpl
                    left join
                        kderp_job_control_area kjca on account_analytic_id = job_id
                    where
                        COALESCE(area_id,0)>0
                    order by
                      contract_id,account_analytic_id,control_support,area_id,area_per""" % vwName)

class kderp_contract_client(osv.osv):
    _inherit = 'kderp.contract.client'
    _name = 'kderp.contract.client'

    _columns = {
                'contract_job_area_ids':fields.one2many('kderp.contract.job.area','contract_id','Job Area', readonly=True)
    }