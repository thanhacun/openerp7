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
                'control_area_id':fields.many2one('kderp.control.area','Control Area', ondelete='restrict'),
                'control_area_percent': fields.float('%'),
                'support_area_id': fields.many2one('kderp.control.area','Support Area', ondelete='restrict'),
                'support_area_percent': fields.float('%'),

                # FIXME Truong nay se co ten la Job Type, Job Type doi thanh E/M, phai hop nhat khi Upgrade len Odoo
                'job_scale':fields.function(_get_job_scale, type = 'selection', string = 'Job Type', selection = JOB_SCALE_SELECTION, method = True, select = 1,
                                            store = {'account.analytic.account':(lambda self, cr, uid, ids, context = {}: ids, ['code'], 50),})
              }
account_analytic_account()