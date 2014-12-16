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
(
	Select 
                        kspl.account_analytic_id,
                        sum(ksp.amount_tax*job_per*case when coalesce(ksp_id,0)=0 then 1 else coalesce(rate,0) end) as vat_received_amount,
                        sum(ksp.amount*job_per*case when coalesce(ksp_id,0)=0 then 1 else coalesce(rate,0) end) as vat_received_subtotal
                    from
                        kderp_supplier_payment_line kspl
                    left join
                        kderp_supplier_payment ksp on supplier_payment_id=ksp.id
                    left join
                        (Select
                            ksp.id as ksp_id,
                            rcr.rate
                        from
                            kderp_supplier_payment ksp
                        left join
                            (Select 
                                ksp.id as ksp_id,
                                max(rcr.name) as max_date
                            from 
                                kderp_supplier_payment ksp
                            left join
                                purchase_order po on order_id=po.id
                            left join
                                res_currency_rate rcr on ksp.currency_id=rcr.currency_id and po.date_order>=rcr.name
                            where
                                ksp.currency_id<>(Select currency_id from res_company rc limit 1)
                                and ksp.id in (Select distinct supplier_payment_id from kderp_supplier_payment_line)
                            group by ksp.id) vwksp_rate on ksp.id=ksp_id
                        left join
                            res_currency_rate rcr on ksp.currency_id = rcr.currency_id and max_date=rcr.name
                        where ksp.currency_id<>(Select currency_id from res_company rc limit 1) and ksp.id in (Select distinct supplier_payment_id from kderp_supplier_payment_line )) vwrate on ksp.id=vwrate.ksp_id
                    left join
                        purchase_order po on order_id=po.id
                    left join
                        (Select 
                            pol.order_id,
                            account_analytic_id,
                            case when coalesce(grant_total,0)=0 then 0
                            else
                                sum(coalesce(final_subtotal,0))/grant_total end as job_per
                        from 
                            purchase_order_line pol
                        left join
                            (Select
                                order_id,
                                sum(coalesce(final_subtotal,0)) as grant_total
                            from 
                                purchase_order_line pol
                            where
                                order_id in (Select order_id from purchase_order_line )
                            group by
                                order_id) vwgrant_total on pol.order_id=vwgrant_total.order_id
                        where
                            pol.order_id in (Select order_id from purchase_order_line )
                        group by
                            pol.order_id,
                            pol.account_analytic_id,
                            grant_total) vwtemp_job_per on ksp.order_id=vwtemp_job_per.order_id and kspl.account_analytic_id=vwtemp_job_per.account_analytic_id
                    where
                        exists(Select 
                            vat_invoice_id 
                        from 
                            kderp_supplier_payment_vat_invoice_rel kspvir 
                        where 
                            coalesce(vat_invoice_id,0)>0 and
                            kspvir.payment_id=kspl.supplier_payment_id limit 1) and 
                            ksp.state not in ('draft','cancel') and po.state not in ('draft','cancel')
                    Group by
                        kspl.account_analytic_id
Union all
                        Select 
                        kspel.account_analytic_id,
                        sum(kspe.amount_tax*job_per*case when coalesce(kspe_id,0)=0 then 1 else coalesce(rate,0) end) as vat_received_amount,
                        sum(kspe.amount*job_per*case when coalesce(kspe_id,0)=0 then 1 else coalesce(rate,0) end) as vat_received_subtotal
                    from
                        kderp_supplier_payment_expense_line kspel
                    left join
                        kderp_supplier_payment_expense kspe on supplier_payment_expense_id=kspe.id
                    left join
                        (Select
                            kspe.id as kspe_id,
                            rcr.rate
                        from
                            kderp_supplier_payment_expense kspe
                        left join
                            (Select 
                                kspe.id as kspe_id,
                                max(rcr.name) as max_date
                            from 
                                kderp_supplier_payment_expense kspe
                            left join
                                kderp_other_expense koe on expense_id=koe.id
                            left join
                                res_currency_rate rcr on kspe.currency_id=rcr.currency_id and koe.date>=rcr.name
                            where
                                kspe.id in (Select distinct supplier_payment_expense_id from kderp_supplier_payment_expense_line ) and
                                kspe.currency_id<>(Select currency_id from res_company rc limit 1)
                            group by kspe.id) vwkspe_rate on kspe.id=kspe_id
                        left join
                            res_currency_rate rcr on kspe.currency_id = rcr.currency_id and max_date=rcr.name
                        where
                            kspe.id in (Select distinct supplier_payment_expense_id from kderp_supplier_payment_expense_line ) and
                            kspe.currency_id<>(Select currency_id from res_company rc limit 1)) vwratee on kspe.id=vwratee.kspe_id
                    left join
                        kderp_other_expense koe on expense_id=koe.id
                    left join
                        (Select 
                            koel.expense_id,
                            account_analytic_id,
                            case when coalesce(grant_total,0)=0 then 0
                            else
                            sum(coalesce(amount,0))/grant_total end as job_per
                        from 
                            kderp_other_expense_line koel
                        left join
                            (Select
                                expense_id,
                                sum(coalesce(amount,0)) as grant_total
                            from 
                                kderp_other_expense_line koel
                            where
                                koel.expense_id in (Select distinct expense_id from kderp_other_expense_line )
                            group by
                                expense_id) vwgrant_total on koel.expense_id=vwgrant_total.expense_id
                        where
                            koel.expense_id in (Select distinct expense_id from kderp_other_expense_line )
                        group by
                            koel.expense_id,
                            koel.account_analytic_id,
                            grant_total) vwtemp_job_per on kspe.expense_id=vwtemp_job_per.expense_id and kspel.account_analytic_id=vwtemp_job_per.account_analytic_id
                    where
                        exists(Select 
                            vat_invoice_id 
                        from 
                            kderp_supplier_payment_expense_vat_invoice_rel kspvir 
                        where 
                            coalesce(vat_invoice_id,0)>0 and
                            kspvir.payment_expense_id=kspel.supplier_payment_expense_id limit 1) and 
                        kspe.state not in ('draft','cancel') and koe.state not in ('draft','cancel') 
                    Group by
                        kspel.account_analytic_id
                        ) vwcombine group by account_analytic_id ) vwvat_temp
where aaa.id=job_id