--drop function funSummaryWorkingProcessPre(getDate date);
CREATE OR REPLACE FUNCTION funSummaryWorkingProcessPre(getDate date)
RETURNS TABLE (area_id integer, em varchar(3),accumlated float) AS $$
BEGIN
    RETURN QUERY
-- TODO: Need to convert if using currency different VND
Select
		areaid as area_id,
		job_type as em,
		(sum(bigjob)::float + sum(otherjob)::float +  sum(own_internal_support)::float + sum(other_internal_support)::float)::float as accumulated
from
	(Select 
		job_type,
		kjca.area_id as areaid,
		sum(case when job_scale='00-big_job' then 
			coalesce(issued_subtotal,0)* case when coalesce(total,0)=0 then 0 else coalesce(kcja.amount,0)/total end
		else 0 end) as bigjob,
		sum(case when job_scale='00-big_job' then 0 else 
			coalesce(issued_subtotal,0)* case when coalesce(total,0)=0 then 0 else coalesce(kcja.amount,0)/total end	
		end) as otherjob,
		0 as own_internal_support,
		sum(case when kcja.control_support='support_area' and kjca.area_id <> kcja.area_id then 
			coalesce(issued_subtotal,0)* case when coalesce(total,0)=0 then 0 else coalesce(kcja.amount,0)/total end
		else 0 end) as other_internal_support
	from
		account_analytic_account aaa
	left join
		kderp_job_control_area kjca on aaa.id = kjca.job_id
	left join     
		kderp_contract_job_area kcja on aaa.id = kcja.job_id
	left join
		(select 
		    contract_id,		   
		    sum(coalesce(amount,0)) as total
		from 
		    kderp_contract_job_area kcja	
		group by
		    contract_id,
		    kcja.area_id,
		    job_id) astemp on  kcja.contract_id = astemp.contract_id
	left join
		account_invoice ai on kcja.contract_id = ai.contract_id and ai.state not in ('draft','cancel')
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
	 		ki.date < getDate
		group by
		    payment_id) vwpayment_vat on ai.id=vwpayment_vat.payment_id and coalesce(vwpayment_vat.payment_id,0)>0
	where
		aaa.state not in ('cancel','closed') and not general_expense 
	group by
		job_type,		
		kjca.area_id
	Union All
	Select 	
		aaa.job_type as job_type,
		kcja.area_id as areaid,
		0 as bigjob,
		0 as otherjob,
		sum(coalesce(issued_subtotal,0)* case when coalesce(total,0)=0 then 0 else coalesce(kcja.amount,0)/total end) as own_internal_support,
		0 as other_interal_support	
	from 
		account_analytic_account aaa 
	left join
		kderp_contract_job_area kcja on aaa.id = job_id
	left join
		(select 
		    contract_id,
		    sum(coalesce(amount,0)) as total
		from 
		    kderp_contract_job_area kcja	
		group by
		    contract_id,
		    kcja.area_id,
		    job_id) astemp on  kcja.contract_id = astemp.contract_id
	left join
		account_invoice ai on kcja.contract_id = ai.contract_id and ai.state not in ('draft','cancel')
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
	 		ki.date < getDate
		group by
		    payment_id) vwpayment_vat on ai.id=vwpayment_vat.payment_id and coalesce(vwpayment_vat.payment_id,0)>0
	where
		aaa.state not in ('cancel','closed') and not general_expense and kcja.control_support='support_area'
	group by
		job_type,		
		kcja.area_id) vwcombine
group by
		areaid,
		job_type;
END;
$$ LANGUAGE plpgsql;