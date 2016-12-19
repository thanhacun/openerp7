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
import openerp.addons.decimal_precision as dp

class wizard_kderp_for_import_budget(osv.osv_memory):
    _name = 'wizard.kderp.for.import.budget'
    _description = 'Wizard for Import Budget'

    def create(self, cr, uid, vals, context):
        new_ids = super(wizard_kderp_for_import_budget, self).create(cr, uid, vals)
        new_ids = new_ids if type(new_ids) == type([]) else [new_ids]
        vals = vals if type(vals) == type([]) else [vals]
        # TODO: Create or Update Budget Data To Job
        kbd_obj = self.pool.get('kderp.budget.data')
        newList = []
        updateList = {}
        newAllList = []

        cr.execute("""Select
                              id,
                              account_analytic_id,
                              budget_id
                          from
                              kderp_budget_data
                          where
                              account_analytic_id in (
                          Select
                              distinct "Job"
                          from
                              wizard_kderp_for_import_budget wkfib
                          left join
                              wizard_kderp_for_import_budget_data wkfibd on wkfib.id = import_id where wkfib.id in (%s))""" % ",".join(map(str, new_ids))
                   )
        currentList = {(job_id, budget_id): kbd_id for kbd_id, job_id, budget_id in cr.fetchall()}
        importDetail = []
        for imp in self.browse(cr, uid, new_ids):
            for detail in imp.Details:
                importDetail.append({'account_analytic_id': detail.Job.id,
                                     'budget_id': detail.Budget.id,
                                     'planned_amount': detail.Amount
                                     })

        for val in importDetail:
            job_id = val['account_analytic_id']
            budget_id = val['budget_id']
            find_key = (job_id, budget_id)
            newAllList.append(find_key)
            if find_key not in currentList.keys():
                newList.append(val)
            else:
                updateList[currentList[find_key]] = {'planned_amount': val['planned_amount']}
        deleteList = []
        # deleteList = [currentList[find_key] if find_key not in newAllList else 0 for find_key in currentList]
        for find_key in currentList:
            if find_key not in newAllList:
                deleteList.append(currentList[find_key])
                # TODO: REMOVE LINE BELOW AFTER TEST
                # deleteList.append(currentList)

        for val in updateList:
            kbd_obj.write(cr, uid, [val], updateList[val])

        for val in newList:
            kbd_obj.create(cr, uid, val, context)

        if deleteList:
            list_warning = []
            for kbd in kbd_obj.browse(cr, uid, deleteList, context=context):
                if kbd.detail_budget:
                    list_warning.append("%s-%s" % (str(kbd.account_analytic_id.code), str(kbd.budget_id.code)))
            if list_warning:
                raise osv.except_osv("KDERP Warning",
                                     "Can not DELETE budget having expenses: %s" % "; ".join(list_warning))
            kbd_obj.unlink(cr, uid, deleteList, context)

        return True
    _rec_name = "create_date"
    _columns = {
                'create_date': fields.datetime('Date Created', readonly=True),
                'Details':fields.one2many('wizard.kderp.for.import.budget.data','import_id','Details'),
                'create_uid': fields.many2one('res.users', 'Owner', readonly=True),
                }

class wizard_kderp_for_import_budget_data(osv.osv_memory):
    _name = 'wizard.kderp.for.import.budget.data'
    _description = 'Wizard for Import Budget Data'

    _columns = {
                'Job': fields.many2one('account.analytic.account',"Job", required = True),
                'Budget': fields.many2one('account.budget.post', "Budget", required=True),
                'Amount': fields.float('Amount', required = True, digits_compute=dp.get_precision('Account')),
                'import_id': fields.many2one('wizard.kderp.for.import.budget','Import', required = True)
                }
    _sql_constraints = [('import_job_budget_unique','unique(import_id, "Job", "Budget")','Job and Budget Alread Exist !')]
wizard_kderp_for_import_budget_data()