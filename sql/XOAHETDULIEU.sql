-- Delete from account_move_line
-- alter SEQUENCE account_move_line_id_seq RESTART with 1
-- Delete from account_invoice_line
-- alter SEQUENCE account_invoice_line_id_seq RESTART with 1
-- DELETE FROM kderp_payment_vat_invoice
-- delete from kderp_invoice 
-- DELETE FROM KDERP_RECEIVED
-- DELETE FROM ACCOUNT_INVOICE

-- delete from kderp_contract_currency
-- DELETE FROM kderp_quotation_contract_project_line
-- alter SEQUENCE kderp_quotation_contract_project_line_id_seq RESTART with 1

-- delete from kderp_sale_order_submit_line 
-- alter SEQUENCE kderp_sale_order_submit_line_id_seq RESTART with 1

-- DELETE FROM SALE_ORDER_LINE
-- alter SEQUENCE SALE_ORDER_LINE_id_seq RESTART with 1

-- DELETE FROM SALE_ORDER
-- delete from kderp_client_payment_term 

-- delete from kderp_progress_evaluation
-- delete from kderp_contract_client

-- delete from kderp_budget_data
-- delete from kderp_budget_history 
-- delete from kderp_expense_budget_line --where id<30000
-- alter SEQUENCE kderp_expense_budget_line_id_seq RESTART with 1

-- delete from account_invoice_tax 
-- alter SEQUENCE account_invoice_tax_id_seq RESTART with 1
-- delete from kderp_supplier_payment_pay
-- delete from kderp_supplier_payment_line
-- alter SEQUENCE kderp_supplier_payment_line_id_seq RESTART with 1
-- delete from kderp_supplier_payment

-- drop table kderp_purchase_budget_line
-- delete from purchase_order_line
-- delete from purchase_order

-- delete from kderp_supplier_payment_expense_line
-- delete from kderp_supplier_payment_expense_pay
-- delete from kderp_supplier_payment_expense 
-- delete from kderp_other_expense_line
-- delete from kderp_other_expense

--delete from kderp_advance_payment_line 
--delete from kderp_advance_payment

-- delete from account_analytic_line 
-- delete from kderp_job_currency 
-- delete from account_analytic_account

-- DELETE FROM ACCOUNT_MOVE
-- DELETE FROM ACCOUNT_MOVE_reconcile
-- alter SEQUENCE account_move_id_seq RESTART 1;
-- alter SEQUENCE account_move_line_id_seq RESTART 1;

-- Delete from res_partner where id not in (1,3,4,6) and id not in (select partner_id from res_users)
-- Delete from stock_move
-- Delete from stock_picking
-- Delete from product_product ;
-- Delete from product_template 

-- Delete from account_budget_post
-- Delete from kderp_budget_category

-- delete from wkf_instance 
-- Delete from wkf_workitem
-- alter SEQUENCE wkf_workitem_id_seq RESTART 1;
-- alter SEQUENCE wkf_instance_id_seq RESTART 1;
-- delete from mail_message
-- alter SEQUENCE mail_message_id_seq RESTART 1;

-- delete from ir_attachment 
-- Delete from account_tax where amount>1

-- update account_invoice set move_id=null
-- update kderp_received  set move_id=null
-- Delete from res_partner
-- delete from res_partner where id not in (select partner_id from res_users) and id<>1