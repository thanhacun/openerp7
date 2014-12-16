Create or replace view vwaccount_invoice_line as
	Select 
		account_analytic_id,
		invoice_id,TAX_BASE,
		case when tax_base='p' then ail.amount
		else case when tax_base='p_adv' then ail.advanced
		else case when tax_base='p_retention' then ail.retention
		else ail.price_subtotal end end end as amount
	from
		account_invoice_line ail 
	left join
		account_invoice ai on invoice_id=ai.id;
-- Update
-- 	account_analytic_account aaa
-- set 
-- 	vat_issued_amount=vwvatreceived.vat_issued_amount,
-- 	vat_issued_subtotal=vwvatreceived.vat_issued_subtotal
-- from (
Select 
	aaa.id as job_id,
	sum(coalesce(vwpayment_vat.issued_vat,0)*
				case when coalesce((select sum(coalesce(amount,0)) from vwaccount_invoice_line ail where invoice_id=ai.id),0)=0 then 0 else coalesce(ail.amount,0)/coalesce((select sum(coalesce(amount,0)) from vwaccount_invoice_line ail where invoice_id=ai.id),0) end) as vat_issued_amount,
	
	sum(coalesce(issued_subtotal,0)*
				case when coalesce((select sum(coalesce(amount,0)) from vwaccount_invoice_line ail where invoice_id=ai.id),0)=0 then 0 else coalesce(ail.amount,0)/coalesce((select sum(coalesce(amount,0)) from vwaccount_invoice_line ail where invoice_id=ai.id),0) end) as vat_issued_subtotal
from
	account_analytic_account aaa
left join 
	 vwaccount_invoice_line ail on aaa.id=ail.account_analytic_id
left join
	 account_invoice ai on invoice_id=ai.id
left join
	(Select
		payment_id,
		sum(kpvi.amount/(1+coalesce(tax_percent,0)/100)) as issued_subtotal,
		sum(case when coalesce(tax_percent,0)=0 then 0 else  kpvi.amount/(1+coalesce(tax_percent,0)/100)/tax_percent end) as issued_vat
	from 
		kderp_payment_vat_invoice kpvi 
	left join
		kderp_invoice ki on vat_invoice_id=ki.id
	where
		payment_id in (Select distinct invoice_id from account_invoice_line where account_analytic_id>0)
	group by
		payment_id) vwpayment_vat on ai.id=vwpayment_vat.payment_id and coalesce(vwpayment_vat.payment_id,0)>0
where
	ai.state not in ('draft','cancel')
group by
	aaa.id
-- ) vwvatreceived
-- where aaa.id=job_id