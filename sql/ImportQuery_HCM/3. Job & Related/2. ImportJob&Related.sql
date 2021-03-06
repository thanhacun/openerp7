﻿----######################################
--delete from res_partner where id not in (1,3,4,6)
--Select max(id) from res_partner
--alter SEQUENCE res_partner_id_seq RESTART with 4024
--Insert address

-- Insert into res_partner
-- 	(
-- 	address_id,
-- 	code,
-- 	name,
-- 	vat,
-- 	lang,
-- 	customer ,
-- 	supplier ,
-- 	trade_name ,
-- 	street ,
-- 	street2 ,
-- 	city,
-- 	country_id,
-- 	type,
-- 	phone,
-- 	fax,
-- 	mobile,
-- 	email,
-- 	parent_id,
-- 	is_company,
-- 	active,
-- 	notification_email_send,
-- 	display_name)

-- Insert into account_analytic_account (id,
-- 	code,
-- 	name,
-- 	job_type,
-- 	description,
-- 	state,
-- 	address_id,
-- 	registration_date,
-- 	invoice_address_id,
-- 	completion_date,
-- 	partner_id,
-- 	date_start,
-- 	date,
-- 	owner_id,
-- 	user_id,
-- 	manager_id,
-- 	general_project_manager_id,
-- 	area_site_manager_id,
-- 	actual_completion_date,
-- 	project_manager_ref,
-- 	process_status,
-- 	type)
-- 
-- Select
-- 	job.id,
-- 	job.code,
-- 	job.name,
-- 	project_type as job_type,
-- 	description,
-- 	project_status as state,
-- 	rpa.id as address_id,
-- 	registration_date,
-- 	rpai.id as invoice_address_id,
-- 	completion_date,
-- 	client_id as partner_id,
-- 	started_date as date_start,
-- 	closed_date as date,
-- 	owner_id,
-- 	project_manager_id as user_id,
-- 	site_manager_id as manager_id,
-- 	general_project_manager_id,
-- 	area_site_manager_id,
-- 	actual_completion_date,
-- 	project_manager_ref,
-- 	process_status,
-- 	'normal' as type
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 'Select 
-- 	id,
-- 	code,
-- 	name,
-- 	project_type,
-- 	description,
-- 	project_status,
-- 	address_id,
-- 	registration_date,
-- 	invoice_address_id,
-- 	completion_date,
-- 	client_id,
-- 	started_date,
-- 	closed_date,
-- 	owner_id,
-- 	project_manager_id,
-- 	site_manager_id,
-- 	general_project_manager_id,
-- 	area_site_manager_id,
-- 	actual_completion_date,
-- 	project_manager_ref,
-- 	process_status 
-- from kdvn_project') 
-- as job(	
-- 	id int,
-- 	code varchar(32),
-- 	name varchar(128),
-- 	project_type varchar(8),
-- 	description varchar(256),
-- 	project_status varchar(8),
-- 	address_id int,
-- 	registration_date date,
-- 	invoice_address_id int,
-- 	completion_date date,
-- 	client_id int,
-- 	started_date date,
-- 	closed_date date,
-- 	owner_id int,
-- 	project_manager_id int,
-- 	site_manager_id int,
-- 	general_project_manager_id int,
-- 	area_site_manager_id int,
-- 	actual_completion_date date,
-- 	project_manager_ref int,
-- 	process_status varchar(8))
-- left join
-- 	res_partner rpa on job.address_id = rpa.address_id
-- left join
-- 	res_partner rpai on job.invoice_address_id = rpai.address_id;
-- Select max(id) from account_analytic_account -- 526
-- alter SEQUENCE account_analytic_account_id_seq RESTART with 527
-- Update account_analytic_account set state_bar =state

---################JOB CURRENCY
-- Insert into kderp_job_currency (id,account_analytic_id,rate,default_curr,name,rounding)
-- 
-- Select
-- 	job_curr.id as id,
-- 	job_id as account_analytic_id,
-- 	job_curr.rate,
-- 	job_curr.default_curr,
-- 	rc.id as name,
-- 	rc.rounding as rounding
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 		'Select 
-- 			id,
-- 			project_id as job_id,
-- 			default_curr,
-- 			name,
-- 			rate
-- 		from 
-- 			project_currency pc
-- 		where
-- 			coalesce(project_id,0)>0')
-- as job_curr(	
-- 	id int,
-- 	job_id int,
-- 	default_curr boolean,
-- 	name varchar(3),
-- 	rate numeric)
-- left join
-- 	res_currency rc on job_curr.name=rc.name;


-- --Select max(id) from kderp_job_currency --3082
-- --alter SEQUENCE kderp_job_currency_id_seq RESTART with 3083
--Select * from kderp_job_currency ;

-- 
-- Insert into users_projects_rel (pid,uid)
-- 
-- Select
-- 	pid,
-- 	uid
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 		'Select pid,uid from user_project')
-- as uvp(	
-- 	pid int,
-- 	uid int)


-- Budget history
-- Insert into 
-- 	kderp_budget_history
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	account_analytic_id,
-- 	date,
-- 	kinden_salary_admin_cost,
-- 	material,
-- 	bussiness_profit,
-- 	amount,
-- 	site_expense,
-- 	sub_contractor,
-- 	status)
-- 	
-- Select
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	job_id as account_analytic_id,
-- 	date,
-- 	kinden_salary_admin_cost,
-- 	material,
-- 	bussiness_profit,
-- 	amount,
-- 	site_expense,
-- 	sub_contractor,
-- 	status
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 		'Select 
-- 			id,
-- 			create_uid,
-- 			create_date,
-- 			write_date,
-- 			write_uid,
-- 			project_id as job_id,
-- 			date,
-- 			kinden_salary_admin_cost,
-- 			material,
-- 			bussiness_profit,
-- 			amount,
-- 			site_expense,
-- 			sub_contractor,
-- 			status
-- 		from 
-- 			kdvn_budget_history
-- 		where
-- 			project_id in (Select id from kdvn_project)')
-- as budget_history(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	job_id int,
-- 	date date,
-- 	kinden_salary_admin_cost numeric,
-- 	material numeric,
-- 	bussiness_profit numeric,
-- 	amount numeric,
-- 	site_expense numeric,
-- 	sub_contractor numeric,
-- 	status varchar(16))

-- --Select max(id) from kderp_budget_history -- 942
-- --alter SEQUENCE kderp_budget_history_id_seq RESTART with 943


-- Budget Data
-- Insert into 
-- 	kderp_budget_data
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	account_analytic_id,
-- 	budget_id,
-- 	planned_amount)
-- 	
-- Select
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	job_id as account_analytic_id,
-- 	budget_id,
-- 	budget_amount as planned_amount
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 		'Select 
-- 			id,
-- 			create_uid,
-- 			create_date,
-- 			write_date,
-- 			write_uid,
-- 			project_id as job_id,
-- 			budget_id,
-- 			budget_amount
-- 		from 
-- 			kdvn_budget_data')
-- as job_budget_data(	
-- 		id int,
-- 		create_uid int,
-- 		create_date date,
-- 		write_date date,
-- 		write_uid int,
-- 		job_id int,
-- 		budget_id int,
-- 		budget_amount numeric)

--Select max(id) from kderp_budget_data --7530
--alter SEQUENCE kderp_budget_data_id_seq RESTART with 7531;

-- Update account_analytic_account set state_bar =state