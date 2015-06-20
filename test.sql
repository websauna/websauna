('/Users/mikko/code/trees/venv/lib/python3.4/site-packages/deform/templates/',)
[['app', 'application'], ['composite', 'composit'], ['pipeline'], ['filter-app']]
('/Users/mikko/code/trees/websauna/websauna/system/form/templates/deform', '/Users/mikko/code/trees/venv/lib/python3.4/site-packages/deform/templates/')
--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

ALTER TABLE ONLY public.users DROP CONSTRAINT users_activation_id_fkey;
ALTER TABLE ONLY public.user_group DROP CONSTRAINT user_group_user_id_fkey;
ALTER TABLE ONLY public.user_group DROP CONSTRAINT user_group_group_id_fkey;
ALTER TABLE ONLY public.referral_program DROP CONSTRAINT referral_program_owner_id_fkey;
ALTER TABLE ONLY public.referral_conversion DROP CONSTRAINT referral_conversion_user_id_fkey;
ALTER TABLE ONLY public.referral_conversion DROP CONSTRAINT referral_conversion_referral_program_id_fkey;
DROP INDEX public.referral_program_slug_index;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_security_code_key;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
ALTER TABLE ONLY public.user_group DROP CONSTRAINT user_group_pkey;
ALTER TABLE ONLY public.referral_program DROP CONSTRAINT referral_program_slug_key;
ALTER TABLE ONLY public.referral_program DROP CONSTRAINT referral_program_pkey;
ALTER TABLE ONLY public.referral_conversion DROP CONSTRAINT referral_conversion_user_id_key;
ALTER TABLE ONLY public.referral_conversion DROP CONSTRAINT referral_conversion_pkey;
ALTER TABLE ONLY public."group" DROP CONSTRAINT group_pkey;
ALTER TABLE ONLY public."group" DROP CONSTRAINT group_name_key;
ALTER TABLE ONLY public.activation DROP CONSTRAINT activation_pkey;
ALTER TABLE ONLY public.activation DROP CONSTRAINT activation_code_key;
ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.user_group ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.referral_program ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.referral_conversion ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public."group" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.activation ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.users_id_seq;
DROP TABLE public.users;
DROP SEQUENCE public.user_group_id_seq;
DROP TABLE public.user_group;
DROP SEQUENCE public.referral_program_id_seq;
DROP TABLE public.referral_program;
DROP SEQUENCE public.referral_conversion_id_seq;
DROP TABLE public.referral_conversion;
DROP SEQUENCE public.group_id_seq;
DROP TABLE public."group";
DROP TABLE public.alembic_version;
DROP SEQUENCE public.activation_id_seq;
DROP TABLE public.activation;
DROP EXTENSION plpgsql;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: moo
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO moo;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: moo
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: activation; Type: TABLE; Schema: public; Owner: moo; Tablespace: 
--

CREATE TABLE activation (
    created_by character varying(30) NOT NULL,
    valid_until timestamp without time zone NOT NULL,
    code character varying(30) NOT NULL,
    id integer NOT NULL
);


ALTER TABLE activation OWNER TO moo;

--
-- Name: activation_id_seq; Type: SEQUENCE; Schema: public; Owner: moo
--

CREATE SEQUENCE activation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE activation_id_seq OWNER TO moo;

--
-- Name: activation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moo
--

ALTER SEQUENCE activation_id_seq OWNED BY activation.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: moo; Tablespace: 
--

CREATE TABLE alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE alembic_version OWNER TO moo;

--
-- Name: group; Type: TABLE; Schema: public; Owner: moo; Tablespace: 
--

CREATE TABLE "group" (
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    group_data jsonb,
    description text,
    name character varying(50),
    id integer NOT NULL
);


ALTER TABLE "group" OWNER TO moo;

--
-- Name: group_id_seq; Type: SEQUENCE; Schema: public; Owner: moo
--

CREATE SEQUENCE group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE group_id_seq OWNER TO moo;

--
-- Name: group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moo
--

