--Begin;
Update kderp_budget_data kbdu set 

    expense_amount=vwtemp.expense_amount,
    paid_amount=vwtemp.paid_amount,
    expense_with_contract=vwtemp.po_withcontract,
    expense_without_contract=vwtemp.po_withoutcontract
from 
    (Select 
                            kbd.id,
                            planned_amount,
                            sum(coalesce(amount,0)) as expense_amount,
                            sum(coalesce(payment_amount,0)) as paid_amount,
                            sum(case when coalesce(without_contract,False)=False then coalesce(amount,0) else 0 end) as po_withcontract,
                            sum(case when coalesce(without_contract,False)=True then coalesce(amount,0) else 0 end) as po_withoutcontract                            
                        from 
                            kderp_budget_data kbd 
                        left join 
                            kderp_expense_budget_line kebl on kbd.account_analytic_id=kebl.account_analytic_id and kbd.budget_id = kebl.budget_id
                        group by
                            kbd.id) vwtemp
    where 
	vwtemp.id=kbdu.id;
--rollback