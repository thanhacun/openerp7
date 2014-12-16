-- Function: fnpo_compute(integer, integer, date)

-- DROP FUNCTION fnpo_compute(integer, integer, date);
-- 
-- CREATE OR REPLACE FUNCTION fnpo_compute(fromcurr integer, tocurr integer, datecurr date)
--   RETURNS numeric AS
-- '                                Select  case when $1=$2 then 1 else (Select rate/(Select rate from res_currency_rate  where currency_id  =$2 and name=(Select max(name) as name                                from res_currency_rate where currency_id =$2 and name<=$3)) from res_currency_rate where ($1=$2) or (currency_id=$1 and 
-- name=(Select max(name) as name                                from res_currency_rate where currency_id=$1 and name<=$3))) end;                                '
--   LANGUAGE sql VOLATILE
--   COST 100;
-- ALTER FUNCTION fnpo_compute(integer, integer, date)
--   OWNER TO openerp;

--  Select * from res_currency
 
Select fnpo_compute(181,24,DATE '2015-02-16');
--Manual amount 662 260 000 662 260 000.0000000940635800 select 463582000 +198678000.000000028219074000000000000000000000
Select
	    kebl.id,
	    kebl.budget_id,
	    kebl.account_analytic_id,
	    expense_amount as amount,
	    vwcombine_manual.amount_currency,	    
	    vwcombine_manual.amount_tax,
	    sum(vwcombine_manual.payment_amount) as payment_amount
from
	kderp_expense_budget_line kebl
left join
	(Select 
		po.id as po_id,
		vwpol.budget_id,
		vwpol.account_analytic_id,	
		amount_currency,
		expense_amount,
		vwpol.amount_tax,
		sum(coalesce(kspl.amount*coalesce(fnpo_compute(ksp.currency_id,company_curr,po.date_order),0))) as payment_amount
	from
		purchase_order po 
	left join
		kderp_supplier_payment ksp on po.id=order_id 
	left join
		(Select 
			order_id,
			budget_id,
			account_analytic_id,
			sum(coalesce(final_subtotal,0)) as amount_currency,
			sum(coalesce(amount_company_curr,0)) as expense_amount,
			sum(coalesce(pol.amount_tax,0)) as amount_tax
		from
			purchase_order_line pol
		group by
			budget_id,
			account_analytic_id,
			order_id) vwpol on po.id=vwpol.order_id
	left join
		kderp_supplier_payment_line kspl on  ksp.id=supplier_payment_id and vwpol.budget_id=kspl.budget_id and vwpol.account_analytic_id=kspl.account_analytic_id
	left join
		(Select currency_id as company_curr from res_company limit 1) vwtemp on True
	where
		coalesce(ksp.base_on_line,False)=True and ksp.state not in ('draft','cancel') and po.state not in ('draft','cancel','done')
	group by
		vwpol.budget_id,
		vwpol.account_analytic_id,
		po.id,
		expense_amount,	
		vwpol.amount_tax,
		amount_currency
Union
	Select 
		po.id as po_id,
		budget_id,
		pol.account_analytic_id,		
		sum(coalesce(final_subtotal,0)) as amount_currency,
		sum(coalesce(amount_company_curr,0)) as expense_amount,
		sum(coalesce(pol.amount_tax,0)) as amount_tax,
		sum(pol.amount_company_curr* case  when coalesce(final_price,0)=0 then 0 else sub_total/final_price end ) as payment_amount		
	from
		purchase_order po 	
	left join
		product_pricelist pl on pricelist_id=pl.id
	left join
		kderp_supplier_payment ksp  on po.id=order_id 
	left join
		purchase_order_line pol on po.id=pol.order_id
	left join
		(Select currency_id as company_curr from res_company limit 1) vwtemp on True
	where
		coalesce(ksp.base_on_line,False)=False and po.state not in ('draft','cancel') and po.id  in (Select 

					order_id 
				from 
					kderp_supplier_payment 
				left join
					purchase_order po on order_id=po.id
				where 
					coalesce(base_on_line,False)=True and po.state not in ('draft','cancel','done'))
		
	group by
		budget_id,
		pol.account_analytic_id,
		po.id) vwcombine_manual on expense_id=po_id and kebl.budget_id=vwcombine_manual.budget_id and kebl.account_analytic_id=vwcombine_manual.account_analytic_id
Where
	expense_obj='purchase.order' and coalesce(po_id,0)>0
