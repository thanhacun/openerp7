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


class res_partner(osv.Model):
    _inherit = "res.partner"

    _columns={
          'general_director_id':fields.many2one('hr.employee', 'General Director', domain=[('user_id.partner_id.title','=','General Director')]),
          }

class res_users(osv.Model):
    _inherit = "res.users"
    def __init__(self, pool, cr):
        init_res = super(res_users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(['general_director_id'])

        self.SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        self.SELF_READABLE_FIELDS.extend(['general_director_id'])


res_users()

class res_company(osv.osv):
    _inherit = 'res.company'
    _name = 'res.company'
    _columns={
             'payment_bycash_limit':fields.float("Payment ByCash Limit"),
             'cash_limit_active':fields.boolean("Cash Limit Active"),
             'date_apply':fields.date("Date Apply"),
             'general_director_id':fields.many2one('hr.employee', 'General Director', domain=[('user_id.partner_id.title','=','General Director')])
             }

    _defaults={
             'payment_bycash_limit':lambda *x:0.0
               }

class kderp_payment_bycash_config_settings(osv.osv_memory):
    _name = 'kderp.payment.bycash.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
                'payment_bycash_limit': fields.float('Payment ByCash Limit', required=True),
                'cash_limit_active':fields.boolean("Cash Limit Active"),
                'date_apply':fields.date("Date Apply")
    }
        
    def set_payment_bycash_limit(self, cr, uid, ids, context=None):
        """
        Luu gia tri cua payment_bycash_limit
        """
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        user.company_id.write({
                               'payment_bycash_limit': config.payment_bycash_limit
                               })
        
    def set_cash_limit_active(self, cr, uid, ids, context=None):
        """
        Luu gia tri cua cash_limit_active
        """
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        user.company_id.write({
                               'cash_limit_active': config.cash_limit_active
                               })
        
    def set_date_apply(self, cr, uid, ids, context=None):
        """
        Luu gia tri cua date_apply
        """
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        user.company_id.write({
                               'date_apply': config.date_apply
                               })
        
    _defaults = {
        'payment_bycash_limit': lambda self, cr, uid, context:self.pool.get('res.users').browse(cr, uid, uid, context).company_id.payment_bycash_limit,
        'cash_limit_active': lambda self, cr, uid, context:self.pool.get('res.users').browse(cr, uid, uid, context).company_id.cash_limit_active,
        'date_apply': lambda self, cr, uid, context:self.pool.get('res.users').browse(cr, uid, uid, context).company_id.date_apply
        }

