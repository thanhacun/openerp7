CREATE OR REPLACE FUNCTION funJobVATIssued(fromDate date, toDate date, states varchar[])
RETURNS TABLE (job_id integer, issued_amount float) AS $$
BEGIN
    RETURN QUERY 
    Select 
	aaa.id as job_id,
	sum(coalesce(issued_subtotal,0)* case when coalesce(total,0)=0 then 0 else coalesce(amount_currency,0)/total end) as vat_issued_subtotal
from
	account_analytic_account aaa
left join     
	kderp_quotation_contract_project_line kqcpl on aaa.id = account_analytic_id
left join
	(select 
	    contract_id,
	    sum(coalesce(amount_currency,0)) as total
	from 
	    kderp_quotation_contract_project_line kqcpls	
	group by
	    contract_id) astemp on  kqcpl.contract_id = astemp.contract_id
left join
	account_invoice ai on kqcpl.contract_id = ai.contract_id
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
		ki.date BETWEEN fromDate
			AND toDate
	group by
	    payment_id) vwpayment_vat on ai.id=vwpayment_vat.payment_id and coalesce(vwpayment_vat.payment_id,0)>0
	where
		aaa.state =any(states)
	group by
		aaa.id;
END;
$$ LANGUAGE plpgsql;

Select * from funJobVATIssued('2011-01-01','2015-12-31',array ['doing','done']) ;
Select * from funJobVATIssued('2010-01-01','2015-02-01',array ['doing','done','closed','closed_temp','cancel']);
