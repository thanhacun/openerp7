--Drop function funSummaryJobArea(getDate date);
CREATE OR REPLACE FUNCTION funSummaryJobArea(getDate date)
RETURNS TABLE (area_id integer, em varchar(3),bigjobamount float,otherjobamount float, owninternalsupport float, otherinternalsupport float) AS $$
BEGIN
    RETURN QUERY
	Select
		areaid as area_id,
		job_type as em,
		sum(bigjob)::float as bigjob,
		sum(otherjob)::float as otherjob,
		sum(own_internal_support)::float as own_internal_support,
		sum(other_interal_support)::float as other_interal_support
	from
		(Select 
			kca.id as areaid,
			aaa.job_type as job_type,
			sum(case when job_scale='00-big_job' then kcja.amount else 0 end) as bigjob,
			sum(case when job_scale='00-big_job' then 0 else kcja.amount end) as otherjob,
			0 as own_internal_support,
			sum(case when kcja.control_support='support_area' and kjca.area_id <> kcja.area_id then kcja.amount else 0 end) as other_interal_support	
		from 
			kderp_job_control_area kjca
		left join
			account_analytic_account aaa on job_id = aaa.id
		left join
			kderp_control_area kca on kjca.area_id = kca.id
		left join
			kderp_contract_job_area kcja on aaa.id = kcja.job_id
		left join
			kderp_contract_client kcc on contract_id = kcc.id
		where
			to_char(kcc.registration_date,'Mon-YY')=to_char(getDate,'Mon-YY') and 
			aaa.state not in ('closed','cancel') and availability='inused'
		group by
			kca.id,
			aaa.job_type
		Union all
		Select 	
			kca.id as areaid,
			aaa.job_type as job_type,
			0 as bigjob,
			0 as otherjob,
			sum(coalesce(kcja.amount,0)) as own_internal_support,
			0 as other_interal_support	
		from 
			kderp_contract_job_area kcja
		left join
			account_analytic_account aaa on job_id = aaa.id
		left join
			kderp_control_area kca on kcja.area_id = kca.id
		left join
			kderp_contract_client kcc on contract_id = kcc.id
		where
			kcja.control_support='support_area' and 
			aaa.state not in ('closed','cancel') and availability='inused' and
			to_char(kcc.registration_date,'Mon-YY')=to_char(getDate,'Mon-YY') 
		group by
			kca.id,
			aaa.job_type) vwcombine
	group by
		areaid,
		job_type;
END;
$$ LANGUAGE plpgsql;