from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null

import openerp.exceptions

class kderp_supplier_payment(osv.osv):
    _name = 'kderp.supplier.payment'
    _inherit= 'kderp.supplier.payment'      
    
    def _check_cash(self, cr, uid, ids, context=None):
        limited_cash_amount=self.pool.get('res.users').browse(cr,uid,uid).company_id.limited_cash_amount
        if not context:
            context={}
        for kap in self.browse(cr, uid, ids, context=context):
            for var in kap.kderp_vat_invoice_ids:
                if var.equivalent_vnd>limited_cash_amount and kap.payment_type == 'cash': 
                    raise osv.except_osv(_('Error!'), _('Check Payment Type and Red Invoice Amount'),)
                    return False
        return True
    
    _constraints = [ (_check_cash, 'Supplier Payment Job must be unique !',['payment_line','kderp_vat_invoice_ids']),]
    
kderp_supplier_payment()
