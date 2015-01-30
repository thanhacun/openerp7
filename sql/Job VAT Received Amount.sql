Update account_analytic_account  aaa 
set 
	vat_received_amount=(vwvat_temp.vat_received_amount),
	vat_received_subtotal=(vwvat_temp.vat_received_subtotal)
from	(
	Select
		account_analytic_id as job_id,
		sum(vat_received_subtotal) as vat_received_subtotal,
		sum(vat_received_amount) as vat_received_amount
	from
		(Select 
			vwtemp_job_per.account_analytic_id,
			sum(job_per*vat_amount*po_final_exrate * case when coalesce(po_id,0)=0 then 1 else rate end) as vat_received_amount,
			sum(job_per*subtotal_vat_amount*po_final_exrate * case when coalesce(po_id,0)=0 then 1 else rate end) as vat_received_subtotal
		from
			purchase_order po
		left join
			product_pricelist pp on pricelist_id = pp.id
		left join
			(Select 
				po.id as po_id,
				max(rcr.name) as max_date
			from 
				purchase_order po
			left join
				product_pricelist pp on po.pricelist_id = pp.id
			left join
				res_currency_rate rcr on pp.currency_id=rcr.currency_id and po.date_order>=rcr.name
			where
				pp.currency_id<>(Select currency_id from res_company rc limit 1)
				and po.id in (Select distinct order_id from purchase_order_line)
			group by
				po.id) vwpo_rate on po.id = po_id
		left join
			res_currency_rate rcr on max_date = rcr.name and pp.currency_id = rcr.currency_id
		left join
			(Select 
			    pol.order_id,
			    pol.account_analytic_id,
			    case when 
				coalesce(grant_total,0)=0 then 0
			    else
				sum(coalesce(final_subtotal,0))/grant_total end as job_per
			from 
			    purchase_order_line pol
			left join
			    purchase_order po on order_id = po.id
			left join
			    (Select
				order_id,
				sum(coalesce(final_subtotal,0)) as grant_total
			    from 
				purchase_order_line pol
			    where
				order_id in (Select distinct order_id from purchase_order_line)
			    group by
				order_id) vwgrant_total on pol.order_id=vwgrant_total.order_id
			where
			    pol.order_id in (Select distinct order_id from purchase_order_line ) and 
			    po.state not in ('draft','cancel')
			group by
			    pol.order_id,
			    pol.account_analytic_id,
			    grant_total) vwtemp_job_per on po.id = order_id			

		Group by
			vwtemp_job_per.account_analytic_id
		Union
		Select 
			vwtemp_job_per.account_analytic_id,
			sum(job_per * vat_amount *  case when coalesce(exp_id,0)=0 then 1 else rate end) as vat_received_amount,
			sum(job_per * subtotal_vat_amount * case when coalesce(exp_id,0)=0 then 1 else rate end) as vat_received_subtotal
		from
			kderp_other_expense koe
		left join
			(Select 
				koe.id as exp_id,
				max(rcr.name) as max_date
			from 
				kderp_other_expense koe
			left join
				res_currency_rate rcr on koe.currency_id=rcr.currency_id and koe.date>=rcr.name
			where
				koe.currency_id<>(Select currency_id from res_company rc limit 1)
				and 
				koe.id in (Select distinct expense_id from kderp_other_expense_line )
			group by
				koe.id) vwexp_rate on koe.id = exp_id
		left join
			res_currency_rate rcr on max_date = rcr.name and koe.currency_id = rcr.currency_id	
		left join
			(Select 
			    koel.expense_id,
			    koel.account_analytic_id,
			    case when 
				coalesce(grant_total,0)=0 then 0
			    else
				sum(coalesce(amount,0))/grant_total end as job_per
			from 
			    kderp_other_expense_line koel
			left join
			    kderp_other_expense koe on expense_id = koe.id
			left join
			    (Select
				expense_id,
				sum(coalesce(amount,0)) as grant_total
			    from 
				kderp_other_expense_line koel
			    where
				expense_id in (Select distinct expense_id from kderp_other_expense_line )
			    group by
				expense_id) vwgrant_total on koel.expense_id = vwgrant_total.expense_id
			where
			    koel.expense_id in (Select distinct expense_id from kderp_other_expense_line ) and 
			    koe.state not in ('draft','cancel')
			group by
			    koel.expense_id,
			    koel.account_analytic_id,
			    grant_total) vwtemp_job_per on koe.id = expense_id

		Group by
			vwtemp_job_per.account_analytic_id) vwcombine
	group by 
		account_analytic_id
) vwvat_temp
where aaa.id=job_id;

-- update account_analytic_account set vat_received_subtotal =0 where code='PE14-0001'