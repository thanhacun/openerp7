SELECT * FROM kderp_asset_code_accounting  ;
--Delete from newassetcode 
-- insert into kderp_asset_code_accounting  Select  id, create_uid, create_date,write_date,write_uid,typeofasset_id,code,type,name from kderp_asset_code
-- 
-- Select *
--  from dblink('dbname=KDVN_Data_HN user=openerp_read password=290797pr host=172.16.10.192',
-- 	'Select 
-- 		  id, create_uid, create_date,write_date,write_uid,typeofasset_id,code,type,name		
-- 	from 
-- 		kderp_asset_code') 
-- as kri(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	typeofasset_id int,
-- 	code varchar(32),
-- 	type int,
-- 	name varchar(64))

-- Select max(id) from kderp_asset_code_accounting ;
-- alter SEQUENCE kderp_asset_code_accounting_id_seq RESTART 17

-- Delete from kderp_asset_management_usage;
-- update kderp_other_expense_line set asset_id =null where coalesce(asset_id,0)>0
-- Delete from kderp_asset_management;
-- Delete from kderp_asset_code 
-- Create table NewAssetCode (Code varchar(4),parentcode varchar(4),name varchar(128),vietnam varchar(128));
-- Update newassetcode set vietnam=null where vietnam=''
-- name:"kderp.asset.code,name", state translated, value:from query,type: model, lang:vi_VN
Select kac.id,vietnam from newassetcode nc left join kderp_asset_code kac on nc.code=kac.code
  where coalesce(vietnam,'')<>'';
--Delete from ir_translation where name ilike 'kderp.asset.code,name' and type='field'
--Insert into ir_translation 
-- Begin;
-- ALTER SEQUENCE ir_translation_id_seq RESTART 973430;
-- alter SEQUENCE kderp_asset_code_id_seq RESTART 55
-- Select max(id) from kderp_asset_code 
-- Insert into ir_translation Select nextval('ir_translation_id_seq'::regclass) as id, 'vi_VN' as lang,kac.name as src,'kderp.asset.code,name',kac.id as res_id,null as module,'translated' as state, vietnam as value, 'model' as type,null as comment from newassetcode nc left join kderp_asset_code kac on nc.code=kac.code where coalesce(vietnam,'')<>'';
-- rollback

--Select * from ir_translation limit 10
-- Select max(id) from ir_translation 
-- -- delete from ir_translation where name  ilike '%kderp.asset.code,name%' and res_id not in (Select id from kderp_asset_code )
-- 

Select res_id,count(id) from ir_translation where name  ilike '%kderp.asset.code,name%' group by res_id having count(id)>1;
