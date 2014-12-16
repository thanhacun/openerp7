Update product_uom pu
set 
	name=exp.name
from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
	'Select id,name from product_uom ')
as exp(
	id int,
	name varchar(64)
	)
where pu.id=exp.id
--select id,name from product_uom,