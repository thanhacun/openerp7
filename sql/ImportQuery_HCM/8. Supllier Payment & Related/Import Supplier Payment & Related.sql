﻿-- IMPORT TAX, LINK VAO RES_ID, RES_MODEL
-- XU LY LAI THUE CO TRUONG HOP TINH THEO ADVANCE HOAC CHI CO THUE KO CO AMOUNT (TRUONG HOP THUE NHAP KHAU), TINH THEO ADVANCE

-- Supplier Payment
-- alter table kderp_supplier_payment add column old_amount_tax numeric
-- Alter table kderp_supplier_payment add column curr_state varchar(16)
-- Select *,id from account_journal where name ilike 'purchase%journal%'; id=3 Purchase Journal Journal ID
-- Select id,* from account_account where code ilike '331%' -- "33100"; id=92 Gia mua hang hoa Account_ID
-- Select id,* from account_account where code ilike '1561%' -- "156100"; id=42 Gia mua hang hoa Expense Account ID
-- 
-- Insert into kderp_supplier_payment 
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	name,
-- 	date,
-- 	due_date,
-- 	order_id,
-- 	payment_type,
-- 	user_applicant_id,
-- 	payee,
-- 	description,
-- 	pro_to_acc,
-- 	to_bc_date_first,
-- 	bc_checked_date,
-- 	to_site_date,
-- 	from_site_date,
-- 	to_procurement_manager,
-- 	to_bc_date_second,
-- 	bc_to_accounting_date,
-- 	currency_id,
-- 	amount,
-- 	advanced_amount,
-- 	retention_amount,
-- 	state,
-- 	curr_state,
-- 	journal_id,
-- 	account_id,
-- 	expense_account_id,
-- 	old_amount_tax,
-- 	tax_base)
-- Select
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	case when paymentno='' then null else paymentno end as paymentno,
-- 	rop_date,
-- 	due_date,
-- 	order_id,
-- 	payment_type,
-- 	user_applicant_id,
-- 	payee,
-- 	description,
-- 	pro_to_acc,
-- 	to_bc_date_first,
-- 	bc_checked_date,
-- 	to_site_date,
-- 	from_site_date,
-- 	to_procurement_manager,
-- 	to_bc_date_second,
-- 	bc_to_accounting_date,
-- 	curr_id,
-- 	amount,
-- 	advanced_amount,
-- 	retention_amount,
-- 	'cancel' as state,
-- 	state as curr_state,
-- 	3 as journal_id,
-- 	92 as account_id,
-- 	42 as expense_account_id,
-- 	tax_amount,
-- 	'p' as tax_base
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		id,
-- 		create_uid,
-- 		create_date,
-- 		write_date,
-- 		write_uid,
-- 		paymentno,
-- 		rop_date,
-- 		due_date,
-- 		order_id,
-- 		project_id,
-- 		supplier_id,
-- 		user_applicant_id,
-- 		case when coalesce(by_cash,False) then ''cash'' else ''bank'' end as payment_type,
-- 		payee,
-- 		description,
-- 		pro_to_acc,
-- 		to_bc_date_first,
-- 		bc_checked_date,
-- 		to_site_date,
-- 		from_site_date,
-- 		to_procurement_manager,
-- 		to_bc_date_second,
-- 		bc_to_accounting_date,
-- 		curr_name,
-- 		amount,
-- 		tax_per,
-- 		tax_amount,
-- 		state,
-- 		advanced_amount,
-- 		retention_amount
-- 	from 
-- 		kdvn_request_of_payment krop
-- 	left join
-- 		(Select id as po_curr_id, name as curr_name from kdvn_purchase_currency) kpc on currency_id=po_curr_id')
-- as rop(
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	paymentno varchar(16),
-- 	rop_date date,
-- 	due_date date,
-- 	order_id int,
-- 	project_id int,
-- 	supplier_id int,
-- 	user_applicant_id int,
-- 	payment_type varchar(8),
-- 	payee varchar(32),
-- 	description varchar(256),
-- 	pro_to_acc date,
-- 	to_bc_date_first date,
-- 	bc_checked_date date,
-- 	to_site_date date,
-- 	from_site_date date,
-- 	to_procurement_manager date,
-- 	to_bc_date_second date,
-- 	bc_to_accounting_date date,
-- 	curr_name varchar(3),
-- 	amount numeric,
-- 	tax_per numeric,
-- 	tax_amount numeric,
-- 	state varchar(16),
-- 	advanced_amount numeric,
-- 	retention_amount numeric)
-- left join
-- 	(Select id as curr_id,name as curr_name from res_currency) rc on rop.curr_name=rc.curr_name
-- where order_id in (Select id from purchase_order )

