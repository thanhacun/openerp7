-- Table: kderp_asset_remaining

-- -- DROP TABLE kderp_asset_remaining;
-- 
-- CREATE TABLE kderp_asset_remaining
-- (
--   code character varying(16) NOT NULL,
--   newcode character varying(32),
--   amount numeric,
--   date date,
--   CONSTRAINT pk PRIMARY KEY (code)
-- )
-- WITH (
--   OIDS=FALSE
-- );
-- ALTER TABLE kderp_asset_remaining
--   OWNER TO openerp;
-- GRANT ALL ON TABLE kderp_asset_remaining TO openerp;
-- GRANT SELECT ON TABLE kderp_asset_remaining TO public;


 -- alter TABLE kderp_asset_management ADD column remaining_amount numeric;
 -- alter TABLE kderp_asset_management ADD column using_remaining boolean;
 begin;
 Update kderp_asset_management kam set remaining_amount=amount,using_remaining=True from kderp_asset_remaining kar where kam.code=kar.newcode;
 rollback;
 Select * from kderp_asset_remaining