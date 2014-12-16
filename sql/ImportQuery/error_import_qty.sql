-- Select
-- 	*
-- into tblPOL_qty
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.197',
-- 	'Select 
-- 		pol.id,
-- 		order_id,
-- 		plan_qty,
-- 		product_qty
-- 	from 
-- 		purchase_order_line pol
-- 	left join
-- 		purchase_order po on order_id = po.id
-- 	left join
-- 		purchase_typeoforder pt on typeoforder=pt.id
-- 	where pt.code<>''e'' and coalesce(pol.project_id,0)>0 and plan_qty=0 and product_qty<>0')
-- as pol(
-- 	id int,
-- 	order_id int,
-- 	plan_qty numeric,
-- 	product_qty numeric)

Select * from tblPOL_qty;
update 
	purchase_order_line pol 
set 
	plan_qty=tblq.product_qty, 
	product_qty=tblq.product_qty 
from tblPOL_qty tblq where pol.id=tblq.id