Group by
	kebl.id,
	vwcombine_manual.amount_currency,
	expense_amount,
	vwcombine_manual.amount_tax
-- 
-- Select
-- 	    kebl.id,
-- 	    kebl.budget_id,
-- 	    kebl.account_analytic_id,
-- 	    sum(coalesce(amount_company_curr,0)) as amount,
-- 	    sum(coalesce(final_subtotal,0)) as amount_currency,
-- 	    sum(coalesce(pol.amount_tax,0)) as amount_tax,
-- 	    sum(coalesce(amount_company_curr,0))*coalesce(payment_percentage,0) as payment_amount
-- 	from
-- 	    kderp_expense_budget_line kebl
-- 	left join
-- 	    purchase_order_line pol on expense_id=order_id and kebl.budget_id=pol.budget_id and kebl.account_analytic_id=pol.account_analytic_id
-- 	left join
-- 	    purchase_order po on pol.order_id=po.id
-- 	where
-- 	    expense_obj='purchase.order' and   po.id  in (Select 
-- 				--distinct 
-- 				order_id 
-- 			from 
-- 				kderp_supplier_payment 
-- 			left join
-- 				purchase_order po on order_id=po.id
-- 			where 
-- 				coalesce(base_on_line,False)=True and po.state not in ('draft','cancel','done'))
-- 	group by
-- 	    kebl.id,
-- 	    po.id;
-- 
-- Select
-- 	    kebl.id,
-- 	    kebl.budget_id,
-- 	    kebl.account_analytic_id,
-- 	    sum(coalesce(amount_company_curr,0)) as amount,
-- 	    sum(coalesce(final_subtotal,0)) as amount_currency,
-- 	    sum(coalesce(pol.amount_tax,0)) as amount_tax,
-- 	    sum(coalesce(amount_company_curr,0))*coalesce(payment_percentage,0) as payment_amount
-- 	from
-- 	    kderp_expense_budget_line kebl
-- 	left join
-- 	    purchase_order_line pol on expense_id=order_id and kebl.budget_id=pol.budget_id and kebl.account_analytic_id=pol.account_analytic_id
-- 	left join
-- 	    purchase_order po on pol.order_id=po.id
-- 	where
-- 	    expense_obj='purchase.order' and
-- 	group by
-- 	    kebl.id,
-- 	    po.id;

