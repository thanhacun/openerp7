Select 		
		code,coalesce(price,0)<=15000000
from 
	kderp_asset_management
where type_asset_acc_id=5 and code ilike 'EQ%' and coalesce(price,0)<=15000000;
-- Update kderp_asset_management set remarks =case when coalesce(remarks,'')='' 
-- 	then 'Error Code: ' || code
-- 	else coalesce(remarks,'') || E'\nError Code: ' || code end where needupdate;
Begin;
Update kderp_asset_management set type_asset_acc_id=case when 
		coalesce(price,0)>=30000000 then 5 
		else 
			case when coalesce(price,0) between 15000000 and 30000000 then 6 else 7 end end 
 where type_asset_acc_id=5 and code ilike 'EQ%' and coalesce(price,0)<=15000000;
Rollback;
Alter table kderp_asset_management ADD  column needupdate boolean
where 
	(coalesce(price,0) >=1000000 or coalesce(price,0)<=0) and AssetNumber not in ('EQ1253-1','EQ1685-1',
'EQ1733-1',
'EQ1889-1',
'EQ2233-1',
'EQ2575-1',
'EQ2703-1',
'EQ3752-1',
'EQ4040-1',
'EQ4041-1') 

--5 6 7
--Select * from kderp_asset_code_accounting 