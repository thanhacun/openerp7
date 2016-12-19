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
import time
import pooler
from osv import osv, fields

 
class wizard_update_discount_of_books(osv.osv_memory):
    _name = 'wizard.update.discount.of.books'
    _columns = {
        'book_id' : fields.many2one('kderp.note.book', 'Book'),
        'date_start' : fields.date('Start'),
        'date_end' : fields.date('End'),
        'discount' : fields.float('Discount' ),  
    }
 
    _defaults = { # make default start, end date
        'date_start' : lambda *a: time.strftime('%Y-%m-%d'),
        'date_end' : lambda *a: time.strftime('%Y-%m-%d'),

     }
    def update_discount_of_books(self, cr, uid, ids, context={}):
        book_ids = self.get_book_ids(cr, uid,ids)
        discount = self.get_discount(cr, uid, ids)
        try:
            self.update_discount(cr, uid, ids, book_ids, discount)
        except Exception, e:
            raise osv.except_osv(('Error'), str(e))
    def get_book_ids(self, cr, uid, ids, context={}):
        current_object = self.read(cr, uid, ids, ['book_id'])
        return current_object[0]['book_id']
 
    def get_discount(self, cr, uid, ids, context={}):
        current_object = self.read(cr, uid, ids, ['discount'])
        return current_object[0]['discount']
 
    def update_discount(self, cr, uid, ids, book_ids, discount):
        val = {
            'discount' : discount
        }
        return self.pool.get('kderp.note.book').write(cr, uid, book_ids,val)
 
    def get_table(self, cr, uid, ids, name_of_table):
        pool = pooler.get_pool(cr.dbname)
        return pool.get(name_of_table)
wizard_update_discount_of_books()