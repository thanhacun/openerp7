from openerp.osv import fields, osv

from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

class KDERPExpenseBudgetLine(osv.osv):
    _name='kderp.expense.budget.line'
    _inherit='kderp.expense.budget.line'

    def _get_curr_period_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        list_cal = []
        kebl_ids=",".join(map(str,ids))
        cr.execute("""Select
                        kebl.id,
                        pp.currency_id,
                        po.period_id as period_id,
                        date_order as date,
                        po.partner_id as partner_id,
                        notes as description,
                        po.name as name
                    from
                        kderp_expense_budget_line kebl
                    left join
                        purchase_order po on kebl.expense_id=po.id and kebl.expense_obj='purchase.order'
                    left join
                        product_pricelist pp on pricelist_id=pp.id
                    where kebl.expense_obj='purchase.order' and kebl.id in (%s)
                    Union
                    Select
                        kebl.id,
                        koe.currency_id,
                        koe.period_id as period_id,
                        koe.date,
                        koe.partner_id,
                        koe.description,
                        koe.name
                    from
                        kderp_expense_budget_line kebl
                    left join
                        kderp_other_expense koe on kebl.expense_id=koe.id and kebl.expense_obj='kderp.other.expense'
                    where kebl.expense_obj='kderp.other.expense' and kebl.id in (%s)
                    Union
                    Select
                        kebl.id,
                        (Select currency_id from res_company limit 1) as currency_id,
                        null as period_id,
                        kme.date,
                        (Select partner_id from res_company limit 1) as partner_id,
                        kme.name,
                        kme.code
                    from
                        kderp_expense_budget_line kebl
                    left join
                        kderp_moving_expense kme on kebl.expense_id=kme.id and kebl.expense_obj='kderp.moving.expense'
                    where kebl.expense_obj='kderp.moving.expense' and kebl.id in (%s)""" % (kebl_ids,kebl_ids,kebl_ids))
        kebl_ids_update=[]
        for id,currency_id,period_id,date,partner_id,description,name in cr.fetchall():
                if name:
                    if 'currency_id' in name:
                        kebl_ids_update.append(id)
                res[id]={'exrate':1} #Exrate temporary
                res[id].update({'currency_id':currency_id})
                res[id].update({'period_id':period_id if period_id else False})
                res[id].update({'name':name})
                res[id].update({'partner_id':partner_id})
                res[id].update({'date':date})
                res[id].update({'description':description})
        if kebl_ids_update:
            self.write(cr, uid, kebl_ids_update,{})
        return res

    def _get_amount_from_line_and_payment(self, cr, uid, ids, name, args, context={}):
        if not context:
            context = {}
        res = {}
        job_obj = self.pool.get('account.analytic.account')
        kbudget_obj = self.pool.get('kderp.budget.data')
        list_update = []
        kebl_ids = ",".join(map(str, ids))
        cr.execute("""Select
                            kebl.id,
                            kebl.budget_id,
                            kebl.account_analytic_id,
                            expense_amount as amount,
                            vwcombine_manual.amount_currency,
                            vwcombine_manual.amount_tax,
                            sum(vwcombine_manual.payment_amount) as payment_amount
                    from
                        kderp_expense_budget_line kebl
                    left join
                        (Select
                            po.id as po_id,
                            vwpol.budget_id,
                            vwpol.account_analytic_id,
                            amount_currency,
                            expense_amount,
                            vwpol.amount_tax,
                            sum(coalesce(kspl.amount*coalesce(fnpo_compute(ksp.currency_id,company_curr,po.date_order),0))) as payment_amount
                        from
                            purchase_order po
                        left join
                            kderp_supplier_payment ksp on po.id=order_id
                        left join
                            (Select
                                order_id,
                                budget_id,
                                account_analytic_id,
                                sum(coalesce(final_subtotal,0)) as amount_currency,
                                sum(coalesce(amount_company_curr,0)) as expense_amount,
                                sum(coalesce(pol.amount_tax,0)) as amount_tax
                            from
                                purchase_order_line pol
                            where
                                    (order_id,
                                    budget_id,
                                    account_analytic_id) in (Select kebl.expense_id,kebl.budget_id,kebl.account_analytic_id from kderp_expense_budget_line kebl where expense_obj='purchase.order' and kebl.id in (%s))
                            group by
                                budget_id,
                                account_analytic_id,
                                order_id) vwpol on po.id=vwpol.order_id
                        left join
                            kderp_supplier_payment_line kspl on  ksp.id=supplier_payment_id and vwpol.budget_id=kspl.budget_id and vwpol.account_analytic_id=kspl.account_analytic_id
                        left join
                            (Select currency_id as company_curr from res_company limit 1) vwtemp on True
                        where
                            po.state not in ('draft','cancel','done') and coalesce(vwpol.order_id,0)>0 and ksp.state not in ('draft','cancel') and coalesce(ksp.base_on_line,False)=True
                        group by
                            vwpol.budget_id,
                            vwpol.account_analytic_id,
                            po.id,
                            expense_amount,
                            vwpol.amount_tax,
                            amount_currency
                    Union
                        Select
                            po.id as po_id,
                            budget_id,
                            pol.account_analytic_id,
                            sum(coalesce(final_subtotal,0)) as amount_currency,
                            sum(coalesce(amount_company_curr,0)) as expense_amount,
                            sum(coalesce(pol.amount_tax,0)) as amount_tax,
                            sum(coalesce(final_subtotal,0)) * payment_per as payment_amount
                        from
                            purchase_order po
                        left join
                            purchase_order_line pol on po.id=pol.order_id
                        left join
                             (Select
                                po.id as po_id,
                                case when coalesce(final_price,0)=0 then 0 else sum(sub_total)/(final_price) end as payment_per
                            from
                                kderp_supplier_payment ksp
                            left join
                                purchase_order po   on po.id=order_id
                            where
                                    po.state not in ('draft','cancel')  and coalesce(ksp.base_on_line,False)=False and ksp.state not in ('draft','cancel')
                                and
                                    po.id  in (Select
                                            order_id
                                            from
                                            kderp_supplier_payment  ksp
                                            left join
                                            purchase_order po on order_id=po.id
                                            where
                                            po.id in (Select kebl.expense_id from kderp_expense_budget_line kebl where expense_obj='purchase.order' and kebl.id in (%s)) and
                                            coalesce(base_on_line,False)=True and  ksp.state not in ('draft','cancel') and po.state not in ('draft','cancel','done'))
                            group by
                                po.id) vwpayment_per on po.id=po_id
                        where
                            po.state not in ('draft','cancel') and po.id in (Select kebl.expense_id from kderp_expense_budget_line kebl where expense_obj='purchase.order' and kebl.id in (%s))  and coalesce(po_id,0)>0
                        group by
                            budget_id,
                            pol.account_analytic_id,
                            po.id,
                            payment_per) vwcombine_manual on expense_id=po_id and kebl.budget_id=vwcombine_manual.budget_id and kebl.account_analytic_id=vwcombine_manual.account_analytic_id
                    Where
                        expense_obj='purchase.order' and coalesce(po_id,0)>0 and kebl.id in (%s)
                    Group by
                        kebl.id,
                        vwcombine_manual.amount_currency,
                        expense_amount,
                        vwcombine_manual.amount_tax
            Union
                    Select
                            kebl.id,
                            kebl.budget_id,
                            kebl.account_analytic_id,
                            sum(coalesce(amount_company_curr,0)) as amount,
                            sum(coalesce(final_subtotal,0)) as amount_currency,
                            sum(coalesce(pol.amount_tax,0)) as amount_tax,
                            sum(coalesce(amount_company_curr,0))*coalesce(payment_percentage,0) as payment_amount
                        from
                            kderp_expense_budget_line kebl
                        left join
                            purchase_order_line pol on expense_id=order_id and kebl.budget_id=pol.budget_id and kebl.account_analytic_id=pol.account_analytic_id
                        left join
                            purchase_order po on pol.order_id=po.id
                        where
                            expense_obj='purchase.order' and kebl.id in (%s) and
                             (po.state='done' or
                                po.id not in (Select
                                                order_id
                                            from
                                                kderp_supplier_payment
                                            left join
                                                purchase_order po on order_id=po.id
                                            where
                                                coalesce(base_on_line,False)=True and po.state not in ('draft','cancel','done')))
                        group by
                            kebl.id,
                            po.id
                        Union
                        Select
                            kebl.id,
                            kebl.budget_id,
                            kebl.account_analytic_id,
                            sum(coalesce(amount_company_curr,0)) as amount,
                            sum(coalesce(koel.amount,0)) as amount_currency,
                            0 as amount_tax,
                            sum(coalesce(amount_company_curr,0))*coalesce(payment_percentage,0) as payment_amount
                        from
                            kderp_expense_budget_line kebl
                        left join
                            kderp_other_expense_line koel on kebl.expense_id=koel.expense_id and kebl.budget_id=koel.budget_id and kebl.account_analytic_id=koel.account_analytic_id
                        left join
                            kderp_other_expense koe on koel.expense_id=koe.id
                        where
                            expense_obj='kderp.other.expense' and kebl.id in (%s)
                        group by
                            kebl.id,
                            koe.id
--Moving Expense Area
                    Union
                    Select
                        kebl.id,
                        kebl.budget_id,
                        kebl.account_analytic_id,
                        sum(-kmel.amount) as amount,
                        sum(-kmel.amount) as amount_currency,
                        0 as amount_tax,
                        sum(-kmel.amount) as payment_amount
                    from
                        kderp_expense_budget_line kebl
                    left join
                        kderp_moving_expense kme on kebl.expense_id = kme.id and expense_obj = 'kderp.moving.expense' and kebl.account_analytic_id = from_job_id
                    left join
                        kderp_moving_expense_line kmel on kme.id = kmel.moving_expense_id and kebl.budget_id = kmel.budget_id
                    where
                        expense_obj = 'kderp.moving.expense' and kme.state not in ('draft','cancel') and kebl.id in (%s)
                    group by
                        kebl.id,
                        kebl.budget_id,
                        kebl.account_analytic_id
                    Union
                    Select
                        kebl.id,
                        kebl.budget_id,
                        kebl.account_analytic_id,
                        sum(+kmel.amount) as amount,
                        sum(+kmel.amount) as amount_currency,
                        0 as amount_tax,
                        sum(+kmel.amount) as payment_amount
                    from
                        kderp_expense_budget_line kebl
                    left join
                        kderp_moving_expense kme on kebl.expense_id = kme.id and expense_obj = 'kderp.moving.expense' and kebl.account_analytic_id = to_job_id
                    left join
                        kderp_moving_expense_line kmel on kme.id = kmel.moving_expense_id and kebl.budget_id = kmel.budget_id
                    where
                        expense_obj = 'kderp.moving.expense' and kme.state not in ('draft','cancel') and kebl.id in (%s)
                    group by
                        kebl.id,
                        kebl.budget_id,
                        kebl.account_analytic_id
                            """ % (kebl_ids, kebl_ids, kebl_ids, kebl_ids, kebl_ids, kebl_ids, kebl_ids, kebl_ids))
        job_list = []
        kbd_ids = []
        for id, bg_id, job_id, amount, amount_currency, amount_tax, p_amount in cr.fetchall():
            res[id] = {'amount': amount,
                       'amount_currency': amount_currency,
                       'amount_tax': amount_tax,
                       'payment_amount': p_amount
                       }
            job_list.append(job_id)
            kbd_ids.extend(
                kbudget_obj.search(cr, uid, [('budget_id', '=', bg_id), ('account_analytic_id', '=', job_id)]))
        if not context.get('stop_write_kebl', False):
            self.write(cr, uid, ids, {}, {'stop_write_kebl': True})

        return res

    ####Get List ID from Purchase and related Object
    def _get_purchase_order(self, cr, uid, ids, context=None):
        result = []
        for po in self.pool.get('purchase.order').browse(cr, uid, ids, context=context):
            for pol in po.order_line:
                if pol.expense_budget_line:
                    result.append(pol.expense_budget_line.id)
        return list(set(result))

    def _get_expense_line_from_pol(self, cr, uid, ids, context=None):
        result = []
        for pol in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            for poll in pol.order_id.order_line:
                result.append(poll.expense_budget_line.id)
        return list(set(result))

    def _get_budget_line_from_supplier_payment(self, cr, uid, ids, context=None):
        result = {}
        ksp_obj = self.pool.get('kderp.supplier.payment')
        for ksp in ksp_obj.browse(cr, uid, ids):
            for pol in ksp.order_id.order_line:
                if pol.expense_budget_line:
                    result[pol.expense_budget_line.id] = True
        result = result.keys()
        return result

    def _get_budget_line_from_supplier_payment_line(self, cr, uid, ids, context=None):
        result = {}
        ksp_obj = self.pool.get('kderp.supplier.payment.line')
        for kspl in ksp_obj.browse(cr, uid, ids):
            for pol in kspl.supplier_payment_id.order_id.order_line:
                if pol.expense_budget_line:
                    result[pol.expense_budget_line.id] = True
        result = list(set(result.keys()))
        return result

    def _get_budget_line_from_supplier_payment_pay(self, cr, uid, ids, context=None):
        result = {}
        kp_obj = self.pool.get('kderp.supplier.payment.pay')
        for kp in kp_obj.browse(cr, uid, ids):
            for pol in kp.supplier_payment_id.order_id.order_line:
                if pol.expense_budget_line:
                    result[pol.expense_budget_line.id] = True
        result = list(set(result.keys()))
        return result

    ###Aread of Other Expense
    def _get_other_expense_line_from_koel(self, cr, uid, ids, context=None):
        result = []
        for koel in self.pool.get('kderp.other.expense.line').browse(cr, uid, ids, context=context):
            for koell in koel.expense_id.expense_line:
                result.append(koell.expense_budget_line.id)
        return list(set(result))

    def _get_other_expense(self, cr, uid, ids, context=None):
        result = []
        for koe in self.pool.get('kderp.other.expense').browse(cr, uid, ids, context=context):
            for koel in koe.expense_line:
                if koel.expense_budget_line:
                    result.append(koel.expense_budget_line.id)
        return list(set(result))

    def _get_budget_line_from_supplier_payment_expense(self, cr, uid, ids, context=None):
        result = {}
        kspe_obj = self.pool.get('kderp.supplier.payment.expense')
        for kspe in kspe_obj.browse(cr, uid, ids):
            for koel in kspe.expense_id.expense_line:
                if koel.expense_budget_line:
                    result[koel.expense_budget_line.id] = True
        result = list(set(result.keys()))
        return result

    def _get_budget_line_from_supplier_payment_expense_line(self, cr, uid, ids, context=None):
        result = {}
        kspel_obj = self.pool.get('kderp.supplier.payment.expense.line')
        for ksple in kspel_obj.browse(cr, uid, ids):
            for koel in ksple.supplier_payment_expense_id.expense_id.expense_line:
                if koel.expense_budget_line:
                    result[koel.expense_budget_line.id] = True
        result = list(set(result.keys()))
        return result

    def _get_budget_line_from_supplier_payment_expense_pay(self, cr, uid, ids, context=None):
        result = {}
        kpe_obj = self.pool.get('kderp.supplier.payment.expense.pay')
        for kpe in kpe_obj.browse(cr, uid, ids):
            for koel in kpe.supplier_payment_expense_id.expense_id.expense_line:
                if koel.expense_budget_line:
                    result[koel.expense_budget_line.id] = True
        result = list(set(result.keys()))
        return result

    def _get_moving_expense(self, cr, uid, ids, context=None):
        result = []
        list_dict_keys = {}
        for koe in self.pool.get('kderp.moving.expense').browse(cr, uid, ids, context=context):
            from_job_id = koe.from_job_id.id if koe.from_job_id else False
            to_job_id = koe.to_job_id.id if koe.to_job_id else False
            exp_id = int(koe.id) #Sometime show in long type
            for koel in koe.detail_ids:
                if from_job_id:
                    list_dict_keys[(exp_id, from_job_id, koel.budget_id.id)] = True
                if to_job_id:
                    list_dict_keys[(exp_id, to_job_id, koel.budget_id.id)] = True
        if not list_dict_keys:
            return []
        cr.execute("""Select
                            id
                      from
                            kderp_expense_budget_line
                      where
                            expense_obj='kderp.moving.expense' and (expense_id,account_analytic_id,budget_id) in (%s)""" % ",".join(map(str, list_dict_keys.keys())))
        return [kebl_id[0] for kebl_id in cr.fetchall()]

    def _get_other_expense_line_from_kmel(self, cr, uid, ids, context=None):
        result = []
        list_dict_keys = {}
        for kmel in self.pool.get('kderp.moving.expense.line').browse(cr, uid, ids, context=context):
            from_job_id = kmel.moving_expense_id.from_job_id.id if kmel.moving_expense_id.from_job_id else False
            to_job_id = kmel.moving_expense_id.to_job_id.id if kmel.moving_expense_id.to_job_id else False
            exp_id = int(kmel.moving_expense_id.id) #Sometime show in long type
            if from_job_id:
                list_dict_keys[(exp_id, from_job_id, kmel.budget_id.id)] = True
            if to_job_id:
                list_dict_keys[(exp_id, to_job_id, kmel.budget_id.id)] = True
        cr.execute("""Select
                            id
                      from
                            kderp_expense_budget_line
                      where
                            expense_obj='kderp.moving.expense' and (expense_id,account_analytic_id,budget_id) in (%s)""" % ",".join(map(str, list_dict_keys.keys())))
        return [kebl_id[0] for kebl_id in cr.fetchall()]

    #####END OF
    _columns = {
                'exrate':fields.function(_get_curr_period_date, string='Exrate', type='float', multi='kderp_get_id',
                                         digits_compute=dp.get_precision('Account'),
                                         store={
                                             'purchase.order':(_get_purchase_order, ['currency_id', 'pricelist_id', 'date_order'], 20),
                                             'kderp.other.expense': (_get_other_expense, ['currency_id', 'date'], 20),
                                             'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids, None, 15),
                                         }),
                'partner_id':fields.function(_get_curr_period_date, string='Supplier', type='many2one', relation='res.partner',
                                             multi='kderp_get_id',
                                             store={
                                                 'purchase.order': (_get_purchase_order, ['partner_id'], 20),
                                                 'kderp.other.expense': (_get_other_expense, ['partner_id'], 20),
                                                 'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids, None, 15),
                                             }),

                'name':fields.function(_get_curr_period_date, string='Name', type='char', size=64, multi='kderp_get_id',
                                       store={
                                           'purchase.order': (_get_purchase_order, ['name'], 20),
                                           'kderp.other.expense': (_get_other_expense, ['name'], 20),
                                           'kderp.moving.expense': (_get_moving_expense, ['code'], 20),
                                           'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids, None, 15),
                                       }),
                'description':fields.function(_get_curr_period_date, string='Desc.', type='char', size=256, multi='kderp_get_id',
                                              store={
                                                  'purchase.order': (_get_purchase_order, ['notes'], 20),
                                                  'kderp.other.expense': (_get_other_expense, ['description'], 20),
                                                  'kderp.moving.expense': (_get_moving_expense, ['name'], 20),
                                                  'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids, None, 15),
                                              }),

                'currency_id':fields.function(_get_curr_period_date, string='Curr.', type='many2one', relation='res.currency',
                                              multi='kderp_get_id',
                                              store={
                                                  'purchase.order': (_get_purchase_order, ['currency_id', 'pricelist_id'], 20),
                                                  'kderp.other.expense': (_get_other_expense, ['currency_id'], 20),
                                                  'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids, None, 15),
                                              }),
                'period_id':fields.function(_get_curr_period_date, string='Period', type='many2one', relation='account.period',
                                            multi='kderp_get_id',
                                            store={
                                                'purchase.order': (_get_purchase_order, ['period_id'], 20),
                                                'kderp.other.expense': (_get_other_expense, ['period_id'], 20),
                                                'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids, None, 15),
                                            }),
                'date': fields.function(_get_curr_period_date, string='Date of Order', type='date', multi='kderp_get_id',
                                        store={
                                            'purchase.order': (_get_purchase_order, ['date_order'], 20),
                                            'kderp.other.expense': (_get_other_expense, ['date'], 20),
                                            'kderp.moving.expense': (_get_moving_expense, ['date'], 20),
                                            'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids, None, 15),
                                        }),

              # Fields Function Store Amount Area
              'amount_currency': fields.function(_get_amount_from_line_and_payment,type='float',method=True,digits_compute=dp.get_precision('Amount'),string='Amount Currency',
                                                 multi="_get_amount_from_line",
                                                store = {
                                                        'purchase.order.line': (_get_expense_line_from_pol,  ['amount_company_curr','price_unit','plan_qty'], 40),
                                                        'purchase.order': (_get_purchase_order, ['pricelist_id','date_order','state','discount_amount'], 40),
                                                        'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids,None, 20),
                                                        'kderp.other.expense.line':(_get_other_expense_line_from_koel, ['amount_company_curr','amount'], 40),
                                                        'kderp.other.expense':(_get_other_expense, ['date','currency_id','state','taxes_id'], 40),
                                                        'kderp.supplier.payment.expense': (_get_budget_line_from_supplier_payment_expense, ['state','taxes_id','currency_id','date'], 40),
                                                        'kderp.supplier.payment.expense.line': (_get_budget_line_from_supplier_payment_expense_line, ['amount'], 40),
                                                        'kderp.supplier.payment.expense.pay': (_get_budget_line_from_supplier_payment_expense_pay, None, 40),
                                                        'kderp.moving.expense.line':(_get_other_expense_line_from_kmel, ['amount'], 40),
                                                        }),
              'amount_tax': fields.function(_get_amount_from_line_and_payment,type='float',digits_compute=dp.get_precision('Budget'),method=True,string='Tax Amount',
                                                multi="_get_amount_from_line",
                                                store = {
                                                        'purchase.order.line':(_get_expense_line_from_pol, ['amount_tax','taxes_id','amount_company_curr','price_unit','plan_qty'], 25),
                                                        'purchase.order':(_get_purchase_order, ['discount_amount','special_case','state'], 25),
                                                        'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids,None, 20),

                                                        'kderp.other.expense.line':(_get_other_expense_line_from_koel, ['amount_company_curr','amount'], 40),
                                                        'kderp.other.expense':(_get_other_expense, ['date','currency_id','state','taxes_id'], 40),
                                                        #'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids,None, 40),
                                                        'kderp.supplier.payment.expense': (_get_budget_line_from_supplier_payment_expense, ['state','taxes_id','currency_id','date'], 40),
                                                        'kderp.supplier.payment.expense.line': (_get_budget_line_from_supplier_payment_expense_line, ['amount'], 40),
                                                        'kderp.supplier.payment.expense.pay': (_get_budget_line_from_supplier_payment_expense_pay, None, 40),
                                                        }),

              'amount': fields.function(_get_amount_from_line_and_payment,type='float',digits_compute=dp.get_precision('Budget'),string='Amount In Company Currency',
                                                multi="_get_amount_from_line_and_payment",
                                                store = {
                                                        'purchase.order.line':(_get_expense_line_from_pol, ['amount_company_curr','price_unit','plan_qty'], 40),
                                                        'purchase.order':(_get_purchase_order, ['discount_amount','special_case','state','pricelist_id','taxes_id'], 40),
                                                        'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids,None, 40),
                                                        'kderp.supplier.payment': (_get_budget_line_from_supplier_payment, ['state','amount','advanced_amount','retention_amount','taxes_id','currency_id','date'], 40),
                                                        'kderp.supplier.payment.pay': (_get_budget_line_from_supplier_payment_pay, None, 40),

                                                        'kderp.other.expense.line':(_get_other_expense_line_from_koel, ['amount_company_curr','amount'], 40),
                                                        'kderp.other.expense':(_get_other_expense, ['date','state','currency_id','taxes_id'], 40),
                                                        #'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids,None, 40),
                                                        'kderp.supplier.payment.expense': (_get_budget_line_from_supplier_payment_expense, ['state','taxes_id','currency_id','date'], 40),
                                                        'kderp.supplier.payment.expense.line': (_get_budget_line_from_supplier_payment_expense_line, ['amount'], 40),
                                                        'kderp.supplier.payment.expense.pay': (_get_budget_line_from_supplier_payment_expense_pay, None, 40),
                                                        'kderp.moving.expense.line':(_get_other_expense_line_from_kmel, ['amount'], 40),
                                                        }),
              #_get_amount_payment
               'payment_amount': fields.function(_get_amount_from_line_and_payment,type='float',digits_compute=dp.get_precision('Budget'),string='Payment Amount',
                                                multi="_get_amount_from_line",
                                                  store = {
                                                        'purchase.order.line':(_get_expense_line_from_pol, ['amount_company_curr','price_unit','plan_qty'], 45),
                                                        'purchase.order':(_get_purchase_order, ['discount_amount','special_case','state','pricelist_id','date_order','taxes_id'], 45),
                                                        'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids,None, 45),
                                                        'kderp.supplier.payment': (_get_budget_line_from_supplier_payment, ['state','amount','advanced_amount','retention_amount','taxes_id','currency_id','date','base_on_line','order_id'], 45),
                                                        'kderp.supplier.payment.line': (_get_budget_line_from_supplier_payment_line, None, 45),
                                                        'kderp.supplier.payment.pay': (_get_budget_line_from_supplier_payment_pay, None, 45),

                                                        'kderp.other.expense.line':(_get_other_expense_line_from_koel, ['amount_company_curr','amount'], 45),
                                                        'kderp.other.expense':(_get_other_expense, ['date','state','currency_id','taxes_id'], 45),
                                                        #'kderp.expense.budget.line': (lambda self, cr, uid, ids, c={}: ids,None, 40),
                                                        'kderp.supplier.payment.expense': (_get_budget_line_from_supplier_payment_expense, ['state','taxes_id','currency_id','date','expense_id'], 45),
                                                        'kderp.supplier.payment.expense.line': (_get_budget_line_from_supplier_payment_expense_line, ['amount'], 45),
                                                        'kderp.supplier.payment.expense.pay': (_get_budget_line_from_supplier_payment_expense_pay, None, 45),
                                                        'kderp.moving.expense.line':(_get_other_expense_line_from_kmel, ['amount'], 40),
                                                        }),
    }

    #Expense Type allocated to budget only Expense and Monthly Expense
    def create_update_expense_budget_line(self,cr,uid,ids,res_obj,field_link='order_id',context={}):
        dict_exp_obj = {'purchase.order':'purchase_order','purchase.order.line':'purchase_order_line',
                        'kderp.other.expense':'kderp_other_expense','kderp.other.expense.line':'kderp_other_expense_line',
                        'kderp.moving.expense':"kderp_moving_expense", 'kderp.moving.expense.line': 'kderp_moving_expense_line'}
        
        #po_budget_line_ids = []
        pol_link_dicts={}
        for exp in self.pool.get(res_obj).browse(cr, uid, ids, context):
            expense_budget_lines = []
            expense_budget_lines_delete = []
        
            expense_id = exp.id

            if res_obj=='purchase.order':
                exp_date = exp.date_order
                exp_type = True
            else:
                exp_date = exp.date
                exp_type = "expense_type in ('expense','monthly_expense')"

            #Expense Type allocated to budget only Expense and Monthly Expense            
            exp_table=dict_exp_obj[res_obj]
            ####DELETE
            #In case KDERP Moving Expense
            if res_obj == 'kderp.moving.expense':
                cr.execute("""Select
                                    kebl.id
                                from
                                    kderp_expense_budget_line kebl
                                left join
                                    %s exp on expense_id=exp.id and (kebl.account_analytic_id = exp.from_job_id or kebl.account_analytic_id = exp.to_job_id)
                                left join
                                    %s_line expl on exp.id=expl.%s and kebl.budget_id=expl.budget_id
                                where
                                    expense_obj='%s' and kebl.expense_id=%s and (coalesce(expl.id,0)=0 or exp.state in ('draft','cancel'))
                                group by
                                    kebl.id,
                                    kebl.account_analytic_id,
                                    kebl.budget_id
                                Union
                                Select
                                    kebl.id
                                from
                                    kderp_expense_budget_line kebl
                                left join
                                     %s exp on expense_id=exp.id and (kebl.account_analytic_id = exp.from_job_id or kebl.account_analytic_id = exp.to_job_id)
                                left join
                                    %s_line expl on exp.id=expl.%s and kebl.budget_id=expl.budget_id
                                where
                                    expense_obj='%s' and kebl.expense_id=%s and coalesce(expl.id,0)=0
                                    """ % (exp_table, exp_table, field_link, res_obj, expense_id,
                                           exp_table, exp_table, field_link, res_obj, expense_id))
            else:
                cr.execute("""Select
                                    kebl.id
                                from
                                    kderp_expense_budget_line kebl
                                left join
                                    %s exp on expense_id=exp.id
                                left join
                                    %s_line expl on exp.id=expl.%s and kebl.budget_id=expl.budget_id and kebl.account_analytic_id=expl.account_analytic_id
                                where
                                    expense_obj='%s' and kebl.expense_id=%s and (coalesce(expl.id,0)=0 or exp.state in ('draft','cancel')) or not %s
                                group by
                                    kebl.id,
                                    kebl.account_analytic_id,
                                    kebl.budget_id
                                Union
                                Select
                                    kebl.id
                                from
                                    kderp_expense_budget_line kebl
                                left join
                                    %s_line expl on kebl.expense_id=expl.%s and kebl.id=expense_budget_line
                                where
                                    expense_obj='%s' and kebl.expense_id=%s and coalesce(expl.id,0)=0
                                    """ % (exp_table,exp_table,field_link,res_obj,expense_id,exp_type,
                                           exp_table,field_link,res_obj,expense_id))
            
            for kebl_id in cr.fetchall():
                expense_budget_lines_delete.append(kebl_id[0])
            if expense_budget_lines_delete:
                deleted_exp=self.unlink(cr, uid, expense_budget_lines_delete,context)
            ###Create

            # In case KDERP Moving Expense
            if res_obj == 'kderp.moving.expense':
                cr.execute("""
                            -- From Job ID
                            Select
                                    exp.id as exp_id,
                                    exp.from_job_id,
                                    expl.budget_id
                            from
                                %s exp
                            left join
                                %s_line expl on exp.id=expl.%s
                            left join
                                kderp_expense_budget_line kebl on
                                                                expense_obj='%s' and
                                                                exp.id=kebl.expense_id and
                                                                expl.budget_id=kebl.budget_id and
                                                                exp.from_job_id = kebl.account_analytic_id
                            where
                                exp.state not in ('draft','cancel') and exp.id=%s and coalesce(kebl.id,0)=0 and coalesce(expl.id,0)>0 and coalesce(exp.from_job_id,0)>0
                            group by
                                exp.id,
                                exp.from_job_id,
                                expl.budget_id
                            UNION
                            -- To Job ID
                                Select
                                        exp.id as exp_id,
                                        exp.to_job_id,
                                        expl.budget_id
                                from
                                    %s exp
                                left join
                                    %s_line expl on exp.id=expl.%s
                                left join
                                    kderp_expense_budget_line kebl on
                                                                    expense_obj='%s' and
                                                                    exp.id=kebl.expense_id and
                                                                    expl.budget_id=kebl.budget_id and
                                                                    exp.to_job_id = kebl.account_analytic_id
                                where
                                    exp.state not in ('draft','cancel') and exp.id=%s and coalesce(kebl.id,0)=0 and coalesce(expl.id,0)>0 and coalesce(exp.to_job_id,0)>0
                                group by
                                    exp.id,
                                    exp.to_job_id,
                                    expl.budget_id
                            """ % (exp_table, exp_table, field_link, res_obj, expense_id,
                                   exp_table, exp_table, field_link, res_obj, expense_id))
            else:
                cr.execute("""Select
                                    exp.id as exp_id,
                                    expl.account_analytic_id,
                                    expl.budget_id
                            from
                                %s exp
                            left join
                                %s_line expl on exp.id=expl.%s
                            left join
                                kderp_expense_budget_line kebl on
                                                                expense_obj='%s' and
                                                                exp.id=kebl.expense_id and
                                                                expl.budget_id=kebl.budget_id and
                                                                expl.account_analytic_id=kebl.account_analytic_id
                            where
                                exp.state not in ('draft','cancel') and exp.id=%s and coalesce(kebl.id,0)=0 and coalesce(expl.id,0)>0 and %s
                            group by
                                exp.id,
                                expl.account_analytic_id,
                                expl.budget_id""" % (exp_table,exp_table,field_link,res_obj,expense_id,exp_type))
            
            for exp_id,job_id,budget_id in cr.fetchall(): #list need to insert
                    expense_budget_line={'expense_id':exp_id,
                                     'expense_obj':res_obj,
                                     'account_analytic_id':job_id,
                                     'budget_id':budget_id}
                    expense_budget_lines.append(expense_budget_line)
            
            pol_link_dicts={}
            #raise osv.except_osv("E",expense_budget_lines)
            for expense_budget_line in expense_budget_lines:
                expense_budget_line_id=self.create(cr,uid,expense_budget_line,context) #Create Purchase Budget line
        #    expense_budget_line_ids.append(expense_budget_line_id)
                pol_link_dicts[str(expense_budget_line['expense_id'])+str(expense_budget_line['account_analytic_id'])+str(expense_budget_line['budget_id'])]=expense_budget_line_id
            
        return pol_link_dicts    
    
    def action_open_related_obj(self, cr, uid, ids, *args):
        context = filter(lambda arg: type(arg) == type({}), args)
        if not context:
            context = {}
        else:
            context = context[0]

        obj_id=False
        obj=''
        dict_name={'purchase.order':'Purchase Order',
                   'kderp.other.expense':'Other Expense',
                   'kderp.moving.expense':"Moving Expense"}
        
        for object in self.browse(cr, uid, ids):
            obj_id = [object.expense_id]
            obj = object.expense_obj
            
        interface_string = 'General Expense' if context.get('general_expense', False) else dict_name[obj]
        if obj_id:            
            return {
            'type': 'ir.actions.act_window',
            'name': interface_string,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': context,
            'res_model': obj,
            'domain': "[('id','in',%s)]" % obj_id
            }
        else:
            return True