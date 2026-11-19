-- Adminer 5.4.0 PostgreSQL 17.11 dump

DROP TABLE IF EXISTS "alembic_version";
CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL,
    CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num")
)
WITH (oids = false);

INSERT INTO "alembic_version" ("version_num") VALUES
('7b1b0ec4a75a');

DROP TABLE IF EXISTS "conversations";
DROP SEQUENCE IF EXISTS conversations_id_seq;
CREATE SEQUENCE conversations_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."conversations" (
    "id" integer DEFAULT nextval('conversations_id_seq') NOT NULL,
    "title" character varying(100) NOT NULL,
    "created_at" timestamp NOT NULL,
    "updated_at" timestamp NOT NULL,
    "user_id" integer NOT NULL,
    CONSTRAINT "conversations_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE INDEX ix_conversations_id ON public.conversations USING btree (id);

CREATE INDEX ix_conversations_user_id ON public.conversations USING btree (user_id);

INSERT INTO "conversations" ("id", "title", "created_at", "updated_at", "user_id") VALUES
(1,	'Python Learning',	'2026-09-15 12:49:31.835872',	'2026-09-15 12:49:31.835876',	1),
(2,	'GenAI Learning',	'2026-09-15 12:50:07.508534',	'2026-09-15 12:50:07.508541',	1),
(3,	'FastAPI Learning',	'2026-09-15 15:54:29.199394',	'2026-09-15 15:54:29.199438',	1),
(4,	'Python Learning',	'2026-09-15 15:55:46.325565',	'2026-09-15 15:55:46.325574',	1),
(5,	'My AI Project',	'2026-09-24 12:37:11.161132',	'2026-09-24 12:37:11.161135',	2),
(6,	'Protected Conversation',	'2026-09-24 12:41:47.020725',	'2026-09-24 12:41:47.02073',	8),
(7,	'Protected Conversation',	'2026-09-24 16:02:15.622536',	'2026-09-24 16:02:15.622551',	13),
(8,	'FastAPI Learning',	'2026-09-24 17:13:49.596939',	'2026-09-24 17:13:49.596954',	2),
(9,	'AI Engineering',	'2026-09-24 17:14:37.005042',	'2026-09-24 17:14:37.005054',	2),
(10,	'Protected Conversation',	'2026-09-24 17:39:21.208235',	'2026-09-24 17:39:21.208251',	16),
(11,	'Get Test Conversation',	'2026-09-24 17:39:21.696141',	'2026-09-24 17:39:21.696156',	17),
(12,	'Protected Conversation',	'2026-09-24 17:39:41.615878',	'2026-09-24 17:39:41.615886',	21),
(13,	'Get Test Conversation',	'2026-09-24 17:39:41.849018',	'2026-09-24 17:39:41.849025',	22),
(14,	'Python Learning',	'2026-09-24 17:41:49.016293',	'2026-09-24 17:41:49.016309',	24),
(15,	'Python Learning',	'2026-09-24 17:41:50.056475',	'2026-09-24 17:41:50.056489',	26),
(16,	'Protected Conversation',	'2026-09-24 17:42:52.70801',	'2026-09-24 17:42:52.708026',	30),
(17,	'Get Test Conversation',	'2026-09-24 17:42:53.208113',	'2026-09-24 17:42:53.20813',	31),
(18,	'Python Learning',	'2026-09-24 17:42:54.185633',	'2026-09-24 17:42:54.185641',	33),
(19,	'Python Learning',	'2026-09-24 17:42:54.661967',	'2026-09-24 17:42:54.661974',	35),
(21,	'Protected Conversation',	'2026-09-24 17:47:50.202539',	'2026-09-24 17:47:50.202547',	39),
(22,	'Get Test Conversation',	'2026-09-24 17:47:50.477684',	'2026-09-24 17:47:50.477699',	40),
(23,	'Python Learning',	'2026-09-24 17:47:51.041163',	'2026-09-24 17:47:51.041171',	42),
(24,	'Python Learning',	'2026-09-24 17:47:51.962439',	'2026-09-24 17:47:51.962446',	44),
(25,	'Private Conversation',	'2026-09-24 17:47:53.045184',	'2026-09-24 17:47:53.045193',	46);

DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "email" character varying(255) NOT NULL,
    "password_hash" character varying(255) NOT NULL,
    "created_at" timestamp NOT NULL,
    "updated_at" timestamp NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);

CREATE INDEX ix_users_id ON public.users USING btree (id);