ALTER SEQUENCE group_id_seq OWNED BY "group".id;


--
-- Name: referral_conversion; Type: TABLE; Schema: public; Owner: moo; Tablespace: 
--

CREATE TABLE referral_conversion (
    id integer NOT NULL,
    referral_program_id integer,
    referrer character varying(512),
    user_id integer NOT NULL
);


ALTER TABLE referral_conversion OWNER TO moo;

--
-- Name: referral_conversion_id_seq; Type: SEQUENCE; Schema: public; Owner: moo
--

CREATE SEQUENCE referral_conversion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE referral_conversion_id_seq OWNER TO moo;

--
-- Name: referral_conversion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moo
--

ALTER SEQUENCE referral_conversion_id_seq OWNED BY referral_conversion.id;


--
-- Name: referral_program; Type: TABLE; Schema: public; Owner: moo; Tablespace: 
--

CREATE TABLE referral_program (
    id integer NOT NULL,
    name character varying(64),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    expires_at timestamp with time zone,
    slug character varying(6),
    hits integer,
    owner_id integer
);


ALTER TABLE referral_program OWNER TO moo;

--
-- Name: referral_program_id_seq; Type: SEQUENCE; Schema: public; Owner: moo
--

CREATE SEQUENCE referral_program_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE referral_program_id_seq OWNER TO moo;

--
-- Name: referral_program_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moo
--

ALTER SEQUENCE referral_program_id_seq OWNED BY referral_program.id;


--
-- Name: user_group; Type: TABLE; Schema: public; Owner: moo; Tablespace: 
--

CREATE TABLE user_group (
    group_id integer,
    user_id integer,
    id integer NOT NULL
);


ALTER TABLE user_group OWNER TO moo;

--
-- Name: user_group_id_seq; Type: SEQUENCE; Schema: public; Owner: moo
--

CREATE SEQUENCE user_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_group_id_seq OWNER TO moo;

--
-- Name: user_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moo
--

ALTER SEQUENCE user_group_id_seq OWNED BY user_group.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: moo; Tablespace: 
--

CREATE TABLE users (
    username character varying(32),
    password character varying(256),
    salt character varying(256),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    activated_at timestamp with time zone,
    enabled boolean,
    last_login_at timestamp with time zone,
    last_login_ip inet,
    last_password_change_at timestamp without time zone,
    user_data jsonb,
    last_login_date timestamp without time zone DEFAULT now() NOT NULL,
    activation_id integer,
    status integer,
    email character varying(100) NOT NULL,
    security_code character varying(256),
    registered_date timestamp without time zone DEFAULT now() NOT NULL,
    id integer NOT NULL
);


ALTER TABLE users OWNER TO moo;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: moo
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_id_seq OWNER TO moo;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moo
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: moo
--