-- ################################################ New Alread Revised #####################################################
Select
                            kebl.id,
                            kebl.budget_id,
                            kebl.account_analytic_id,
                            expense_amount as amount,
                            vwcombine_manual.amount_currency,        
                            vwcombine_manual.amount_tax,
                            sum(vwcombine_manual.payment_amount) as payment_amount
                    from
                        kderp_expense_budget_line kebl
                    left join
                        (Select 
                            po.id as po_id,
                            vwpol.budget_id,
                            vwpol.account_analytic_id,    
                            amount_currency,
                            expense_amount,
                            vwpol.amount_tax,
                            sum(coalesce(kspl.amount*coalesce(fnpo_compute(ksp.currency_id,company_curr,po.date_order),0))) as payment_amount
                        from
                            purchase_order po 
                        left join
                            kderp_supplier_payment ksp on po.id=order_id and ksp.state not in ('draft','cancel') and coalesce(ksp.base_on_line,False)=True
                        left join
                            (Select 
                                order_id,
                                budget_id,
                                account_analytic_id,
                                sum(coalesce(final_subtotal,0)) as amount_currency,
                                sum(coalesce(amount_company_curr,0)) as expense_amount,
                                sum(coalesce(pol.amount_tax,0)) as amount_tax
                            from
                                purchase_order_line pol
                            where
                                    (order_id,
                                    budget_id,
                                    account_analytic_id) in (Select kebl.expense_id,kebl.budget_id,kebl.account_analytic_id from kderp_expense_budget_line kebl where expense_obj='purchase.order' and kebl.id in (%s)) 
                            group by
                                budget_id,
                                account_analytic_id,
                                order_id) vwpol on po.id=vwpol.order_id
                        left join
                            kderp_supplier_payment_line kspl on  ksp.id=supplier_payment_id and vwpol.budget_id=kspl.budget_id and vwpol.account_analytic_id=kspl.account_analytic_id
                        left join
                            (Select currency_id as company_curr from res_company limit 1) vwtemp on True
                        where
                            po.state not in ('draft','cancel','done')
                        group by
                            vwpol.budget_id,
                            vwpol.account_analytic_id,
                            po.id,
                            expense_amount,    
                            vwpol.amount_tax,
                            amount_currency
                    Union
                        Select 
                            po.id as po_id,
                            budget_id,
                            pol.account_analytic_id,        
                            sum(coalesce(final_subtotal,0)) as amount_currency,
                            sum(coalesce(amount_company_curr,0)) as expense_amount,
                            sum(coalesce(pol.amount_tax,0)) as amount_tax,
                            sum(pol.amount_company_curr* case  when coalesce(final_price,0)=0 then 0 else sub_total/final_price end ) as payment_amount        
                        from
                            purchase_order po     
                        left join
                            product_pricelist pl on pricelist_id=pl.id
                        left join
                            kderp_supplier_payment ksp on po.id=order_id and coalesce(ksp.base_on_line,False)=False and ksp.state not in ('draft','cancel')
                        left join
                            purchase_order_line pol on po.id=pol.order_id
                        left join
                            (Select currency_id as company_curr from res_company limit 1) vwtemp on True
                        where
                                    (pol.order_id,
                                    pol.budget_id,
                                    pol.account_analytic_id) in (Select kebl.expense_id,kebl.budget_id,kebl.account_analytic_id from kderp_expense_budget_line kebl where expense_obj='purchase.order' and kebl.id in (%s))
                            and
                                    po.state not in ('draft','cancel') 
                            and 
                                    po.id  in (Select                    
                                        order_id 
                                    from 
                                        kderp_supplier_payment 
                                    left join
                                        purchase_order po on order_id=po.id
                                    where 
                                        po.id in (Select kebl.expense_id from kderp_expense_budget_line kebl where expense_obj='purchase.order' and kebl.id in (%s)) and
                                        coalesce(base_on_line,False)=True and po.state not in ('draft','cancel','done'))
                            
                        group by
                            budget_id,
                            pol.account_analytic_id,
                            po.id) vwcombine_manual on expense_id=po_id and kebl.budget_id=vwcombine_manual.budget_id and kebl.account_analytic_id=vwcombine_manual.account_analytic_id
                    Where
                        expense_obj='purchase.order' and coalesce(po_id,0)>0 and kebl.id in (%s) 
                    Group by
                        kebl.id,
                        vwcombine_manual.amount_currency,
                        expense_amount,
                        vwcombine_manual.amount_tax
    Union
                    Select
                            kebl.id,
                            kebl.budget_id,
                            kebl.account_analytic_id,
                            sum(coalesce(amount_company_curr,0)) as amount,
                            sum(coalesce(final_subtotal,0)) as amount_currency,
                            sum(coalesce(pol.amount_tax,0)) as amount_tax,
                            sum(coalesce(amount_company_curr,0))*coalesce(payment_percentage,0) as payment_amount
                        from
                            kderp_expense_budget_line kebl
                        left join
                            purchase_order_line pol on expense_id=order_id and kebl.budget_id=pol.budget_id and kebl.account_analytic_id=pol.account_analytic_id
                        left join
                            purchase_order po on pol.order_id=po.id
                        where
                            expense_obj='purchase.order' and kebl.id in (%s) and 
                             (po.state='done' or
                                po.id not in (Select                                         
                                                order_id 
                                            from 
                                                kderp_supplier_payment 
                                            left join
                                                purchase_order po on order_id=po.id
                                            where 
                                                coalesce(base_on_line,False)=True and po.state not in ('draft','cancel','done'))) 
                        group by
                            kebl.id,
                            po.id
                        Union
                        Select
                            kebl.id,
                            kebl.budget_id,
                            kebl.account_analytic_id,
                            sum(coalesce(amount_company_curr,0)) as amount,
                            sum(coalesce(koel.amount,0)) as amount_currency,
                            0 as amount_tax,
                            sum(coalesce(amount_company_curr,0))*coalesce(payment_percentage,0) as payment_amount
                        from
                            kderp_expense_budget_line kebl
                        left join
                            kderp_other_expense_line koel on kebl.expense_id=koel.expense_id and kebl.budget_id=koel.budget_id and kebl.account_analytic_id=koel.account_analytic_id
                        left join
                            kderp_other_expense koe on koel.expense_id=koe.id
                        where
                            expense_obj='kderp.other.expense' and kebl.id in (%s)
                        group by
                            kebl.id,
                            koe.id