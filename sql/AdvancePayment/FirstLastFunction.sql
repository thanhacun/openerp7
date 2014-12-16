Select 
	kcp.id,
	first(id) over (order by date_start) as EndingBalance_vnd,
	sum(coalesce(balance_this_period_vnd,0)) over (order by date_start) as EndingBalance_vnd,
	sum(coalesce(balance_this_period_usd,0)) over (order by date_start) as EndingBalance_usd
from 
	kderp_cash_period kcp
Group by
	kcp.id
order by date_start;

-- 
-- -- Create a function that always returns the first non-NULL item
-- CREATE OR REPLACE FUNCTION public.first_agg ( anyelement, anyelement )
-- RETURNS anyelement LANGUAGE sql IMMUTABLE STRICT AS $$
--         SELECT $1;
-- $$;
--  
-- -- And then wrap an aggregate around it
-- CREATE AGGREGATE public.first (
--         sfunc    = public.first_agg,
--         basetype = anyelement,
--         stype    = anyelement
-- );
--  
-- -- Create a function that always returns the last non-NULL item
-- CREATE OR REPLACE FUNCTION public.last_agg ( anyelement, anyelement )
-- RETURNS anyelement LANGUAGE sql IMMUTABLE STRICT AS $$
--         SELECT $2;
-- $$;
--  
-- -- And then wrap an aggregate around it
-- CREATE AGGREGATE public.last (
--         sfunc    = public.last_agg,
--         basetype = anyelement,
--         stype    = anyelement
-- );