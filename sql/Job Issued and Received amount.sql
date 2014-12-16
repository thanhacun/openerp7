select aaa.code as Job_Code,
	aaa.name as Job_Name ,
	rp.name as Client_Name,
	sum(coalesce(received_amount,0)) as Receive_Amount ,
	sum(coalesce(issued_amount,0)) as Issued_Amount 
   
 from account_analytic_account aaa   left join res_partner rp on aaa.partner_id=rp.id 
     Left Join ( 
	select aaa.id as  job_id,
	 qrpo.subtotal+sum(qrex.subtotal) as received_amount ,
	 0 as issued_amount from account_analytic_account aaa 
     left join (
	select aaa.id as job_id ,
	sum(pol.final_total) as subtotal from kderp_supplier_vat_invoice ksvi 
		left join kderp_supplier_payment_vat_invoice_rel kspvir    on    kspvir.vat_invoice_id=ksvi.id 
		left join kderp_supplier_payment ksp on ksp.id =kspvir.payment_id 
		left join purchase_order po on po.id =ksp.order_id 
		left join purchase_order_line pol on pol.order_id=po.id 
		left join account_analytic_account aaa on aaa.id=pol .account_analytic_id where ksp.state not in ('draft','cancel')
												and ksvi.date  between '2013-7-1' and '2013-12-31'group by aaa.id 
		)qrpo on qrpo.job_id=aaa.id 
     Left Join  (select koel.account_analytic_id as job_id ,
			koel.amount as subtotal,koe.name from kderp_supplier_vat_invoice ksvi 
			left join kderp_supplier_payment_expense_vat_invoice_rel kspevir  on    kspevir.vat_invoice_id=ksvi.id
			left join kderp_supplier_payment_expense kspe on kspe.id =kspevir.payment_expense_id 
			left join kderp_other_expense koe on koe.id=kspe.expense_id 
			left join kderp_other_expense_line koel on koel.expense_id=koe.id  
			left join account_analytic_account aaa on aaa.id=koel .account_analytic_id
			where kspe.state not in ('draft','cancel')  and ksvi.date  between '2013-7-1' and '2013-12-31'  group by  koel.account_analytic_id,koe.name,koel.amount
		) qrex on qrex.job_id=aaa.id group by aaa.id,aaa.code,qrpo.subtotal
     union 	(Select  aaa.id as job_id,
			0 as received_amount_po,
			sum(coalesce(ki.subtotal,0)*case when coalesce((select sum(coalesce(amount,0))
			from account_invoice_line ail where invoice_id=ai.id),0)=0 then 0 else coalesce(ail.amount,0)/coalesce((select sum(coalesce(amount,0))from 				account_invoice_line ail where invoice_id=ai.id),0) end) as issued_amount 
			From account_analytic_account aaa  left join account_invoice_line ail on ail.account_analytic_id=aaa.id  left join account_invoice ai on invoice_id=ai.id 			 left join kderp_payment_vat_invoice kpvi on ai.id = kpvi.payment_id 
			left join kderp_invoice ki on vat_invoice_id=ki.id where coalesce(kpvi.id,0)>0 and ai.state not in ('draft','cancel') 
			and ki.date  between '2013-7-1' and '2013-12-31'  group by aaa.id,aaa.code
		) )vwvat on aaa.id = vwvat.job_id 
     group by aaa.code,aaa.name,rp.name