ALTER TABLE ONLY activation ALTER COLUMN id SET DEFAULT nextval('activation_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: moo
--

ALTER TABLE ONLY "group" ALTER COLUMN id SET DEFAULT nextval('group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: moo
--

ALTER TABLE ONLY referral_conversion ALTER COLUMN id SET DEFAULT nextval('referral_conversion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: moo
--

ALTER TABLE ONLY referral_program ALTER COLUMN id SET DEFAULT nextval('referral_program_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: moo
--

ALTER TABLE ONLY user_group ALTER COLUMN id SET DEFAULT nextval('user_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: moo
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Data for Name: activation; Type: TABLE DATA; Schema: public; Owner: moo
--

COPY activation (created_by, valid_until, code, id) FROM stdin;
\.


--
-- Name: activation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moo
--

SELECT pg_catalog.setval('activation_id_seq', 1, false);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: moo
--

COPY alembic_version (version_num) FROM stdin;
1038b4caee2
\.


--
-- Data for Name: group; Type: TABLE DATA; Schema: public; Owner: moo
--

COPY "group" (created_at, updated_at, group_data, description, name, id) FROM stdin;
\.


--
-- Name: group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moo
--

SELECT pg_catalog.setval('group_id_seq', 1, false);


--
-- Data for Name: referral_conversion; Type: TABLE DATA; Schema: public; Owner: moo
--

COPY referral_conversion (id, referral_program_id, referrer, user_id) FROM stdin;
\.


--
-- Name: referral_conversion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moo
--

SELECT pg_catalog.setval('referral_conversion_id_seq', 1, false);


--
-- Data for Name: referral_program; Type: TABLE DATA; Schema: public; Owner: moo
--

COPY referral_program (id, name, created_at, updated_at, expires_at, slug, hits, owner_id) FROM stdin;
\.


--
-- Name: referral_program_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moo
--

SELECT pg_catalog.setval('referral_program_id_seq', 1, false);


--
-- Data for Name: user_group; Type: TABLE DATA; Schema: public; Owner: moo
--

COPY user_group (group_id, user_id, id) FROM stdin;
\.


--
-- Name: user_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moo
--

SELECT pg_catalog.setval('user_group_id_seq', 1, false);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: moo
--

COPY users (username, password, salt, created_at, updated_at, activated_at, enabled, last_login_at, last_login_ip, last_password_change_at, user_data, last_login_date, activation_id, status, email, security_code, registered_date, id) FROM stdin;
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moo
--

SELECT pg_catalog.setval('users_id_seq', 1, false);


--
-- Name: activation_code_key; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY activation
    ADD CONSTRAINT activation_code_key UNIQUE (code);


--
-- Name: activation_pkey; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY activation
    ADD CONSTRAINT activation_pkey PRIMARY KEY (id);


--
-- Name: group_name_key; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY "group"
    ADD CONSTRAINT group_name_key UNIQUE (name);


--
-- Name: group_pkey; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY "group"
    ADD CONSTRAINT group_pkey PRIMARY KEY (id);


--
-- Name: referral_conversion_pkey; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY referral_conversion
    ADD CONSTRAINT referral_conversion_pkey PRIMARY KEY (id);


--
-- Name: referral_conversion_user_id_key; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY referral_conversion
    ADD CONSTRAINT referral_conversion_user_id_key UNIQUE (user_id);


--
-- Name: referral_program_pkey; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY referral_program
    ADD CONSTRAINT referral_program_pkey PRIMARY KEY (id);


--
-- Name: referral_program_slug_key; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY referral_program
    ADD CONSTRAINT referral_program_slug_key UNIQUE (slug);


--
-- Name: user_group_pkey; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY user_group
    ADD CONSTRAINT user_group_pkey PRIMARY KEY (id);


--
-- Name: users_email_key; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_security_code_key; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_security_code_key UNIQUE (security_code);


--
-- Name: users_username_key; Type: CONSTRAINT; Schema: public; Owner: moo; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: referral_program_slug_index; Type: INDEX; Schema: public; Owner: moo; Tablespace: 
--

CREATE UNIQUE INDEX referral_program_slug_index ON referral_program USING btree (slug);


--
-- Name: referral_conversion_referral_program_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moo
--

ALTER TABLE ONLY referral_conversion
    ADD CONSTRAINT referral_conversion_referral_program_id_fkey FOREIGN KEY (referral_program_id) REFERENCES referral_program(id);


--
-- Name: referral_conversion_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moo
--

ALTER TABLE ONLY referral_conversion
    ADD CONSTRAINT referral_conversion_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: referral_program_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moo
--

ALTER TABLE ONLY referral_program
    ADD CONSTRAINT referral_program_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES users(id);


--
-- Name: user_group_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moo
--

ALTER TABLE ONLY user_group
    ADD CONSTRAINT user_group_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group"(id);


--
-- Name: user_group_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moo
--

ALTER TABLE ONLY user_group
    ADD CONSTRAINT user_group_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: users_activation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moo
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_activation_id_fkey FOREIGN KEY (activation_id) REFERENCES activation(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: moo
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM moo;
GRANT ALL ON SCHEMA public TO moo;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

