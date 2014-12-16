SAVEPOINT test;
Update resource_resource rr set user_id=ru.id from hr_employee hr  left join res_users ru on trim(substring(work_email from 1 for position('@' in work_email)-1))=login where rr.id=hr.resource_id ;
ROLLBACK  TO SAVEPOINT  test;

