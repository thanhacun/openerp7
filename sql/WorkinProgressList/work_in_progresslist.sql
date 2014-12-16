--create or replace view vwbudget_category as
Select 
	abp.id as budget_id,
	case when 
		bc.name is null 
	then
		case when 
			code in ('5700','5800','5910','7000','8500') then 'gse'
		else
			case when 
				code in ('5900','6000') then 'kfp'
			else
				case when 
					code in ('8000','8901') then 'profit'
				end
			end
		end
	else
		bc.cat_code
	end as category
from 
	account_budget_post abp
left join
	kderp_budget_category bc on budget_categ_id = bc.id and bc.cat_code in ('material','sub_contractor','site_expense')
where (bc.name is not null or code in ('5700','5800','5910','7000','5900','6000','8000','8901','8500'));

--Create or replace view kderp_project_workinprogresslist_report as
Select
	aaa.id,
	
	sum(case when category='material' then coalesce(planned_amount,0) else 0 end) as material_planned_amount,
	sum(case when category='site_expense' then coalesce(planned_amount,0) else 0 end) as site_expense_planned_amount,
	sum(case when category='sub_contractor' then coalesce(planned_amount,0) else 0 end) as sub_contractor_planned_amount,
	sum(case when category='gse' then coalesce(planned_amount,0) else 0 end) as gse_planned_amount,
	sum(case when category='kfp' then coalesce(planned_amount,0) else 0 end) as kfp_planned_amount,
	sum(case when category='profit' then coalesce(planned_amount,0) else 0 end) as profit_planned_amount,
	
	sum(case when category='material' then coalesce(kebl.amount,0) else 0 end) as material_order_vnd,
	sum(case when category='site_expense' then coalesce(kebl.amount,0) else 0 end) as site_expense_order_vnd,
	sum(case when category='sub_contractor' then coalesce(kebl.amount,0) else 0 end) as sub_contractor_order_vnd,
	sum(case when category='gse' then coalesce(kebl.amount,0) else 0 end) as gse_order_vnd,
	sum(case when category='kfp' then coalesce(kebl.amount,0) else 0 end) as kfp_order_vnd,
	sum(case when category='profit' then coalesce(kebl.amount,0) else 0 end) as profit_order_vnd,
	
	sum(case when category='material' then coalesce(payment_amount,0) else 0 end) as material_payment_amount,
	sum(case when category='site_expense' then coalesce(payment_amount,0) else 0 end) as site_expense_payment_amount,
	sum(case when category='sub_contractor' then coalesce(payment_amount,0) else 0 end) as sub_contractor_payment_amount,
	sum(case when category='gse' then coalesce(payment_amount,0) else 0 end) as gse_payment_amount,
	sum(case when category='kfp' then coalesce(payment_amount,0) else 0 end) as kfp_payment_amount,
	sum(case when category='profit' then coalesce(payment_amount,0) else 0 end) as profit_payment_amount
from 
	account_analytic_account aaa
left join
	kderp_budget_data kbd on aaa.id=account_analytic_id
left join
	vwbudget_category vwbc on kbd.budget_id=vwbc.budget_id
left join
	kderp_expense_budget_line kebl on aaa.id= kebl.account_analytic_id and kbd.budget_id=kebl.budget_id
Group by
	aaa.id;