-- Select max(id) from kderp_supplier_payment --12597
-- Alter SEQUENCE kderp_supplier_payment_id_seq RESTART with 12598

-- KDERP VAT INVOICE
--##############CAN THEN PERCENTAGE
-- Delete from kderp_supplier_vat_invoice
-- Insert into kderp_supplier_vat_invoice
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	name,
-- 	date,
-- 	subtotal,
-- 	tax_per,
-- 	amount_tax,
-- 	total_amount,
-- 	equivalent_vnd,
-- 	rate,
-- 	currency_id,
-- 	to_accounting_date,
-- 	received_date,
-- 	returned_date,
-- 	notes)
-- Select
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	name,
-- 	date,
-- 	subtotal,
-- 	tax_percent,
-- 	amount_tax,
-- 	total_amount,
-- 	equivalent_vnd,
-- 	rate,
-- 	rc.curr_id,
-- 	to_accounting_date,
-- 	received_date,
-- 	returned_date,
-- 	notes
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		id,
-- 		create_uid,
-- 		create_date,
-- 		write_date,
-- 		write_uid,
-- 		name,
-- 		date,
-- 		subtotal,
-- 		tax_percent,
-- 		amount_tax,
-- 		total_amount,
-- 		equivalent_vnd,
-- 		rate,
-- 		coalesce(curr_name,''VND''),
-- 		to_accounting_date,
-- 		received_date,
-- 		returned_date,
-- 		notes
-- 	from 
-- 		kdvn_purchase_red_invoice kpri
-- 	left join
-- 		(Select id as curr_id,name as curr_name from kdvn_purchase_currency kpc) vw on currency_id=curr_id')
-- as rop(
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	name varchar(32),
-- 	date date,
-- 	subtotal numeric,
-- 	tax_percent numeric,
-- 	amount_tax numeric,
-- 	total_amount numeric,
-- 	equivalent_vnd numeric,
-- 	rate numeric,
-- 	curr_name varchar(3),
-- 	to_accounting_date date,
-- 	received_date date,
-- 	returned_date date,
-- 	notes varchar(256))
-- left join
-- 	(Select id as curr_id,name as curr_name from res_currency) rc on rop.curr_name=rc.curr_name
-- where id not in (select id from kderp_supplier_vat_invoice)

-- Select max(id) from kderp_supplier_vat_invoice --16266
-- Alter SEQUENCE kderp_supplier_vat_invoice_id_seq RESTART with 16355

-- IMPORT Supplier Payment & VAT Invoice
-- 
-- Insert into kderp_supplier_payment_vat_invoice_rel
-- 	(payment_id,
-- 	vat_invoice_id)
-- Select
-- 	rop_id,
-- 	vat_id
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		rop_id,
-- 		kdvn_purchase_red_invoice_id as vat_id 
-- 	from 
-- 		kdvn_request_of_payment_kdvn_purchase_red_invoice_rel')
-- as rop_vat(
-- 	rop_id int,
-- 	vat_id int)
-- where rop_id in (Select id from kderp_supplier_payment)

-- ## IMPORT TAX
-- BASE CODE Taxeable: 20, Deducte Amount Received Tax: 21
-- Tax 133100 23 (Co the sua thanh thue nhap khau)
-- Insert into account_tax 
-- 	(company_id,sequence,account_collected_id,account_paid_id,base_code_id,ref_base_code_id,tax_code_id,ref_tax_code_id,type,type_tax_use,applicable_type,active,name,description,amount,res_id,res_model)
-- Select
-- 	1,1,23,23,20,20,21,21,'fixed','purchase',true,true,'For ' || coalesce(ksp.name,'VAT '),ksp.name,old_amount_tax,ksp.id as res_id,'kderp.supplier.payment' as res_model
-- from 
-- 	kderp_supplier_payment ksp
-- left join
-- 	res_currency rc on currency_id = rc.id
-- where 
-- 	(
-- 		round((0.1*ksp.amount/rounding)::numeric,0)*rounding!=old_amount_tax
-- 	and
-- 		round((0.05*ksp.amount/rounding)::numeric,0)*rounding!=old_amount_tax
-- 	and
-- 		case when coalesce(ksp.amount,0)=0 then 0 else old_amount_tax/ksp.amount end not in (0.1,0.05) 
-- 	and 
-- 		coalesce(old_amount_tax,0)<>0
-- 	)
-- 	or
-- 		(coalesce(ksp.amount,0)=0 and coalesce(old_amount_tax)<>0)

