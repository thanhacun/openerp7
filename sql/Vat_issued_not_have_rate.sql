select sum(subtotal),name from 
(select pol.account_analytic_id as job_id ,pol.final_subtotal as subtotal,
						po.name as name 
						from kderp_supplier_vat_invoice ksvi 
						left join kderp_supplier_payment_vat_invoice_rel kspvir    on    kspvir.vat_invoice_id=ksvi.id
						left join kderp_supplier_payment ksp on ksp.id =kspvir.payment_id 
						left join purchase_order po on po.id =ksp.order_id 
						left join purchase_order_line pol on pol.order_id=po.id
						where ksp.state not in ('draft','cancel')  and ksvi.date between '2013-1-1' and '2013-12-31'  
						and pol.account_analytic_id=(select id from account_analytic_account where code='HE13-0008' )
						group by pol.account_analytic_id ,po.name , pol.sequence,pol.final_subtotal 
					Union all
						select koel.account_analytic_id as job_id ,koel.amount as subtotal,koe.name as name from kderp_supplier_vat_invoice ksvi
						left join kderp_supplier_payment_expense_vat_invoice_rel kspevir  on    kspevir.vat_invoice_id=ksvi.id 
						left join kderp_supplier_payment_expense kspe on  kspe.id =kspevir.payment_expense_id 
						left join kderp_other_expense koe on koe.id=kspe.expense_id 
						left join kderp_other_expense_line koel on koel.expense_id=koe.id
						left join account_analytic_account aaa on aaa.id=koel .account_analytic_id
						where kspe.state not in ('draft','cancel')  and ksvi.date  between '2013-1-1' and '2013-12-31' 
						and  koel.account_analytic_id =(select id from account_analytic_account where code='HE13-0008' )
						 group by  koel.account_analytic_id,koe.name,koel.amount,koel.id
)qr
group by name
order by name