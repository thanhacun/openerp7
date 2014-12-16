-- Select 
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
-- from 
-- 	kdvn_project

Select 
	id,
	code,
	name,
	job_type,
	description,
	state,
	address_id,
	registration_date,
	invoice_address_id,
	completion_date,
	partner_id,
	date_start,
	date,
	owner_id,
	user_id,
	manager_id,
	general_project_manager_id,
	area_site_manager_id,
	actual_completion_date,
	project_manager_ref,
	process_status
from 
	account_analytic_account