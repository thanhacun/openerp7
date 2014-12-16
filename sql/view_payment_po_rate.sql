CREATE OR REPLACE VIEW vwnew_rate_payment_po AS 

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
								where ksp.currency_id<>(Select currency_id from res_company rc limit 1) and ksp.id in (Select distinct 									supplier_payment_id from kderp_supplier_payment_line ))