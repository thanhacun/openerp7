Select 
	kam.id,
	price*quantity as original_price,
	sum(coalesce(kad.amount,0))  as depreciation,
	0 as reduce,
	previous_depreciation+sum(coalesce(kad.amount,0)) as accumulated_depreciation
from
	kderp_asset_management kam
left join
	kderp_asset_code_accounting kaca on kam.type_asset_acc_id=kaca.id
left join
	kderp_type_of_asset ktoa on kaca.typeofasset_id=ktoa.id
left join
	kderp_asset_depreciation kad on kam.id=asset_id and kad.date between '2014/01/01' and '2014/2/28'
left join
	(select 
		kam.id,kam.code,
		sum(coalesce(kado.amount,0))+(case when using_remaining then price*quantity -remaining_amount else 0 end) as previous_depreciation
	from
		kderp_asset_management kam
	left join
		kderp_asset_code_accounting kaca on kam.type_asset_acc_id=kaca.id
	left join
		kderp_type_of_asset ktoa on kaca.typeofasset_id=ktoa.id
	left join
		kderp_asset_depreciation kado on kam.id=asset_id and kado.date<'2014/01/01'
	where
		state not in ('draft','liquidated') and ktoa.name='FA'
	group by
		kam.id) vwold on kam.id=vwold.id
where
	state not in ('draft','liquidated') and ktoa.name='FA' and dateofinvoice>='2014/01/01'
group by
	kam.id,
	previous_depreciation
Union
Select 
	kam.id,
	0 as original_price,
	sum(coalesce(kad.amount,0))  as depreciation,
	 price*quantity-sum(coalesce(kad.amount,0)) as reduce,
	0 as accumulated_depreciation
from
	kderp_asset_management kam
left join
	kderp_asset_code_accounting kaca on kam.type_asset_acc_id=kaca.id
left join
	kderp_type_of_asset ktoa on kaca.typeofasset_id=ktoa.id
left join
	kderp_asset_depreciation kad on kam.id=asset_id and kad.date between '2014/01/01' and '2014/2/28'
where
	state='liquidated' and ktoa.name='FA' and dateofliquidated between '2014/01/01' and '2014/2/28'
group by
	kam.id;