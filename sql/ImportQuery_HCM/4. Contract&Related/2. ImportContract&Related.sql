-- #####################KDERP LOCATION#################
-- insert into 
-- 	kderp_location (id,create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,city,code,name)
-- Select
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	city,
-- 	code,
-- 	name
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 'Select
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	city,
-- 	code,
-- 	name
-- from 
-- 	kdvn_location') 
-- as kl(
-- 	id int, 
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	city varchar(30),
-- 	code varchar(4),
-- 	name varchar(100))
-- --Select max(id) from kderp_location --25
-- --alter SEQUENCE kderp_location_id_seq RESTART with 26
-- Select * from kderp_location
-- ALTER TABLE kderp_contract_client ALTER COLUMN state DROP NOT NULL;
-- ALTER TABLE kderp_contract_client ALTER COLUMN outstanding  DROP NOT NULL;
-- ALTER TABLE kderp_contract_client ALTER COLUMN state DROP NOT NULL;
Insert into kderp_contract_client
	(id,
	create_uid,
	create_date,
	write_date,
	write_uid,
	client_representative_name,
	address_id,
	code,
	contract_ref,
	outstanding,
	registration_date,
	invoice_address_id,
	project_location_id,
	project_name,
	client_id,
	date,
	attached_contract_sent,
	attached_contract_received,
	started_date,
	closed_date,
	name,
	title_id,
	completion_date,
	state,
	owner_id)
Select
	kcc.id,
	kcc.create_uid,
	kcc.create_date,
	kcc.write_date,
	kcc.write_uid,
	client_representative_name,
	rpa.id as address_id,
	kcc.code,
	contract_ref,
	coalesce(outstanding,'') as outstanding,
	registration_date,
	rpai.id as invoice_address_id,
	project_location_id,
	project_name,
	client_id,
	kcc.date,
	attached_contract_sent,
	attached_contract_received,
	started_date,
	closed_date,
	kcc.name,
	title_id,
	completion_date,
	coalesce(state,'uncompleted') as state,
	owner_id
from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
'Select 
	id,
	create_uid,
	create_date,
	write_date,
	write_uid,
	client_representative_name,
	address_id,
	contract_no as code,
	contract_ref,
	outstanding,
	registration_date,
	invoice_address_id,
	project_location_id,
	project_name,
	client_id,
	date,
	attached_contract_sent,
	attached_contract_received,
	started_date,
	closed_date,
	description as name,
	title_id,
	completion_date,
	status as state,
	owner_id
from 
	kdvn_contract_client') 
as kcc(	
	id int,
	create_uid int,
	create_date date,
	write_date date,
	write_uid int,
	client_representative_name varchar(128),
	address_id int,
	code varchar(32),
	contract_ref varchar(128),
	outstanding varchar(32),
	registration_date date,
	invoice_address_id int,
	project_location_id int,
	project_name varchar(256),
	client_id int,
	"date" date,
	attached_contract_sent boolean,
	attached_contract_received boolean,
	started_date date,
	closed_date date,
	"name" varchar(256),
	title_id int,
	completion_date date,
	state varchar(16),
	owner_id int)
left join
	res_partner rpa on kcc.address_id = rpa.address_id
left join
	res_partner rpai on kcc.invoice_address_id = rpai.address_id;

--Select max(id) from kderp_contract_client --1098
--alter SEQUENCE kderp_contract_client_id_seq RESTART with 1099


---################Contract CURRENCY
 -- 
-- Insert into kderp_contract_currency 
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	contract_id,
-- 	rate,
-- 	default_curr,
-- 	name,
-- 	rounding) 
-- Select
-- 	kcc_curr.id as id,
-- 	kcc_curr.create_uid,
-- 	kcc_curr.create_date,
-- 	kcc_curr.write_date,
-- 	kcc_curr.write_uid,
-- 	kcc_id as contract_id,
-- 	kcc_curr.rate,
-- 	kcc_curr.default_curr,
-- 	rc.id as name,
-- 	rc.rounding as rounding
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 		'Select 
-- 			id,
-- 			create_uid,
-- 			create_date,
-- 			write_date,
-- 			write_uid,
-- 			contract_id as kcc_id,
-- 			default_curr,
-- 			name,
-- 			rate
-- 		from 
-- 			project_currency pc
-- 		where
-- 			coalesce(contract_id,0)>0')
-- as kcc_curr(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	kcc_id int,
-- 	default_curr boolean,
-- 	name varchar(3),
-- 	rate numeric)
-- left join
-- 	res_currency rc on kcc_curr.name=rc.name;

