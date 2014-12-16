CREATE OR REPLACE VIEW vwnew_electrical_project_code AS 
SELECT 
	vwnewcode.pattern || 
	btrim(to_char(max("substring"(vwnewcode.code::text, length(vwnewcode.pattern) + 1, 2)::integer) + 1, '00'::text)) 
	AS newcode, vwnewcode.name
FROM 
	( 
	SELECT isq.name, 
               CASE
                    WHEN aaa.code IS NULL THEN (isq.prefix::text || to_char('now'::text::date::timestamp with time zone, ('YY-'::text || isq.suffix::text) || '00'::text))::character varying
                    ELSE aaa.code
                END AS code, isq.prefix::text || to_char('now'::text::date::timestamp with time zone, 'YY-'::text || isq.suffix::text) AS pattern
           FROM ir_sequence isq
      LEFT JOIN account_analytic_account aaa ON aaa.code::text ~~ ((isq.prefix::text || to_char('now'::text::date::timestamp with time zone, 'YY-'::text || isq.suffix::text)) || '__'::text)
     WHERE isq.code::text = 'kderp_electrical_project_code'::text AND isq.active) vwnewcode
  GROUP BY vwnewcode.pattern, vwnewcode.name;

  CREATE OR REPLACE VIEW vwnew_mechanical_project_code AS 
 SELECT vwnewcode.pattern || btrim(to_char(max("substring"(vwnewcode.code::text, length(vwnewcode.pattern) + 1, 2)::integer) + 1, '00'::text)) AS newcode, vwnewcode.name
   FROM ( SELECT isq.name, 
                CASE
                    WHEN aaa.code IS NULL THEN (isq.prefix::text || to_char('now'::text::date::timestamp with time zone, ('YY-'::text || isq.suffix::text) || '00'::text))::character varying
                    ELSE aaa.code
                END AS code, isq.prefix::text || to_char('now'::text::date::timestamp with time zone, 'YY-'::text || isq.suffix::text) AS pattern
           FROM ir_sequence isq
      LEFT JOIN account_analytic_account aaa ON aaa.code::text ~~ ((isq.prefix::text || to_char('now'::text::date::timestamp with time zone, 'YY-'::text || isq.suffix::text)) || '__'::text)
     WHERE isq.code::text = 'kderp_mechanical_project_code'::text AND isq.active) vwnewcode
  GROUP BY vwnewcode.pattern, vwnewcode.name;