Select 
	distinct
	ksp.name,
	aaa.code
from
	kderp_supplier_payment ksp
left join
	purchase_order_line pol on ksp.order_id=pol.order_id
left join
	purchase_order po on pol.order_id=po.id
left join
	account_analytic_account aaa on pol.account_analytic_id=aaa.id
where
	ksp.state not in ('draft','cancel') and po.state not in ('draft','cancel') and coalesce(base_on_line,False)=False
Union
Select 
	distinct
	ksp.name,
	aaa.code
from
	kderp_supplier_payment ksp
left join
	kderp_supplier_payment_line kspl on ksp.id=kspl.supplier_payment_id
left join
	purchase_order po on order_id=po.id
left join
	account_analytic_account aaa on kspl.account_analytic_id=aaa.id
where
	ksp.state not in ('draft','cancel') and po.state not in ('draft','cancel') and coalesce(ksp.base_on_line,False)=True
Union
Select 
	distinct
	kspe.name,
	aaa.code
from
	kderp_supplier_payment_expense kspe
left join
	kderp_other_expense_line koel on kspe.expense_id=koel.expense_id
left join
	account_analytic_account aaa on koel.account_analytic_id=aaa.id
left join
	kderp_other_expense koe on kspe.expense_id = koe.id
where
	kspe.state not in ('draft','cancel') and koe.state not in ('draft','cancel') 