--Select * from kderp_contract_currency
-- Select max(id) from kderp_contract_currency; --3102
-- alter SEQUENCE kderp_contract_currency_id_seq RESTART with 3103
-- Select * from kderp_contract_currency ;

--Select * from kderp_contract_tax;
--Import Tax

-- delete from kderp_contract_tax 3684
-- Insert into kderp_contract_tax 
-- 	(contract_currency_id,tax_id) 
-- Select
-- 	kcc_curr.id as contract_currency_id,
-- 	at.id as tax_id
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 			id,
-- 			case when coalesce(contract_amount_e,0)+coalesce(contract_amount_m,0)=0
-- 			then 0
-- 			else
-- 				(coalesce(contract_vat,0)/(coalesce(contract_amount_e,0)+coalesce(contract_amount_m,0))*100)::int/100.0 
-- 			end as rate
-- 	from 
-- 		kdvn_contract_client kcc')
-- as kcc(	
-- 	id int,
-- 	rate numeric)
-- left join
-- 	account_tax at on type='percent' and amount-rate=0 and type_tax_use='sale'
-- left join
-- 	kderp_contract_currency kcc_curr on contract_id=kcc.id and default_curr


--Import Client Payment Term
-- 
-- Insert into kderp_client_payment_term 
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	contract_id,
-- 	name,
-- 	value_amount,
-- 	sequence,
-- 	value,
-- 	due_date,
-- 	type)
-- Select
-- 	*
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		id,
-- 		create_uid,
-- 		create_date,
-- 		write_date,
-- 		write_uid,
-- 		contract_id,
-- 		name,
-- 		value_amount,
-- 		sequence,
-- 		value,
-- 		due_date,
-- 		type
-- 	from 
-- 		kdvn_payment_term_line 	
-- 	where coalesce(contract_id,0)>0')
-- as kcc_term(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	contract_id int,
-- 	name varchar(256),
-- 	value_amount numeric,
-- 	sequence int,
-- 	value varchar(16),
-- 	due_date date,
-- 	type varchar(16))

-- Select max(id) from kderp_client_payment_term; --1355
-- alter SEQUENCE kderp_client_payment_term_id_seq RESTART with 1356



--  #####################THIEU PROGRESS EVALUTAION SHEET
-- 
-- insert into kderp_progress_evaluation
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	contract_id,
-- 	date,
-- 	amount,
-- 	advanced,
-- 	retention,
-- 	vat,
-- 	name,
-- 	currency_id)
-- Select
-- 	kcc_progress.id,
-- 	kcc_progress.create_uid,
-- 	kcc_progress.create_date,
-- 	kcc_progress.write_date,
-- 	kcc_progress.write_uid,
-- 	kcc_progress.contract_id,
-- 	kcc_progress.date,
-- 	kcc_progress.amount,
-- 	kcc_progress.advanced,
-- 	kcc_progress.retention,
-- 	kcc_progress.vat,
-- 	kcc_progress.progress_no as name,
-- 	rc.id as currency_id
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		kp.id,
-- 		kp.create_uid,
-- 		kp.create_date,
-- 		kp.write_date,
-- 		kp.write_uid,
-- 		kp.contract_id,
-- 		date,
-- 		kp.AMOUNT,
-- 		advanced,
-- 		retention,
-- 		vat,
-- 		progress_no,
-- 		pc.name
-- 	from 
-- 		KDVN_PROGRESS kp
-- 	left join
-- 		project_currency pc on kp.contract_id=pc.contract_id and default_curr=True
-- 	where coalesce(kp.contract_id,0)>0')
-- as kcc_progress(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	contract_id int,
-- 	date date,
-- 	AMOUNT numeric,
-- 	advanced numeric,
-- 	retention numeric,
-- 	vat numeric,
-- 	progress_no int,
-- 	curr_name varchar(3))
-- left join
-- 	res_currency rc on curr_name=rc.name

-- Select max(id) from kderp_progress_evaluation; --1451
-- alter SEQUENCE kderp_progress_evaluation_id_seq RESTART with 1452