CREATE OR REPLACE FUNCTION funJobVATReceivedDirect(fromDate date, toDate date, states varchar[])
RETURNS TABLE (job_id integer, received_amount float) AS $$
BEGIN
    RETURN QUERY Select
			ACCOUNT_ANALYTIC_ID,
			sum(received_subtotal)::float as received_subtotal
		from
			(
			SELECT 	
				pol.ACCOUNT_ANALYTIC_ID,
				vwvat.subtotal_vat_amount* CASE WHEN COALESCE(FINAL_PRICE,0)=0 THEN 0 ELSE SUM(final_subtotal)/FINAL_PRICE END AS received_subtotal
			FROM purchase_order_line pol
			left join product_product pp on product_id = pp.id
			left join account_budget_post abp on pp.budget_id = abp.id
			left join kderp_budget_category kbc on budget_categ_id = kbc.id
			LEFT JOIN purchase_order po on order_id = po.id
			left join account_analytic_account aaa on pol.ACCOUNT_ANALYTIC_ID = aaa.id
			left join (Select
					--Rate * amount
					KSP.ORDER_ID,
					SUM(coalesce(ksvi.subtotal* ksvi.rate, 0)) as subtotal_vat_amount
				FROM 
					kderp_supplier_payment ksp		
				LEFT JOIN
					kderp_supplier_payment_vat_invoice_rel kspvir ON ksp.id = kspvir.payment_id
				LEFT JOIN  
					kderp_supplier_vat_invoice ksvi on kspvir.vat_invoice_id = ksvi.id
				WHERE
					ksvi.date between fromDate and toDate and
					ksp.state not in ('draft','cancel')
				GROUP BY
					KSP.ORDER_ID) vwvat on po.id = vwvat.order_id 
			where 
				po.state not in ('draft','cancel') and 
				coalesce(allocate_order,False)=False and 
				coalesce(vwvat.ORDER_ID,0)>0 and 
				aaa.state = any(states) and 
				kbc.cat_code in ('material','direct_cost','sub_contractor','electrical','site_expense','mechanial')
			GROUP BY	
				po.id,
				vwvat.subtotal_vat_amount,
				pol.ACCOUNT_ANALYTIC_ID
			Union All
			--PO Allocated
			SELECT 	
				pol.ACCOUNT_ANALYTIC_ID,
				sum(AFTER_NEGOTIATION) as received_subtotal
			FROM purchase_order_line pol
			left join product_product pp on product_id = pp.id
			left join account_budget_post abp on pp.budget_id = abp.id
			left join kderp_budget_category kbc on budget_categ_id = kbc.id
			left join account_analytic_account aaa on pol.ACCOUNT_ANALYTIC_ID = aaa.id
			LEFT JOIN purchase_order po on order_id = po.id
			where 
				po.state not in ('draft','cancel') and coalesce(allocate_order,False)=True and
				po.date_order between fromDate and toDate and aaa.state = any(states) and
				kbc.cat_code in ('material','direct_cost','sub_contractor','electrical','site_expense','mechanial')
			GROUP BY	
				pol.ACCOUNT_ANALYTIC_ID
			Union all
			SELECT 	
				koel.ACCOUNT_ANALYTIC_ID,
				CASE WHEN COALESCE(amount_untaxed,0)=0 THEN 0 ELSE SUM(amount)/amount_untaxed END*vwvat.subtotal_vat_amount AS received_subtotal
			FROM kderp_other_expense_line koel
			left join account_budget_post abp on budget_id = abp.id
			left join kderp_budget_category kbc on budget_categ_id = kbc.id
			left join account_analytic_account aaa on koel.ACCOUNT_ANALYTIC_ID = aaa.id
			LEFT JOIN kderp_other_expense koe on expense_id = koe.id
			left join (Select
					--Rate * amount
					KSPe.expense_id,
					SUM(coalesce(ksvi.subtotal* ksvi.rate, 0)) as subtotal_vat_amount
				FROM 
					kderp_supplier_payment_expense kspe		
				left join
					kderp_supplier_payment_expense_vat_invoice_rel kspevir on kspe.id = kspevir.payment_expense_id
				LEFT JOIN 
					kderp_supplier_vat_invoice ksvi on kspevir.vat_invoice_id=ksvi.id
				WHERE
					ksvi.date between fromDate and toDate and
					kspe.state not in ('draft','cancel')
				GROUP BY
					KSPe.expense_id) vwvat on koe.id = vwvat.expense_id
			where 
				koe.state not in ('draft','cancel') and coalesce(vwvat.expense_id,0)>0 and expense_type not in ('prepaid','fixed_asset','monthly_expense') and aaa.state = any(states) and
				kbc.cat_code in ('material','direct_cost','sub_contractor','electrical','site_expense','mechanial')
			Group by
				koe.id,
				koel.ACCOUNT_ANALYTIC_ID,
				vwvat.subtotal_vat_amount
			UNION ALL
			--Expense Allocated
			SELECT 	
				koel.ACCOUNT_ANALYTIC_ID,
				SUM(amount) AS received_subtotal
			FROM kderp_other_expense_line koel
			left join account_budget_post abp on budget_id = abp.id
			left join kderp_budget_category kbc on budget_categ_id = kbc.id
			left join account_analytic_account aaa on koel.ACCOUNT_ANALYTIC_ID = aaa.id
			LEFT JOIN kderp_other_expense koe on expense_id = koe.id
			where 
				koe.state not in ('draft','cancel') and expense_type ='monthly_expense' and koe.date between fromDate and toDate and aaa.state = any(states) and
				kbc.cat_code in ('material','direct_cost','sub_contractor','electrical','site_expense','mechanial')
			Group by
				koe.id,
				koel.ACCOUNT_ANALYTIC_ID
		) vwcombine
		group by
			ACCOUNT_ANALYTIC_ID;
END;
$$ LANGUAGE plpgsql;

-- Select * from funJobVATReceivedDirect('2016-01-01','2016-12-31',array ['doing','done']);
-- Select * from funJobVATReceived('2010-01-01','2015-12-01',array ['doing','done','closed','closed_temp','cancel']);