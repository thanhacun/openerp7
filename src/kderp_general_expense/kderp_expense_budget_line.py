from openerp.osv import fields, osv


class kderp_expense_budget_line(osv.osv):
    _name='kderp.expense.budget.line'
    _inherit='kderp.expense.budget.line'
    
    #Expense Type allocated to budget only Expense and Monthly Expense
    def create_update_expense_budget_line(self,cr,uid,ids,res_obj,field_link='order_id',context={}):
        dict_exp_obj = {'purchase.order':'purchase_order','purchase.order.line':'purchase_order_line',
                        'kderp.other.expense':'kderp_other_expense','kderp.other.expense.line':'kderp_other_expense_line'}
        
        #po_budget_line_ids = []
        pol_link_dicts={}
        for exp in self.pool.get(res_obj).browse(cr,uid,ids,context):
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