-- IMPORT Supplier Payment TAX
-- 
-- Select count(*) from kderp_supplier_payment where coalesce(old_amount_tax,0)>0
-- Insert into supplier_payment_tax
-- 	(supplier_payment_id,
-- 	tax_id)
-- Select
-- 	ksp.id as ksp_id,
-- 	at.id
-- from 
-- 	kderp_supplier_payment ksp
-- left join
-- 	res_currency rc on currency_id=rc.id
-- left join
-- 	account_tax at on 
-- 		(ksp.id=at.res_id and res_model='kderp.supplier.payment' and at.amount<>0) 
-- 	or
-- 		(case when coalesce(ksp.amount,0)=0 then 0 else coalesce(old_amount_tax,0)/ksp.amount end = at.amount and type_tax_use='purchase' and at.amount<>0 and at.type='percent')
-- 	or 
-- 		(round(coalesce(at.amount,0)*ksp.amount/rounding,0)*rounding=coalesce(old_amount_tax,0) and coalesce(old_amount_tax,0)<>0 and at.type='percent' and type_tax_use='purchase' and
--  			case when coalesce(ksp.amount,0)=0 then 0 else coalesce(old_amount_tax,0)/ksp.amount end<>at.amount and at.amount<>0)
-- where
-- 	coalesce(at.id,0)>0 and coalesce(at.amount,0)<>0


--  ################################## IMPORT PAYMENT PAID TO SUPPLIER

-- Select 	
-- 	id,paymentno,
-- 	(krop.amount+advanced_amount+retention_amount +krop.tax_amount) rop_total
-- from
-- 	 (Select 
-- 		payment_id,
-- 		payment_currency_id,
-- 		sum(actual_amount) as payment_amount
-- 	from 
-- 		kdvn_payment kp
-- 	group by
-- 		payment_id,payment_currency_id) kp
-- left join
-- 	kdvn_request_of_payment krop on payment_id=krop.id
-- where
-- 	payment_currency_id=krop.currency_id and payment_amount<>(krop.amount+advanced_amount+retention_amount +krop.tax_amount)
-- 
-- 
-- -- Select * from account_journal where type='bank'; --9

-- Insert into kderp_supplier_payment_pay
-- 	(supplier_payment_id,
-- 	date,
-- 	currency_id,
-- 	amount,
-- 	exrate,
-- 	journal_id)
-- Select
-- 	rop_id,
-- 	paid.date,
-- 	rc.id as curr_id,
-- 	paid_amount,
-- 	exrate,
-- 	9 as journal_id
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		krop.id,
-- 		kp.date,
-- 		kpc.name,
-- 		sum(actual_amount) as paid_amount,
-- 		sum(actual_amount)/(krop.amount+advanced_amount+retention_amount +krop.tax_amount) as exrate
-- 	from 
-- 		kdvn_payment kp
-- 	left join
-- 		kdvn_request_of_payment krop on payment_id =krop.id
-- 	left join
-- 		kdvn_purchase_currency kpc on payment_currency_id=kpc.id
-- 	where
-- 		(krop.amount+advanced_amount+retention_amount +krop.tax_amount)<>0
-- 	group by
-- 		krop.id,
-- 		kpc.name,
-- 		date;')
-- as paid(
-- 	rop_id int,
-- 	date date,
-- 	curr_name varchar(3),
-- 	paid_amount numeric,
-- 	exrate numeric)
-- left join
-- 	res_currency rc on curr_name=rc.name
-- where
-- 	rop_id in (Select id from kderp_supplier_payment)

