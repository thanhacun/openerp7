from osv import osv, fields

class account_fiscalyear(osv.osv):
    _name = "account.fiscalyear"
    _inherit = "account.fiscalyear"

    def create_period6(self, cr, uid, ids, context=None):
        return self.create_period(cr, uid, ids, context, 6)