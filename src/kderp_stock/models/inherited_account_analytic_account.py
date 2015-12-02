from openerp.osv import osv

from openerp import SUPERUSER_ID

class account_analytic_account(osv.osv):
    """Inherit Analytic Object (Job)"""
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    def create(self, cr, uid, vals, context=None):
        new_job_id=super(account_analytic_account, self).create(cr, uid, vals, context=context)
        #Create Stock Related Project
        try:
            context = context or {}
            ctx = context.copy()
            ctx['jobCode'] = vals['code']
            ctx['warehouseType'] = 'internal'
            sl_obj = self.pool.get('stock.location')
            stock_vals = {'name': vals.get('name'),
                          'account_analytic_id': new_job_id,
                          'usage':'internal'
                          }
            sl_obj.create(cr, SUPERUSER_ID, stock_vals, ctx)
            stock_vals['usage']= 'customer'
            ctx['warehouseType'] = 'customer'
            sl_obj.create(cr, SUPERUSER_ID, stock_vals, ctx)
        except:
            pass
        return new_job_id