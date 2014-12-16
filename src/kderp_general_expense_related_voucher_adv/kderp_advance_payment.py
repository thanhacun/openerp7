import time
from datetime import datetime
from openerp.osv.orm import Model
from openerp.osv import fields, osv

import openerp.addons.decimal_precision as dp
import re

class kderp_advance_payment(Model):
    _inherit='kderp.advance.payment'
    _description='Add Advance Relation to General Expense'
    _columns={
               'general_expense_id':fields.one2many('kderp.general.expense', 'advance_id', 'General Expense', domain=[('state','not in',('draft','cancel'))],readonly=True),
              }
kderp_advance_payment()