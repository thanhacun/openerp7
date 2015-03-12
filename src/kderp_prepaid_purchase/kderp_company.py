import re
import time

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_round, float_is_zero, float_compare
from openerp.tools.translate import _

class res_company(osv.osv):
    _inherit = 'res.company'
    _name = 'res.company'
    
    _columns={
             'location_code':fields.selection((('h','Hanoi'),('s','HCM')),'Location', help='Using for move code', required = True),
             }
    _defaults={
               'location_code':'h'
               }
res_company()