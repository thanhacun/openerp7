from openerp.osv import fields, osv
    
class kderp_supplier_payment_expense(osv.osv):
    _name = 'kderp.supplier.payment.expense'
    _inherit = 'kderp.supplier.payment.expense'
    
    def _get_payment_from_ge(self, cr, uid, ids, context):
        if not context:
            context = {}
        res = {}
        for ge in self.pool.get('kderp.other.expense').browse(cr, uid, ids, context):
            for pge in ge.supplier_payment_expense_ids:
                res[pge.id] = True
        return res.keys()
    
    _columns={              
              #Relation Field
              'allocated_to': fields.related('expense_id', 'allocated_to', type='char', size=32, string='Allocated to', select = 1,
                                             store={
                                                    'kderp.supplier.payment.expense': (lambda self, cr, uid, ids, c={}: ids, ['expense_id'], 15),
                                                    'kderp.other.expense': (_get_payment_from_ge, ['allocated_to'], 15),
                                                    }),
              'section_incharge_id': fields.related('expense_id', 'section_incharge_id', type='many2one',relation='hr.department', size=32, string='Section Incharge', select = 1,
                                             store={
                                                    'kderp.supplier.payment.expense': (lambda self, cr, uid, ids, c={}: ids, ['expense_id'], 15),
                                                    'kderp.other.expense': (_get_payment_from_ge, ['section_incharge_id'], 15),
                                                    }),
              }