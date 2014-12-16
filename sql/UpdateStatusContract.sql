--State is Uncompleted, Outstanding is pm_check
Select 
	'uncompleted' as status,'pm_check' as outstanding
from
	kderp_contract_client kcc
where 
	coalesce(state,'')<>'completed' and
	id in 
		(Select 
			distinct kpfc.contract_id 
		 from 
			account_invoice kpfc
		 left join 
			kderp_client_payment_term kptl on kpfc.id = kptl.id 
		 where 
			due_date<=current_date and state ='draft') and 
	not (coalesce(attached_approved_quotation,False)=True or coalesce(attached_contract_received,False)=True);

--State is Uncompleted, Outstanding is BC_Check
Select
	'uncompleted',
	'bc_check'
from 
	kderp_contract_client kcc
where 
	coalesce(state,'')<>'completed' and
	id not in 
		(Select 
			distinct kpfc.contract_id
		from 
			account_invoice kpfc
		left join 
			kderp_client_payment_term kptl on kpfc.id = kptl.id 
		where 
			due_date<=current_date and state ='draft') and
	(	
		not exists(Select id from account_invoice kpfc where kpfc.contract_id = kcc.id limit 1) or
		not (coalesce(attached_approved_quotation,False)=True or coalesce(attached_contract_received,False)=True) or
		kcc.id in (Select
				    contract_id 
				from 
				    account_invoice
				where 
					coalesce(attached_progress_received,False)=False and coalesce(contract_id,0)>0 and contract_id=kcc.id) or
		kcc.id in 
			(Select 
			    kccs.id
			from 
			    kderp_contract_client kccs
			left join
			    (Select
				kpfc.contract_id,
				sum(coalesce(kpvi.amount,0)) as total_vat_amount
			    from
				account_invoice kpfc
			    left join
				kderp_payment_vat_invoice kpvi on kpfc.id = kpvi.payment_id
			    left join
				kderp_contract_client kcc on contract_id=kcc.id
			    where 
				coalesce(kcc.state,'uncompleted')<>'completed'
			    group by contract_id) vwpayment_vat on kcc.id = vwpayment_vat.contract_id
			where 
			    kccs.id=kcc.id and (
			    total_vat_amount!=contracted_total
			    or contracted_total!=contract_collect_total)
			    ));

--Contract Completed
Select
	'completed',
	'none' 
from
	kderp_contract_client kcc
where 
	coalesce(state,'')<>'completed'	and
	(coalesce(attached_approved_quotation,False)=True or
	coalesce(attached_contract_received,False)=True) and
	kcc.id not in (Select
				contract_id 
			from 
				account_invoice
			where 
				coalesce(attached_progress_received,False)=False and coalesce(contract_id,0)=kcc.id) and
	kcc.id not in (Select 
			    kcc.id
			from 
			    kderp_contract_client kcc
			left join
			    (Select
				kpfc.contract_id,
				sum(coalesce(kpvi.amount,0)) as total_vat_amount
			    from
				account_invoice kpfc
			    left join
				kderp_payment_vat_invoice kpvi on kpfc.id = kpvi.payment_id
			    left join
				kderp_contract_client kcc on contract_id=kcc.id
			    where 
				coalesce(kcc.state,'uncompleted')<>'completed'
			    group by contract_id) vwpayment_vat on kcc.id = vwpayment_vat.contract_id
			where 
			    total_vat_amount!=contracted_total
			    or contracted_total!=contract_collect_total)