-- ################## Kiem tra lai va cap nhat lai exrate ################################
-- Update 
-- 	kderp_supplier_payment_pay kspp
-- set
-- 	exrate=1
-- where kspp.currency_id=24 and exrate<>1;
-- 
-- Update 
-- 	kderp_supplier_payment_pay kspp
-- set
-- 	exrate=vwtemp.rate
-- from
-- 	(Select
-- 		kspp.id as kspp_id,
-- 		rcr.rate
-- 	from
-- 		kderp_supplier_payment_pay kspp
-- 	left join
-- 		(Select 
-- 			kspp.id as kspp_id,
-- 			max(rcr.name) as max_date
-- 		from 
-- 			kderp_supplier_payment_pay kspp
-- 		left join
-- 			res_currency_rate rcr on kspp.currency_id=rcr.currency_id and kspp.date>=rcr.name
-- 		where
-- 			kspp.currency_id<>24
-- 		group by kspp.id) vwkspp_rate on kspp.id=kspp_id
-- 	left join
-- 		res_currency_rate rcr on kspp.currency_id = rcr.currency_id and max_date=rcr.name
-- 	where kspp.currency_id<>24) vwtemp where kspp.id=kspp_id


-- ###################### Import Payment Detail
-- 
-- Insert into kderp_supplier_payment_line
-- 	(supplier_payment_id,
-- 	account_analytic_id,
-- 	amount
-- 	)
-- Select
-- 	rop_id,
-- 	project_id,
-- 	amount
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		rop_id,
-- 		project_id,
-- 		sum(coalesce(amount,0)+coalesce(advanced_amount,0)+coalesce(retention_amount,0))
-- 	from 
-- 		kdvn_request_of_payment_detail 
-- 
-- 		group by rop_id,
-- 		project_id')
-- as pay_detail(
-- 	rop_id int,
-- 	project_id int,
-- 	amount numeric)
-- where rop_id in (Select id from kderp_supplier_payment) and coalesce(project_id,0)<>0

-- --- Xoa thue bi cap nhat 2 lan
-- Select supplier_payment_id from supplier_payment_tax group by supplier_payment_id  having count(tax_id)>1
-- Create table supplier_payment_tax_temp (rop_id int, tax_id int)
-- Delete from supplier_payment_tax  spt
-- where (supplier_payment_id,tax_id) not in 
-- 
-- 	(Select 
-- 		supplier_payment_id as rop,
-- 		min(tax_id) as t_id
-- 	from 
-- 		supplier_payment_tax  spt
-- 	group by
-- 		supplier_payment_id);


Update kderp_supplier_payment ksp7 set to_bc_date_second=
Select to_bc_date_second

from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.12',
	'Select 
		id,
		create_uid,
		create_date,
		write_date,
		write_uid,
		paymentno,
		rop_date,
		due_date,
		order_id,
		project_id,
		supplier_id,
		user_applicant_id,
		case when coalesce(by_cash,False) then ''cash'' else ''bank'' end as payment_type,
		payee,
		description,
		pro_to_acc,
		to_bc_date_first,
		bc_checked_date,
		to_site_date,
		from_site_date,
		to_procurement_manager,
		to_bc_date_second,
		bc_to_accounting_date,
		curr_name,
		amount,
		tax_per,
		tax_amount,
		state,
		advanced_amount,
		retention_amount
	from 
		kdvn_request_of_payment krop
	left join
		(Select id as po_curr_id, name as curr_name from kdvn_purchase_currency) kpc on currency_id=po_curr_id')
as rop(
	id int,
	create_uid int,
	create_date date,
	write_date date,
	write_uid int,
	paymentno varchar(16),
	rop_date date,
	due_date date,
	order_id int,
	project_id int,
	supplier_id int,
	user_applicant_id int,
	payment_type varchar(8),
	payee varchar(32),
	description varchar(256),
	pro_to_acc date,
	to_bc_date_first date,
	bc_checked_date date,
	to_site_date date,
	from_site_date date,
	to_procurement_manager date,
	to_bc_date_second date,
	bc_to_accounting_date date,
	curr_name varchar(3),
	amount numeric,
	tax_per numeric,
	tax_amount numeric,
	state varchar(16),
	advanced_amount numeric,
	retention_amount numeric)
where order_id in (Select id from purchase_order )