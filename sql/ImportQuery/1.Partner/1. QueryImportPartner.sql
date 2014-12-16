Select * from res_partner where id=1
--List Min ID many Address
select 
	min(id) as address_id
from 
	res_partner_address 
group by 
	partner_id 
having 
	count(partner_id)>1;

Create or replace view for_import_partner as
--List only one partner
Select 
	rp.id as id,
	rpa.id as address_id,
	ref,
	rp.name,
	vat_code as vat,
	lang,
	customer,
	supplier,
	rp.trade_name,
	street,
	street2,
	city,
	rpa.country_id,
	type,
	phone,
	fax,
	mobile,
	email,
	NULL::integer as parent_id,
	true as is_company
from 
	res_partner rp
left join
	res_partner_address rpa on rp.id = partner_id
where
	rp.id not in (select partner_id from res_partner_address group by partner_id having count(partner_id)>1) 
	or coalesce(rpa.id,0)=0
Union
--List multi address (With address min)
Select 
	rp.id as id,
	rpa.id as address_id,
	ref,
	rp.name,
	vat_code as vat,
	lang,
	customer,
	supplier,
	rp.trade_name,
	street,
	street2,
	city,
	rpa.country_id,
	type,
	phone,
	fax,
	mobile,
	email,
	NULL::integer as parent_id,
	true as is_company
from
	res_partner rp
left join
	res_partner_address rpa on rp.id = partner_id
where
	rpa.id in (select 
			min(id) 
		from 
			res_partner_address 
		group by 
			partner_id 
		having count(partner_id)>1)
Union

Select 
	Null::integer as id,
	rpa.id as address_id,
	ref,
	rp.name,
	'' as vat,
	lang,
	false as customer,
	false as supplier,
	rp.trade_name,
	street,
	street2,
	city,
	rpa.country_id,
	type,
	phone,
	fax,
	mobile,
	email,
	rp.id as parent_id,
	False as is_company
from
	res_partner rp
left join
	res_partner_address rpa on rp.id = partner_id
where
	rpa.id not in (select 
			min(id) 
		from 
			res_partner_address 
		group by 
			partner_id 
		having count(partner_id)>1)
	and rp.id in (select 
			partner_id
		from 
			res_partner_address 
		group by 
			partner_id 
		having count(partner_id)>1);
