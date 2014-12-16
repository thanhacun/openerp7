--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.13
-- Dumped by pg_dump version 9.3.1
-- Started on 2014-05-08 13:29:50

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 166 (class 1259 OID 22990)
-- Name: U_CodeAsset; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--
Drop table "U_CodeAsset";
CREATE TABLE "U_CodeAsset" (
    assetcode character varying(16) NOT NULL,
    assetname character varying(256)
);


ALTER TABLE public."U_CodeAsset" OWNER TO openerp;

--
-- TOC entry 167 (class 1259 OID 22993)
-- Name: U_CodeJob; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--
Drop table "U_CodeJob";
CREATE TABLE "U_CodeJob" (
    code character varying(16),
    name character varying(128),
    id integer
);


ALTER TABLE public."U_CodeJob" OWNER TO openerp;

--
-- TOC entry 168 (class 1259 OID 22996)
-- Name: U_DataAsset; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--
Drop table "U_DataAsset";
CREATE TABLE "U_DataAsset" (
    assetnumber character varying(16) NOT NULL,
    refeqno character varying(16),
    assetcode character varying(16),
    description character varying(256),
    quantity integer,
    price numeric,
    makername character varying(32),
    brandname character varying(32),
    estimatedusefulllife integer,
    monthlydepreciation numeric,
    purchasedate date,
    inused boolean,
    codesupplier character varying,
    liquidated boolean,
    outdated boolean
);


ALTER TABLE public."U_DataAsset" OWNER TO openerp;

--
-- TOC entry 169 (class 1259 OID 23002)
-- Name: U_FixAsset_Ac; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--
Drop table "U_FixAsset_Ac";
CREATE TABLE "U_FixAsset_Ac" (
    oldcode character varying(16),
    name character varying(128),
    originalprice numeric,
    typeofasset character varying(2),
    code_code integer,
    code_name character varying(128),
    tangible integer
);


ALTER TABLE public."U_FixAsset_Ac" OWNER TO openerp;

--
-- TOC entry 1079 (class 1259 OID 26072)
-- Name: u_dataassetusage; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--
Drop table "u_dataassetusage";
CREATE TABLE u_dataassetusage (
    assetusednumber character varying(16) NOT NULL,
    assetnumber character varying(16),
    usedtime date,
    endtime date,
    managernumber character varying(16),
    staffnumber character varying(16),
    jobnumber character varying(32),
    managerelectrical character varying(16),
    managermechanical character varying(16),
    remarks character varying(128)
);


ALTER TABLE public.u_dataassetusage OWNER TO openerp;

--
-- TOC entry 1080 (class 1259 OID 26075)
-- Name: u_dataassetusage_wrong; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--
Drop table "u_dataassetusage_wrong";
CREATE TABLE u_dataassetusage_wrong (
    assetusednumber character varying(16) NOT NULL,
    assetnumber character varying(16),
    usedtime date,
    endtime date,
    managernumber character varying(16),
    staffnumber character varying(16),
    jobnumber character varying(32),
    managerelectrical character varying(16),
    managermechanical character varying(16),
    remarks character varying(128)
);


ALTER TABLE public.u_dataassetusage_wrong OWNER TO openerp;

--
-- TOC entry 1081 (class 1259 OID 26078)
-- Name: u_staff_code; Type: TABLE; Schema: public; Owner: openerp; Tablespace: 
--
Drop table "u_staff_code";
CREATE TABLE u_staff_code (
    staffcode character varying(16) NOT NULL,
    name character varying(64)
);


ALTER TABLE public.u_staff_code OWNER TO openerp;

--
-- TOC entry 4631 (class 2606 OID 27002)
-- Name: U_CodeAsset_pkey; Type: CONSTRAINT; Schema: public; Owner: openerp; Tablespace: 
--

ALTER TABLE ONLY "U_CodeAsset"
    ADD CONSTRAINT "U_CodeAsset_pkey" PRIMARY KEY (assetcode);


--
-- TOC entry 4633 (class 2606 OID 27004)
-- Name: U_DataAsset_pkey; Type: CONSTRAINT; Schema: public; Owner: openerp; Tablespace: 
--

ALTER TABLE ONLY "U_DataAsset"
    ADD CONSTRAINT "U_DataAsset_pkey" PRIMARY KEY (assetnumber);


--
-- TOC entry 4635 (class 2606 OID 27409)
-- Name: fdafds; Type: CONSTRAINT; Schema: public; Owner: openerp; Tablespace: 
--

ALTER TABLE ONLY u_dataassetusage
    ADD CONSTRAINT fdafds PRIMARY KEY (assetusednumber);


--
-- TOC entry 4639 (class 2606 OID 27970)
-- Name: staff_key; Type: CONSTRAINT; Schema: public; Owner: openerp; Tablespace: 
--

ALTER TABLE ONLY u_staff_code
    ADD CONSTRAINT staff_key PRIMARY KEY (staffcode);


--
-- TOC entry 4637 (class 2606 OID 28058)
-- Name: u_dataassetusage_wrong_pkey; Type: CONSTRAINT; Schema: public; Owner: openerp; Tablespace: 
--

ALTER TABLE ONLY u_dataassetusage_wrong
    ADD CONSTRAINT u_dataassetusage_wrong_pkey PRIMARY KEY (assetusednumber);

--DROP TABLE kderp_job_from_access;

CREATE TABLE kderp_job_from_access
(
  code character varying(128)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE kderp_job_from_access
  OWNER TO openerp;
GRANT SELECT ON TABLE kderp_job_from_access TO public;
GRANT ALL ON TABLE kderp_job_from_access TO openerp;

--DROP TABLE newcode_convert;

CREATE TABLE newcode_convert
(
  oldcode character varying(8),
  newcode character varying(4),
  assetname character varying(250),
  greater30m integer,
  between15and30 integer,
  less15m integer,
  intangible integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE newcode_convert
  OWNER TO openerp;
GRANT SELECT ON TABLE newcode_convert TO public;
GRANT ALL ON TABLE newcode_convert TO openerp;


CREATE TABLE newassetcode
(
  code character varying(4) NOT NULL,
  parentcode character varying(4),
  name character varying(128),
  vietnam character varying(128),
  CONSTRAINT fdsafdsaf PRIMARY KEY (code)
)
WITH (
  OIDS=FALSE
);