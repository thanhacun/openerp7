from openerp.osv import fields, osv

class kderp_expense_budget_line(osv.osv):
    _name = 'kderp.expense.budget.line'
    _description='Expense Budget Line'
    _inherit = 'kderp.expense.budget.line'
    
    def _get_effdate(self, cr, uid, ids, args, name, context ={}):
        res={}        
        dict_obj={'purchase.order':True}
        po_obj = self.pool.get('purchase.order')
        dict_f = {}
        for kebl in self.browse(cr, uid, ids, context):            
            if kebl.expense_obj in dict_obj:
                exp_id = kebl.expense_id
                if exp_id in dict_f:
                    dict_f[exp_id][kebl.id] = True
                else:
                    dict_f[exp_id] = {kebl.id : True}                
                #res[id] = po_obj.browse(cr, uid, exp_id).effective_date        
            else:
                res[kebl.id] = False
        po_ids = dict_f.keys()
        for po in po_obj.browse(cr, uid, po_ids):
            eff_date = po.effective_date
            for id in dict_f[po.id].keys():
                res[id] = eff_date
        return res
    
    _columns = {
                "eff_date":fields.function(_get_effdate, type='date', string='Eff. Date')
                }