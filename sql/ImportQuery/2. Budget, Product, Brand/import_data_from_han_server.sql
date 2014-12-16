﻿--### ACCOUNT BUDGET CATEGORY ###
-- select 
-- * 
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192','Select id,parent_id,sequence,type,cat_code,name from budget_category') as bc(id int,parent_id int,sequence int,type varchar(16),cat_code varchar(32),name varchar(64))

-- Select * from kderp_budget_category;

-- Insert into kderp_budget_category (id,parent_id,sequence,type,cat_code,name) select 
-- * 
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192','Select id,parent_id,sequence,type,cat_code,name from budget_category') as bc(id int,parent_id int,sequence int,type varchar(16),cat_code varchar(32),name varchar(64))
--Select max(id) from kderp_budget_category;
--alter SEQUENCE kderp_budget_category_id_seq RESTART with 13

--### ACCOUNT BUDGET POST ###
-- delete from account_budget_post
-- select * 
-- from 
-- dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 'Select code,name,categ_id from account_budget_post') as abp(code varchar(8),name varchar(256),categ_id int)
-- 

-- Insert into account_budget_post (id,code,name,budget_categ_id,company_id) 
-- select * from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 'Select id,code,name,categ_id,1 from account_budget_post') as abp(id integer,code varchar(8),name varchar(256),categ_id int,company_id int)
-- Select max(id) from account_budget_post;-- 819
-- alter SEQUENCE account_budget_post_id_seq RESTART with 820;

--### Brand ###
-- select * 
-- from 
-- dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 'Select id,code,name from kdvn_brand_name') as kbn(id int,code varchar(10),name varchar(50))
-- 
--Select * from kderp_brand_name
-- Insert into kderp_brand_name (id,code,name) select * 
-- from 
-- dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 'Select id,code,name from kdvn_brand_name') as kbn(id int,code varchar(10),name varchar(50))
-- alter SEQUENCE kderp_brand_name_id_seq RESTART with 36;


--### Code Japan###
-- select * 
-- from 
-- dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 'Select id,code,name from kdvn_product_category_japan') as kbn(id int,code varchar(4),name varchar(255))
-- 
-- Insert into kderp_product_category_japan (id,code,name) select * 
-- from 
-- dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 'Select id,code,name from kdvn_product_category_japan') as kbn(id int,code varchar(4),name varchar(255))
-- Select max(id) from kderp_product_category_japan
-- alter SEQUENCE kderp_product_category_japan_id_seq RESTART with 400;

-----#### PRODUCT & PRODUCT TEMPLATE ##########
--PRODUCT TEMPLATE
-- Select * from product_template;
-- Insert into 
-- 	product_template
-- (ID,name,uom_id,purchase_ok,type,categ_id,cost_method,uom_po_id,supply_method,procure_method) 
-- Select ID,name,1 as uom_id,true as purchase_ok,'product' as type,3 as categ_id,'standard' as cost_method,1 as uom_po_id,
-- 'buy' as supply_method,'make_to_stock'  as procure_method
-- from 
-- 	dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select id,name from product_template') as kbn(id int,name varchar(128))
---- Select max(id) from product_template;69187
-- alter SEQUENCE product_template_id_seq RESTART with 69188


---######PRODUCT PRODUCT######
-- Insert into product_product 
-- 	(id, default_code, product_tmpl_id,active,category_follow_japan_id,budget_id,valuation) 
-- Select 	*,'manual_periodic' as valuation
-- from 
-- 	dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select id,default_code,product_tmpl_id,active,category_follow_japan_id,kdvn_budget_id as budget_id from product_product') as 
-- pp(id int,default_code varchar(64),product_tmpl_id int,active boolean,category_follow_japan_id int,kdvn_budget_id int)
-- Select max(id) from product_product; 69480
--alter SEQUENCE product_product_id_seq RESTART with 69489
------------Tempprary  --Update product_product pp set budget_id = abp.id from account_budget_post abp where substring(default_code from 1 for 4)=abp.code

-------------------###############IMPORT USERS AREA ###################################-------
	--- 1. IMPORT PARTNER - FOR USERS
	--- 2. IMPORT ALIAS -- FOR USERS
	--- 3. IMPORT USER  -- FOR USERS
--Import User
-- Select * from res_users;
-- alter table res_partner add column u_id int
-- 
-- Insert into res_partner
-- 	(name,
-- 	u_id,
-- 	color,
-- 	use_parent_address,
-- 	active,
-- 	supplier,
-- 	employee,
-- 	type,
-- 	tz,
-- 	customer,
-- 	is_company,
-- 	notification_email_send,
-- 	opt_out,
-- 	display_name,
-- 	vat_subjected)
-- 
-- Select 	
-- 	name,
-- 	id as user_id,
-- --	'en_US' as lang,
-- 	0 as color,
-- 	False as use_parent_address,
-- 	True as active,
-- 	False as supplier,
-- 	False as employee,
-- 	'contact' as type,
-- 	'Asia/Ho_Chi_Minh' as tz,
-- 	False as customer,
-- 	True as is_company,
-- 	'comment' as notification_email_send,
-- 	False as opt_out,
-- 	name as display_name,
-- 	False as vat_subjected 
-- from 
-- 	dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select id,name from res_users where id<>1') as ru(id int,name varchar(128));
-- Select max(id) from res_partner ; --5111
-- alter SEQUENCE res_partner_id_seq RESTART with 5252


-- IMPORT MAIL ALIAS
-- ALTER TABLE MAIL_ALIAS add column u_id int
-- Select * from mail_alias
--76 is user model
--7 next number of alias_force_thread_id

-- Select 	
-- 	76 as alias_model_id,
-- 	'{}' as alias_defaults,
-- 	row_number() over (ORDER BY login)+7 as alias_force_thread_id,
-- 	id as u_id,
-- 	login as alias_name,
-- 	1 as alaias_user_id
-- from 
-- 	dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select id,login from res_users where id<>1') as ru(id int,login varchar(128));
-- 
-- insert into mail_alias (alias_model_id,alias_defaults,alias_force_thread_id,u_id,alias_name,alias_user_id)
-- Select 	
-- 	76 as alias_model_id,
-- 	'{}' as alias_defaults,
-- 	row_number() over (ORDER BY login)+7 as alias_force_thread_id,
-- 	id as u_id,
-- 	login as alias_name,
-- 	1 as alaias_user_id
-- from 
-- 	dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select id,login from res_users where id<>1') as ru(id int,login varchar(128))
-- Select max(id) from mail_alias ; 525
-- alter SEQUENCE mail_alias_id_seq RESTART with 542

--Import users
-- Insert into res_users (active,menu_id,company_id,id,login,password,partner_id,alias_id)
-- Select 	
-- 	True as active,
-- 	1 as menu_id, 
-- 	1 as company_id,
-- 	ru.id,
-- 	ru.login,
-- 	ru.password,
-- 	rp.id as partner_id,
-- 	ma.id as alias_id
-- from 
-- 	dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select id,login,password from res_users where id<>1') as ru(id int,login varchar(128),password varchar(128))
-- left join
-- 	res_partner rp on ru.id=rp.u_id
-- left join
-- 	mail_alias ma on ru.id=ma.u_id order by id;
	--Select * from res_users where id=3
--Delete from res_users where id=5
-- Select max(id) from res_users ; 639
-- alter SEQUENCE res_users_id_seq RESTART with 653