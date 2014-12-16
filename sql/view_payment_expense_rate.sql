CREATE OR REPLACE VIEW vwnew_rate_payment_expense AS 

						
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
										kspe.id in (Select distinct supplier_payment_expense_id from kderp_supplier_payment_expense_line 											) and
										kspe.currency_id<>(Select currency_id from res_company rc limit 1)
										group by kspe.id) vwkspe_rate on kspe.id=kspe_id
										left join
										res_currency_rate rcr on kspe.currency_id = rcr.currency_id and max_date=rcr.name
										where
										kspe.id in (Select distinct supplier_payment_expense_id from 			kderp_supplier_payment_expense_line	)										 and
										kspe.currency_id<>(Select currency_id from res_company rc limit 1) group by kspe.id ,
										    rcr.rate
									  ) 