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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class account_analytic_account(osv.osv):
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    JOB_SCALE_SELECTION = [('big_job','Big Job'), ('small_maintenance', 'Small/Maintenance Job'), ('f-cost','F-Cost Job')]
    def _get_job_scale(self, cr, uid, ids, name, args, context = {}):
        res = {}
        for job in self.browse(cr, uid, ids):
            jobCode = job.code.upper()
            if jobCode[1:2] == 'A' or len(jobCode)<9: #Trong truong hop Job la HA hoac Code ko dung dinh dang
                res[job.id] = False
            elif len(jobCode)>10 and jobCode[10:11] == 'F':
                res[job.id] = 'f-cost'
            elif jobCode[4:6] == '-0':
                res[job.id] = 'big_job'
            elif jobCode[4:6] in ('-1','-2'):
                res[job.id] = 'small_maintenance'
        return res

    _columns={
                # 'control_area_id':fields.many2one('kderp.control.area','Control Area', ondelete='restrict'),

                # 'support_area_id': fields.many2one('kderp.control.area','Support Area', ondelete='restrict'),

                #'target_profit': fields.float('Target Profit', digits_compute=dp.get_precision('Amount')),
                'target_profit': fields.char('Target Profit', size=6),
                'kickoff_meeting_date': fields.date('K.O.M. Date', help="Kick-off meeting Date"),

                # FIXME Truong nay se co ten la Job Type, Job Type doi thanh E/M, phai hop nhat khi Upgrade len Odoo
                'job_scale':fields.function(_get_job_scale, type = 'selection', string = 'Job Type', selection = JOB_SCALE_SELECTION, method = True, select = 1,
                                            store = {'account.analytic.account':(lambda self, cr, uid, ids, context = {}: ids, ['code'], 50),}),

                'control_area_ids':fields.one2many('kderp.job.control.area', 'job_id', 'Control Area'),
                'area_allotment_ids': fields.one2many('kderp.job.area.allotment', 'job_id', 'Area Allotment', readonly=1)
              }

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        context = context or {}
        if context.get("filter_by_contract_id", False):
            contract_id = context.get("filter_by_contract_id", False)
            sqlConn = """Select DISTINCT account_analytic_id from kderp_quotation_contract_project_line kqcpl where contract_id=%s""" % contract_id
            cr.execute(sqlConn)
            job_ids = [job_id[0] for job_id in cr.fetchall()]
            args.append(('id','in',job_ids))
        return super(account_analytic_account, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=False)
account_analytic_account()
