-- Select partner_id from account_move limit 100;
-- Select partner_id from account_move_line limit 100;
-- Select partner_id from account_move_line limit 100;
-- 
-- Select partner_id from purchase_order  limit 100;
-- 
-- Select partner_id from kderp_other_expense  limit 100;
-- Select supplier_id from kderp_supplier_payment_expense  limit 100;
-- 
-- 
-- Select * from res_partner where name ilike '%THANH Tung%'; -- 3595 -->2617;
Begin ;
Update account_move set partner_id=2617 where partner_id=3595;
Update account_move_line set partner_id=2617 where partner_id=3595;

Update purchase_order set partner_id=2617 where partner_id=3595;

Update kderp_other_expense set partner_id=2617 where partner_id=3595;

Update kderp_supplier_payment_expense set supplier_id=2617 where supplier_id=3595;
rollback;