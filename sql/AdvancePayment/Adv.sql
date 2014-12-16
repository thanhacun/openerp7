Create or replace view kderp_detail_cash_advance as
                            Select 
                                row_number() over (order by date,voucher_no,user) as id,
                                *
                            from
                                (--Cash Payment & Recived
                                Select 
                                    kap.name,
                                    kap.date_received_money as date,
                                    krl.voucher_no,
                                    case when coalesce(krl.other_user,'')<>'' then 'Others' else staffno end as staffno,
                                    coalesce(krl.other_user,rr.name) as user,
                                    case when type_cash='receive' then krl.amount else 0 end as debit,
                                    case when type_cash='payment' then krl.amount else 0 end as credit,
                                    currency_id,
                                    --to_char(krl.date,'Mon.YYYY') as Period,
                                    kcp.id as cash_period_id,
                                    krl.name as description,
                                    case when advance_buying<>'cash' then 'advance' else 'cash' end as type,
                                    0 as request_amount,
                                    0 as return_amount
                                from
                                    kderp_advance_payment_reimbursement_line krl                               
                                left join
                                    kderp_advance_payment kap on advance_id=kap.id
                                 left join
                                    kderp_cash_period kcp on kap.date_received_money between date_start and date_stop
                                left join
                                    hr_employee he on krl.user_id=he.id
                                left join
                                    resource_resource rr on he.resource_id = rr.id
                                LEFT JOIN
                                    RES_CURRENCY RC ON CURRENCY_ID=RC.ID
                                where 
                                    advance_buying='cash' and kap.state not in ('draft','cancel')
                            Union
                                -- Request ADV Amount
                                Select 
                                    kap.name,
                                    date_received_money as date,
                                    payment_voucher_no as voucher_no,
                                    staffno,    
                                    rr.name as user,
                                    0 as debit,
                                    request_amount as credit,
                                    currency_id,
                                    kcp.id as cash_period_id,
                                    'Tạm Ứng / Advance Payment Cash No. ' || right(kap.name,2) as Description,
                                    case when advance_buying<>'cash' then 'request_advance' else 'cash' end as type,
                                    request_amount,
                                    0 as return_amount
                                from
                                    kderp_advance_payment kap
                                left join
                                    kderp_cash_period kcp on date_received_money between date_start and date_stop
                                left join
                                    hr_employee he on kap.user_id=he.id
                                left join
                                    resource_resource rr on he.resource_id = rr.id
                                where 
                                    advance_buying<>'cash' and kap.state not in ('draft','cancel')
                            Union
                                --Return ADV Amount
                                Select
                                    kap.name,
                                    date_of_received_reimbursement as date,
                                    receive_voucher_no as voucher_no,
                                    staffno,    
                                    rr.name as user,
                                    request_amount as debit,
                                    0 as credit,
                                    currency_id,
                                    kcp.id as cash_period_id,
                                    'Trả lại tạm ứng / Return Advance Payment Cash No.' || right(kap.name,2) as Description,
                                    case when advance_buying<>'cash' then 'return_advance' else 'cash' end as type,
                                    request_amount,
                                    reimbursement_amount as return_amount
                                from
                                    kderp_advance_payment kap
                                left join
                                    kderp_cash_period kcp on date_of_received_reimbursement between date_start and date_stop
                                left join
                                    hr_employee he on kap.user_id=he.id
                                left join
                                    resource_resource rr on he.resource_id = rr.id
                                where 
                                    advance_buying<>'cash' and kap.state not in ('draft','cancel') and date_of_received_reimbursement is not null
                            Union
                                --Return Reimbursement
                                Select 
                                    kap.name,
                                    date_of_received_reimbursement as date, --krl.date
                                    krl.voucher_no,
                                    case when coalesce(krl.other_user,'')<>'' then 'Others' else staffno end as staffno,    
                                    coalesce(krl.other_user,rr.name) as user,
                                    0 as debit,
                                    krl.amount as credit,
                                    currency_id,
                                    kcp.id as cash_period_id,
                                    krl.name as Description,
                                    case when advance_buying<>'cash' then 'reimbursed' else 'cash' end as type,
                                    0 as request_amount,
                                    0 as return_amount
                                from
                                    kderp_advance_payment_reimbursement_line krl                                
                                left join
                                    kderp_advance_payment kap on advance_id=kap.id
                                left join
                                    kderp_cash_period kcp on date_of_received_reimbursement between date_start and date_stop
                                left join
                                    hr_employee he on kap.user_id=he.id
                                left join
                                    resource_resource rr on he.resource_id = rr.id
                                where 
                                    advance_buying<>'cash' and kap.state not in ('draft','cancel')
                                ) vwcashadvancecombine

;-- drop VIEW kderp_detail_cash_advance ;
Select * from kderp_detail_cash_advance where name='AD14-1213-02'
--# BACKUP 
-- Select 
-- 	date_received_money as date,
-- 	payment_voucher_no as voucher_no,
-- 	rr.name as user,
-- 	0 as debit,
-- 	request_amount as credit,
-- 	currency_id,
-- 	to_char(date_received_money,'Mon.YYYY') as period,
-- 	'Tạm Ứng / Advance Payment Cash No.' || row_number() over (PARTITION BY kap.user_id,extract(ISOYEAR FROM date_received_money) order by kap.user_id,payment_voucher_no asc) as Description
-- from
-- 	kderp_advance_payment kap
-- left join
-- 	hr_employee he on kap.user_id=he.id
-- left join
-- 	resource_resource rr on he.resource_id = rr.id
-- where 
-- 	advance_buying<>'cash' and kap.state not in ('draft','cancel')