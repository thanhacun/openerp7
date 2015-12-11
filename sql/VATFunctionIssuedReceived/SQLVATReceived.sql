﻿CREATE OR REPLACE FUNCTION funJobVATReceived(fromDate date, toDate date, states varchar[])
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
			LEFT JOIN purchase_order po on order_id = po.id
			left join account_analytic_account aaa on pol.ACCOUNT_ANALYTIC_ID = aaa.id
			left join (Select
					--Rate * amount
					KSP.ORDER_ID,
					SUM(
					case when coalesce(vwrate.ksp_id,0)=0 THEN 1 else coalesce(vwrate.rate,0) end * 
					case when coalesce(tax_base,'p')='p' then coalesce(amount,0) else 
					case when coalesce(tax_base,'p')='all' then coalesce(amount,0) + coalesce(advanced_amount,0) + coalesce(retention_amount,0) else 
					case when coalesce(tax_base,'p')='p_adv' then abs(coalesce(advanced_amount,0)) else abs(coalesce(retention_amount,0)) end end end) as subtotal_vat_amount
				FROM kderp_supplier_payment ksp		
				LEFT JOIN kderp_payment_supplier_rate vwrate ON ksp.id = vwrate.ksp_id
				WHERE
					EXISTS(select ksvi.id from  kderp_supplier_payment_vat_invoice_rel kspvir LEFT JOIN  kderp_supplier_vat_invoice ksvi on kspvir.vat_invoice_id=ksvi.id where
						kspvir.payment_id=ksp.id  and ksvi.date between fromDate and toDate) and
					ksp.state not in ('draft','cancel')
				GROUP BY
					KSP.ORDER_ID) vwvat on po.id = vwvat.order_id
			where 
				po.state not in ('draft','cancel') and coalesce(allocate_order,False)=False and coalesce(vwvat.ORDER_ID,0)>0 and aaa.state = any(states)
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
			left join account_analytic_account aaa on pol.ACCOUNT_ANALYTIC_ID = aaa.id
			LEFT JOIN purchase_order po on order_id = po.id
			where 
				po.state not in ('draft','cancel') and coalesce(allocate_order,False)=True and
				po.date_order between fromDate and toDate and aaa.state = any(states)
			GROUP BY	
				pol.ACCOUNT_ANALYTIC_ID
			Union all
			SELECT 	
				koel.ACCOUNT_ANALYTIC_ID,
				CASE WHEN COALESCE(amount_untaxed,0)=0 THEN 0 ELSE SUM(amount)/amount_untaxed END*vwvat.subtotal_vat_amount AS received_subtotal
			FROM kderp_other_expense_line koel
			left join account_analytic_account aaa on koel.ACCOUNT_ANALYTIC_ID = aaa.id
			LEFT JOIN kderp_other_expense koe on expense_id = koe.id
			left join (Select
					--Rate * amount
					KSPe.expense_id,
					SUM(coalesce(amount,0)) as subtotal_vat_amount
				FROM kderp_supplier_payment_expense kspe		
				LEFT JOIN kderp_payment_supplier_expense_rate vwrate ON kspe.id = vwrate.kspe_id
				WHERE
					EXISTS(select ksvi.id from kderp_supplier_payment_expense_vat_invoice_rel kspevir LEFT JOIN kderp_supplier_vat_invoice ksvi on kspevir.vat_invoice_id=ksvi.id where kspe.id = kspevir.payment_expense_id  and ksvi.date between fromDate and toDate) and
					kspe.state not in ('draft','cancel')
				GROUP BY
					KSPe.expense_id) vwvat on koe.id = vwvat.expense_id
			where 
				koe.state not in ('draft','cancel') and coalesce(vwvat.expense_id,0)>0 and expense_type not in ('prepaid','fixed_asset','monthly_expense') and aaa.state = any(states)
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
			left join account_analytic_account aaa on koel.ACCOUNT_ANALYTIC_ID = aaa.id
			LEFT JOIN kderp_other_expense koe on expense_id = koe.id
			where 
				koe.state not in ('draft','cancel') and expense_type ='monthly_expense' and koe.date between fromDate and toDate and aaa.state = any(states)
			Group by
				koe.id,
				koel.ACCOUNT_ANALYTIC_ID
		) vwcombine
		group by
			ACCOUNT_ANALYTIC_ID;
END;
$$ LANGUAGE plpgsql;

Select * from funJobVATReceived('2015-01-01','2015-12-31',array ['doing','done']);
Select * from funJobVATReceived('2010-01-01','2015-12-01',array ['doing','done','closed','closed_temp','cancel']);