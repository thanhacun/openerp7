begin; delete from wkf_instance where res_type='account.invoice' and res_id in  (select id from account_invoice where state in ('paid','cancel'));
delete from wkf_instance where res_type='purchase.order' and res_id in  (select id from purchase_order where state in ('done','cancel'));
Delete from wkf_instance where res_type='kderp.supplier.payment' and res_id in (select id from kderp_supplier_payment where state in ('completed','paid','done','cancel'));
Delete from wkf_instance where res_type='kderp.supplier.payment.expense' and res_id in (select id from kderp_supplier_payment_expense where state in ('completed','paid','done','cancel'));

Delete from wkf_instance where res_type='kderp.advance.payment' and res_id in (select id from kderp_advance_payment where state in ('done','cash_received','cancel'));
Delete from wkf_instance where res_type='kderp.general.expense' and res_id in (select id from kderp_general_expense where state in ('done','cancel'));
Delete from wkf_instance where res_type='kderp.general.expense.supplier.payment' and res_id in (select id from kderp_general_expense_supplier_payment where state in ('done','cancel')); rollback;