INSERT INTO "users" ("id", "email", "password_hash", "created_at", "updated_at") VALUES
(1,	'legacy@nexa-ai.local',	'LEGACY_MIGRATION_USER',	'2026-09-24 11:40:14.063038',	'2026-09-24 11:40:14.063038'),
(2,	'dev@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$sx1BJvc5Rpnz7k+ZmY9Gfw$b0GY2Q2ncgcY+QfhyQvJHyEYPbRrIhj2cJeZSLGSgTw',	'2026-09-24 12:06:51.175748',	'2026-09-24 12:06:51.175751'),
(6,	'test_register_unique@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$PjB1NzL02PfkxZ2IzzDPDg$itrv9kyu5O6gYOHN0AiTkble4J6dlmSR087SEz6JKoA',	'2026-09-24 12:41:46.649243',	'2026-09-24 12:41:46.649247'),
(7,	'test_login_unique@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$NmGp6yUG/IokGpnE5B02vw$O0wDkp3pzMhZTQU2nXT53U3lirHKXcV/7VGrmssvTIs',	'2026-09-24 12:41:46.763459',	'2026-09-24 12:41:46.763464'),
(8,	'test_protected_unique@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$2Tm3VQLfFg/eOHDapbH7FQ$Gwqsh3/QcHO8y0xuGlLHGzaiKbIrQ+EsqzMMwqmOIYU',	'2026-09-24 12:41:46.905379',	'2026-09-24 12:41:46.905384'),
(9,	'home-test@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$Jb6RX1loem2D28E/h0UQXA$SJxZ5INP15PjPd69eoaU2WT8PCCIcq8CcRUykWpkfDg',	'2026-09-24 15:56:03.806165',	'2026-09-24 15:56:03.806179'),
(10,	'test-3d016f01@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$kIbUEtXe+m2RBHT8Azflzg$NuKNVeQcKAhXuFQ2/DybBuhVLhHlCTwaO5MdOKq9qGw',	'2026-09-24 15:59:07.340835',	'2026-09-24 15:59:07.340845'),
(11,	'test-f3f92f5c@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$UlYyOcjPE1rIHKZvXXPYzA$V4R3ziC1Vq97FaPV5GQhVuz2v7vWGWT3psGtWwBMJTM',	'2026-09-24 16:02:15.08854',	'2026-09-24 16:02:15.088549'),
(12,	'login-a307e209@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$Zv+0mKxWhvAUYREyL+pNwQ$FiQlg4KqXksBURbNPn5DpgjLCgSIA0T7XIPaZa+LlAY',	'2026-09-24 16:02:15.22096',	'2026-09-24 16:02:15.220969'),
(13,	'protected-095cd57d@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$gGbB6DbUSSFPD1dCvsPGNQ$4wDVRWOO2+F6OhIdf3VuvXmmHTGm98xA9wmwvWkcKvs',	'2026-09-24 16:02:15.464337',	'2026-09-24 16:02:15.464348'),
(14,	'test-1a3086ed@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$mQQ+YmZDN0VcDqUFrrW08A$3r5LJ9A0vr+Vfzod9F+dI7E3jZ0JwsRBjzuIb17bgyY',	'2026-09-24 17:39:20.069115',	'2026-09-24 17:39:20.069134'),
(15,	'login-7fe16dbe@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$B8uca3si56tuqmMEnrA/sg$HeF4BZ8dfOpYiP+3OYGirwrrgB7wbt9zfuVC12WYiXs',	'2026-09-24 17:39:20.34801',	'2026-09-24 17:39:20.348058'),
(16,	'protected-c53dc302@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$E2CEj0vKedVka/fQ5/s3pw$9GoMxcHoku8mWzNBb6aXINNglm4O79N3aLNMZZqvvEQ',	'2026-09-24 17:39:20.900873',	'2026-09-24 17:39:20.900896'),
(17,	'get-dd37c05e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$6T5wpk4OpL/nFa2K3YF71g$u5tIU3BfrEeZmX/ryDZhuKbiQFN/2ZwFVezya9cjUuU',	'2026-09-24 17:39:21.46279',	'2026-09-24 17:39:21.462833'),
(18,	'not-found-f69b7f6e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$JpimmiQwoxBqCT7ixlSJJA$mxJDZ97HhY2MgnKBlloIDCztUAPRsW523VCmwgsSLGI',	'2026-09-24 17:39:21.964423',	'2026-09-24 17:39:21.964439'),
(19,	'test-38a13539@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$0wdOpNBi6erPPwWmnlwRrw$cxguygTOiw+tD8Qh4b/k+QAl17vXnFJKVhRiNGQ1FOU',	'2026-09-24 17:39:41.081935',	'2026-09-24 17:39:41.081945'),
(20,	'login-48e22884@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$6eFaTA+Cfv+T1oPqMAxtHQ$WfABCNp/Q3t4roneXauYvyL+5qxgJy0f8oHDr+QLEDM',	'2026-09-24 17:39:41.216424',	'2026-09-24 17:39:41.216437'),
(21,	'protected-bfac45d5@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$HjJVoloZqAU3SQkh2u+iCg$XvY/tIgYs9ZTdFCSfgbOQMJTGnpJ265jbcpU48IIvss',	'2026-09-24 17:39:41.468432',	'2026-09-24 17:39:41.46844'),
(22,	'get-ec5de6aa@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$IFCpM7ZC9yeo4PmAx8+zlg$8O2KQwsvLSBDmKctfmnyH5qoLOBRelNTKIVRDrKaGkY',	'2026-09-24 17:39:41.738045',	'2026-09-24 17:39:41.738054'),
(23,	'not-found-f05a1edd@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$k5EciCqLMZjLpAffafx5Jw$L0lRfqMt9YKXU8fosAcRfYhKOvCXAns+tc8QccZEdNs',	'2026-09-24 17:39:42.105112',	'2026-09-24 17:39:42.105129'),
(24,	'conversation-0a9c176d@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$NKHVW3di3blDdreb3rG8dg$hGTz1iZm+ceY9unvzyDoPQskpapGNKTMW/Cs0xSCJAs',	'2026-09-24 17:41:48.829566',	'2026-09-24 17:41:48.829578'),
(25,	'conversation-b22bde57@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$IpSFAw3Hj0l71kpnrMdzdw$Kp7V31gSPHRmVhW/XglEL9yrsYx0zHcRYS9d7J1Ao/Q',	'2026-09-24 17:41:49.315168',	'2026-09-24 17:41:49.315185'),
(26,	'conversation-4ea7f41e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$m3qn4llSGYK5oyowUWMc2g$Eg0TozQ+X6Wd4nb9Mv1cwn+1Z1CfnGRfoABipclvQQ0',	'2026-09-24 17:41:49.819939',	'2026-09-24 17:41:49.819959'),
(27,	'conversation-8a07a031@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$5qnw4xnS5Z4DiCq4IwQt+g$cyjSidlWOWFNP2Qear1OxIVfbjMM52FBPFsusFHaMSs',	'2026-09-24 17:41:50.338227',	'2026-09-24 17:41:50.338244'),
(28,	'test-ee4dfee7@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$9jD3PPCgR61n2Y8ArdPuFQ$1DHPTcEVcpc9dKLmJrDVZIwFiGBMhSQpDJfS8HtOamY',	'2026-09-24 17:42:52.155858',	'2026-09-24 17:42:52.155868'),
(29,	'login-4e09e4a6@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$c9tjiCgm9VcqhbVvtyGNug$Gn6Zq+K7hgyVA46wnRmawBmL4sfFV8W9PhxVYJMkAXE',	'2026-09-24 17:42:52.286473',	'2026-09-24 17:42:52.286482'),
(30,	'protected-060b1501@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$hcD4OpkzlMMGAhtp6fqWaA$zGEGFy0N3VurcmwyFFu9Q82mJ8tEIR0sCT+Re+TYMy4',	'2026-09-24 17:42:52.509568',	'2026-09-24 17:42:52.509577'),
(31,	'get-661266e7@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$jQAg3lPUgItdGoIG6ma6wg$WGdQ6m3VehbqDNZhSFer8Ttd4qqLnurdDktSR/kk9e8',	'2026-09-24 17:42:52.947105',	'2026-09-24 17:42:52.947122'),
(32,	'not-found-98bdecc0@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$CAJGIn00CGYPoP2c+B8/LQ$fGA4B6szRy86YLWiRTEK5UoR6pmEKi/IssvP9rOLlGU',	'2026-09-24 17:42:53.469369',	'2026-09-24 17:42:53.469387'),
(33,	'conversation-be7d139f@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$j35qt1lqPrkskXuuMgCdiQ$YYqduRgdEDqGih++5fK6hp+HECx4ZmnW1GuFv5bfOK0',	'2026-09-24 17:42:53.960894',	'2026-09-24 17:42:53.960922'),
(34,	'conversation-4e156c09@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$BdZJsO1z5lKi1AHIViea4Q$VsfiYtiUUqEw+i54HAR4334bExJTSixbCH1EIo+BKe0',	'2026-09-24 17:42:54.315123',	'2026-09-24 17:42:54.315132'),
(35,	'conversation-47648614@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$bu5QUMx5FpXfZhrMJLbbTg$BCh7MxPWK09WOpAgl8jeEBMwszik7BL14DANgES4lD4',	'2026-09-24 17:42:54.544621',	'2026-09-24 17:42:54.54463'),
(36,	'conversation-c5cd826e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$8sLWcqyLXxPSF4grmvtbdw$/z88MIRSs9/E2lEo/ISjNWKJqOb2xNUiR3M7SKqFmQA',	'2026-09-24 17:42:54.899581',	'2026-09-24 17:42:54.899607'),
(37,	'test-de81f003@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$p30Ht1Rh6eDU0GP/Pp+h2A$XKQoABqchU8vKJI0DsotmK4le4oYMy7PM82brSvjhDQ',	'2026-09-24 17:47:49.386879',	'2026-09-24 17:47:49.386891'),
(38,	'login-f78a48a5@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$LB63aSGroDOT3fy7TMgyKw$GUPNM0CdVF5oPY85eHSLbkFLoewhCe3tUg5ZtYHouaY',	'2026-09-24 17:47:49.607209',	'2026-09-24 17:47:49.607227'),
(39,	'protected-5e3fc5df@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$x1EbQJPHqsXyvc/nK98tQg$LZWDGvVGLzuffM6J6zRPbQlaveH5snjdDLcERn0dx58',	'2026-09-24 17:47:50.046094',	'2026-09-24 17:47:50.046109'),
(40,	'get-6be61e14@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$BIjsWhQbty+3y4L5YSaZTQ$HzMiHCXNU5sG51b1qKjWCcj5xEYu9xn7YPTKP2w7upE',	'2026-09-24 17:47:50.334231',	'2026-09-24 17:47:50.334243'),
(41,	'not-found-eb0c52fe@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$fy86gwbtbmIMDx533IcNLQ$nqbmSYkMdF7MFcRMBY1iNDXmnwkE9EFvQ2rfUXOM2z4',	'2026-09-24 17:47:50.625945',	'2026-09-24 17:47:50.625955'),
(42,	'conversation-6b5ac48e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$DT4nYnokArFg12GKnA14Bg$pcbBGYtSs2Bk1xTbPOPG9KQc1bFfXgHBAjaV1cFVi+w',	'2026-09-24 17:47:50.889129',	'2026-09-24 17:47:50.889139'),
(43,	'conversation-66b64281@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$HF7cgR4qvFaykh+hyMwauw$t8IBrBS9kElPb+dLrzRsyR1NENclCw42uBa1vrhJKSY',	'2026-09-24 17:47:51.272553',	'2026-09-24 17:47:51.272573'),
(44,	'conversation-59e0c29e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$ZwtsOnyg2QyRrll7Swyjpg$93aTbbQ1c3A6q+pI7zYFmktA3BIcgircoWBfT31060c',	'2026-09-24 17:47:51.836235',	'2026-09-24 17:47:51.836264'),
(45,	'conversation-cd0ea089@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$TfZ3jA99TdJWndVBuzDJpg$9hzdHl3FYz3pmmuENjjlgdddoJFlXVGLgcpL3SVAJLs',	'2026-09-24 17:47:52.218347',	'2026-09-24 17:47:52.218367'),
(46,	'conversation-39b61cee@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$hC2faNLvJ8jmz5sf2OWdsA$jfnGN/hCZIBK2gSbhVUmJDhJAft4df6NnDAuj7qbf+8',	'2026-09-24 17:47:52.813079',	'2026-09-24 17:47:52.813112'),
(47,	'conversation-589ca6e2@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$jbkH66XujOPxU/oGXD9GiQ$1UhxI9m4pQPtYKaaAExgp8fUGlWSi2NeQ54Wrdfck+U',	'2026-09-24 17:47:53.174248',	'2026-09-24 17:47:53.174257');

ALTER TABLE ONLY "public"."conversations" ADD CONSTRAINT "fk_conversations_user_id_users" FOREIGN KEY (user_id) REFERENCES users(id) NOT DEFERRABLE;

-- 2026-09-24 18:23:47 UTC
