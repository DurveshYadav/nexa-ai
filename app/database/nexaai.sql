-- Adminer 5.4.0 PostgreSQL 17.11 dump

DROP TABLE IF EXISTS "alembic_version";
CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL,
    CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num")
)
WITH (oids = false);

INSERT INTO "alembic_version" ("version_num") VALUES
('219c320a2ddc');

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
(36,	'FastAPI Learning',	'2026-09-25 11:52:21.317598',	'2026-09-25 11:52:21.3176',	71),
(1,	'Protected Conversation',	'2026-09-26 15:02:08.514447',	'2026-09-26 15:02:08.514452',	3),
(2,	'Get Test Conversation',	'2026-09-26 15:02:08.720198',	'2026-09-26 15:02:08.720203',	4),
(3,	'Python Learning',	'2026-09-26 15:02:09.122304',	'2026-09-26 15:02:09.122309',	6),
(4,	'Python Learning',	'2026-09-26 15:02:09.520757',	'2026-09-26 15:02:09.520762',	8),
(5,	'Private Conversation',	'2026-09-26 15:02:09.944153',	'2026-09-26 15:02:09.944157',	10),
(6,	'Docker V1 Smoke Test',	'2026-09-27 09:34:19.636173',	'2026-09-27 09:34:19.636187',	12),
(7,	'Protected Conversation',	'2026-09-27 12:26:41.769029',	'2026-09-27 12:26:41.769033',	15),
(8,	'Get Test Conversation',	'2026-09-27 12:26:41.937871',	'2026-09-27 12:26:41.937875',	16),
(9,	'Chat Test',	'2026-09-27 12:26:42.280157',	'2026-09-27 12:26:42.280161',	18),
(10,	'Chat Test',	'2026-09-27 12:26:42.458144',	'2026-09-27 12:26:42.458151',	19),
(11,	'Chat Test',	'2026-09-27 12:26:42.786604',	'2026-09-27 12:26:42.786608',	21),
(12,	'Python Learning',	'2026-09-27 12:26:43.146299',	'2026-09-27 12:26:43.146307',	23),
(13,	'Python Learning',	'2026-09-27 12:26:43.522714',	'2026-09-27 12:26:43.522718',	25),
(14,	'Private Conversation',	'2026-09-27 12:26:43.858055',	'2026-09-27 12:26:43.858059',	27),
(15,	'Protected Conversation',	'2026-09-27 12:35:24.953023',	'2026-09-27 12:35:24.953028',	31),
(16,	'Get Test Conversation',	'2026-09-27 12:35:25.188099',	'2026-09-27 12:35:25.188104',	32),
(17,	'Chat Test',	'2026-09-27 12:35:25.637427',	'2026-09-27 12:35:25.637433',	34),
(18,	'Chat Test',	'2026-09-27 12:35:25.952113',	'2026-09-27 12:35:25.952121',	35),
(19,	'Chat Test',	'2026-09-27 12:35:26.541491',	'2026-09-27 12:35:26.541498',	37),
(20,	'Python Learning',	'2026-09-27 12:35:27.080846',	'2026-09-27 12:35:27.080854',	39),
(21,	'Python Learning',	'2026-09-27 12:35:27.425141',	'2026-09-27 12:35:27.425145',	41),
(22,	'Private Conversation',	'2026-09-27 12:35:27.88884',	'2026-09-27 12:35:27.888845',	43);

DROP TABLE IF EXISTS "messages";
DROP SEQUENCE IF EXISTS messages_id_seq;
CREATE SEQUENCE messages_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."messages" (
    "id" integer DEFAULT nextval('messages_id_seq') NOT NULL,
    "conversation_id" integer NOT NULL,
    "role" character varying NOT NULL,
    "content" text NOT NULL,
    "model" character varying,
    "input_tokens" integer,
    "output_tokens" integer,
    "created_at" timestamp NOT NULL,
    CONSTRAINT "messages_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE INDEX ix_messages_conversation_id ON public.messages USING btree (conversation_id);

INSERT INTO "messages" ("id", "conversation_id", "role", "content", "model", "input_tokens", "output_tokens", "created_at") VALUES
(1,	36,	'user',	'What is FastAPI?',	NULL,	NULL,	NULL,	'2026-09-25 12:21:58.684945'),
(2,	36,	'assistant',	'FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ that emphasizes automatic validation, type hints, and developer productivity.

Key points
- Built on Starlette (ASGI) and Pydantic. Uses ASGI for async I/O and Pydantic for data parsing/validation.
- Uses Python type hints to declare request parameters, body models, and response types. That enables automatic input validation and helpful editor autocompletion.
- Automatically generates interactive API documentation (Swagger UI and ReDoc) from your code.
- High performance — comparable to frameworks written in Node/Go — thanks to async support and efficient internals.
- Includes useful features out of the box: dependency injection, background tasks, WebSocket support, OAuth2/JWT utilities, request/response validation, and test client.

Typical use cases
- REST/JSON APIs and microservices
- ML model serving and inference endpoints
- Real-time apps using WebSockets
- Internal tooling and rapid API prototyping

Minimal example
- main.py
  from typing import Optional
  from fastapi import FastAPI
  from pydantic import BaseModel

  app = FastAPI()

  class Item(BaseModel):
      name: str
      price: float
      tax: Optional[float] = None

  @app.post("/items/")
  async def create_item(item: Item):
      return {"name": item.name, "price_with_tax": item.price + (item.tax or 0)}

Run it with an ASGI server:
- uvicorn main:app --reload

Pros
- Fast development with clear, type-driven APIs
- Automatic docs and validation
- Great async support and performance
- Strong typing improves reliability and IDE help

Limitations / considerations
- Learning curve if you’re new to async programming or type hints
- More geared to APIs than full server-rendered web apps (though you can still render templates)
- Depends on Pydantic and Starlette, so patching/upgrading their internals can affect behavior

In short: FastAPI is an excellent choice when you need high-performance, type-safe APIs in Python with fast developer iteration and built-in docs.',	'gpt-5-mini-2025-08-07',	26,	652,	'2026-09-25 12:22:07.454581'),
(3,	36,	'user',	'What did I just ask you about?',	NULL,	NULL,	NULL,	'2026-09-26 14:59:20.446188'),
(4,	36,	'assistant',	'You asked about FastAPI — specifically, "What is FastAPI?"',	'gpt-5-mini-2025-08-07',	522,	87,	'2026-09-26 14:59:20.462728'),
(5,	9,	'user',	'What is FastAPI?',	NULL,	NULL,	NULL,	'2026-09-27 12:26:42.29795'),
(6,	9,	'assistant',	'FastAPI is a Python web framework.',	'test-model',	10,	8,	'2026-09-27 12:26:42.30544'),
(7,	10,	'user',	'Hello NexaAI',	NULL,	NULL,	NULL,	'2026-09-27 12:26:42.470469'),
(8,	10,	'assistant',	'Test response',	'test-model',	5,	3,	'2026-09-27 12:26:42.475881'),
(9,	17,	'user',	'What is FastAPI?',	NULL,	NULL,	NULL,	'2026-09-27 12:35:25.676806'),
(10,	17,	'assistant',	'FastAPI is a Python web framework.',	'test-model',	10,	8,	'2026-09-27 12:35:25.697342'),
(11,	18,	'user',	'Hello NexaAI',	NULL,	NULL,	NULL,	'2026-09-27 12:35:25.997109'),
(12,	18,	'assistant',	'Test response',	'test-model',	5,	3,	'2026-09-27 12:35:26.019882');

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
(70,	'dev@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$QmRxmd0zUD0JCR6kiwkZ1g$qPf8i6XXL0Seeg6lGWPla07jNpze8kBP0E+xLRFh0mc',	'2026-09-25 09:46:30.089699',	'2026-09-25 09:46:30.089702'),
(71,	'testdev@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$CJki9PYvgTD7YWPNB+wVmw$I9ArnsPgznh7avVpcQdmXD0XjrgTe6oD8wPQLH6aRlk',	'2026-09-25 11:49:16.338849',	'2026-09-25 11:49:16.338852'),
(1,	'test-12b9c960@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$8toZFpL+rOEAExuVPAL/Rw$VIPWqdkhl0CWxVh9LbcX13GUMkNh1PC5z7jqyWpTHmQ',	'2026-09-26 15:02:08.076702',	'2026-09-26 15:02:08.07671'),
(2,	'login-c3b0bb32@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$fSVN33GbTdKzXSjWgX2mgQ$1EyiWWouW8/ppC7zuQufoiZyEBDVGmX9V3Qvd+3kCVc',	'2026-09-26 15:02:08.177717',	'2026-09-26 15:02:08.177724'),
(3,	'protected-ece946d6@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$/d77ZT+rP9QoM9s0IJg0ww$sQYJ/wgItbK0mG4AnqlCxyjxOIdEEF7MG8qWV2be7ro',	'2026-09-26 15:02:08.397984',	'2026-09-26 15:02:08.397998'),
(4,	'get-b7e11144@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$zhqBGCyy0wmW0h8FXVcTGw$L5Q+bxmtM3WOvEOUzoKte+qpGRZGpOZ0PEh5uuNo4M4',	'2026-09-26 15:02:08.622392',	'2026-09-26 15:02:08.622398'),
(5,	'not-found-2b1e44dc@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$wwUqfxHhfxmYpPB5JLk53A$u/u39H1xjARmhCTs1Y9E1kjEuZ6NPsGXrb7giCQkmKE',	'2026-09-26 15:02:08.828322',	'2026-09-26 15:02:08.828328'),
(6,	'conversation-05a2a600@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$uSzcvWw6FTz8YQdzs7Zvfw$3N+p1KlafRH40Z02X1Qx2+5pc4DaXrqxp51q+/Eimjg',	'2026-09-26 15:02:09.03419',	'2026-09-26 15:02:09.034196'),
(7,	'conversation-d78a6ce3@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$bfbU6qRWzk7M2VdzOQ9zKA$UVPhxl9jmrGq//zF9D+3a3ifRROr2M1m+ehxwU4PLpA',	'2026-09-26 15:02:09.220247',	'2026-09-26 15:02:09.220254'),
(8,	'conversation-34dd0c52@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$WW/5TFMPSAJFX13XhTcJ2w$iVw0kIrsV79wi2LNUIb6RhlbukeZiOrS0n2Ttql8Fto',	'2026-09-26 15:02:09.42436',	'2026-09-26 15:02:09.424367'),
(9,	'conversation-aa371ad9@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$lE8BA3LUpC0cC+eyNjeN1w$npB2/6f/pKWbA3nQqfaqJBVW+xSSLqmZEuS+s10H7GU',	'2026-09-26 15:02:09.630151',	'2026-09-26 15:02:09.630158'),
(10,	'conversation-ccdaf09b@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$NJrIAhdPf7JNNzLg53yp1w$LlA11SyIEcbHU0WWGTPjoWRJrs+7WE1mklP8gA+98NI',	'2026-09-26 15:02:09.851745',	'2026-09-26 15:02:09.851752'),
(11,	'conversation-e926c382@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$LZmewvCAVucpIAjJcM/1Hg$4dw4h9bentxPOkEy96dcPT4DsTRLgEZtIQ52nkMD8QI',	'2026-09-26 15:02:10.041985',	'2026-09-26 15:02:10.042003'),
(12,	'docker-test@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$S+m2cloDQZv5Cd14G6POag$nN7+Es/E13xvGgC6ARMlKZLDue59VTlzjZbFwmkp/Gs',	'2026-09-27 09:23:38.783972',	'2026-09-27 09:23:38.783991'),
(13,	'test-6a145a30@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$DdIipn8S5CVXVdII8134XA$WWfP0hK1Q8sQiKtVi7dTQJ1H2+HPy1cvBm1YCwLreoI',	'2026-09-27 12:26:41.398983',	'2026-09-27 12:26:41.398991'),
(14,	'login-ec181adf@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$6HslG9zxWgkuhFf3Wr20YA$Lgtn1JZbWQu8HLcET/EfA4n7Ie6ptLcg52O6ok+uHu4',	'2026-09-27 12:26:41.50534',	'2026-09-27 12:26:41.505347'),
(15,	'protected-1c52cf84@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$meKF2MVw72DZIWvFQuFOhQ$VCLT5GgZg4tWZt3JUlahsFJ1Y5yFXrzmKTSNxwPW+e4',	'2026-09-27 12:26:41.672799',	'2026-09-27 12:26:41.672807'),
(16,	'get-44b778c4@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$luuCntfVHXKxtvKb3AsVHQ$nLpwBmYhXFc5bO9C1K8gpbfGHcBgR1g11UC4ZUu3ryk',	'2026-09-27 12:26:41.855359',	'2026-09-27 12:26:41.855365'),
(17,	'not-found-30e6532d@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$NH1uPvXfBDSWAmCGAOh+bQ$mEBgyk9HmCUYDI/2oLzDzDxJs1CaJSQDCaQ04gIRRIg',	'2026-09-27 12:26:42.036974',	'2026-09-27 12:26:42.03698'),
(18,	'chat-95be1c0e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$VoK/fUYNCPng/Zkd7TsfOA$OpcoDX8pXpbN+Jal2OYJSZw7NYfz3ohfyb3XpKVWA0w',	'2026-09-27 12:26:42.197179',	'2026-09-27 12:26:42.197191'),
(19,	'chat-d598b22a@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$MFCMzB1MonPZjnjgxg0r7A$a4lTNA5Hjhk3o7cNzJkvvSLo2+eKLBLv1C67uijjNCg',	'2026-09-27 12:26:42.383946',	'2026-09-27 12:26:42.383952'),
(20,	'chat-57933451@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$yul25fG8STWoIXwo5RFKug$rtL/jHqoFSKRPvvQVYE2jHrOq6aFoVAK7gn2NBHBfK0',	'2026-09-27 12:26:42.556309',	'2026-09-27 12:26:42.556314'),
(21,	'chat-053ab1df@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$kLpfYYYYGdJnr3fG5120QA$2PHlLWwEUP4ytCRPI6kJjz0pdEltCZrCHGvovfYjPo4',	'2026-09-27 12:26:42.708957',	'2026-09-27 12:26:42.708963'),
(22,	'chat-53a52676@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$Txqtz+/pS/4Rv4kBkTaWHQ$IRJLPyWdpltyXQFa/ZQut2GEf6anmUigR8e6LYbRXLQ',	'2026-09-27 12:26:42.85213',	'2026-09-27 12:26:42.852135'),
(23,	'conversation-ff0e7c25@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$O/3Iw/4LDQ1EHNTHeQT2eg$FL8hHpUQIYyenAeK6nAS6aEIQSy1c82Sgubmgy6NRCY',	'2026-09-27 12:26:43.012232',	'2026-09-27 12:26:43.012254'),
(24,	'conversation-51a8f5d3@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$uESAs31KEIeVIEMKkzjT+g$Eno/F1kIPtudWPMMkLUZ8V60OoimEN7+PKMyJ/Py2Uw',	'2026-09-27 12:26:43.263532',	'2026-09-27 12:26:43.26354'),
(25,	'conversation-d63c1bc5@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$kgmchBF4XqWELgQTq2f2rw$2eie4BcOddGraS/WgfiFlVmBBWmdPxpqU+3R/gY4YAM',	'2026-09-27 12:26:43.444863',	'2026-09-27 12:26:43.444869'),
(26,	'conversation-ea4d4f9a@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$9AQ5fMTjKRY9DeqP2UdCCA$QPbWKmk3EJyTQ6HO4lUvmUR9pp/PqQCkLRGZvgpErxc',	'2026-09-27 12:26:43.60982',	'2026-09-27 12:26:43.609834'),
(27,	'conversation-c4a5d171@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$QSEAjCbZraHDNtJMvuWUJg$apeP9pjo9i3auodgoQRLMgTa5yoHiHc6Z4riI7eX0s8',	'2026-09-27 12:26:43.776182',	'2026-09-27 12:26:43.776191'),
(28,	'conversation-f82c144f@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$7HQo7RHhmNBUfKxWz2QeAg$BM4jZaojLiCK+mzAVJU/OaUIKYa2nrKB7QDte25ZwCw',	'2026-09-27 12:26:43.922354',	'2026-09-27 12:26:43.922359'),
(29,	'test-f4ad5ab6@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$S1TXtAB1BLlH8ZFDnAw+XA$Nyazsw+ilw0kAH584zxfkQMMs8t3XZDVC69JK0N2nDU',	'2026-09-27 12:35:24.444261',	'2026-09-27 12:35:24.444277'),
(30,	'login-0aff4102@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$FZGGasEq48vsy52tnnRQxg$XbbT9loyjet/Ir4735lRGMTml5i8uQIaE9NEjxtuDxo',	'2026-09-27 12:35:24.595729',	'2026-09-27 12:35:24.595738'),
(31,	'protected-f66ecd31@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$IeS48HKpv4H6F0+CPI2Wog$0GOI9K5sqwiViKtiae/m91Cv29JkQELq0/f0O1EIQ/8',	'2026-09-27 12:35:24.841219',	'2026-09-27 12:35:24.841225'),
(32,	'get-c2d4d83f@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$WKyxjcCzLzeufQDKBeOySA$Sjd3CMxLIK3Aufgf3guE+ZDddyVPjCx8KRGLoip4MLw',	'2026-09-27 12:35:25.091773',	'2026-09-27 12:35:25.091782'),
(33,	'not-found-186b119b@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$qokaqtcQcCXARqzml+QZqw$Ik+RfydjrysJaTEAPDDHzjeij3s6pOe7zguA0MUSe1k',	'2026-09-27 12:35:25.276107',	'2026-09-27 12:35:25.276113'),
(34,	'chat-b80468e1@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$QOJ49F07bjooUKa3dLGqRQ$RZXoyzGnxoCG+YjpL7hJwCe717KGLh/RvjpYvf4XjOI',	'2026-09-27 12:35:25.469111',	'2026-09-27 12:35:25.469122'),
(35,	'chat-1a2b3bb1@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$XnjNwMY/EP8crQv1o0emSg$NEUK8zUp4gRG13Jg+MTWE+SLuxH690RUh6B9y2ZYbKw',	'2026-09-27 12:35:25.852498',	'2026-09-27 12:35:25.852505'),
(36,	'chat-579bb477@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$mmAk9Ld6A+iBoeMu5kBM6Q$9Obgnu1XOAAMMiOiRRpmpqqr1wx+S3AgA8/g9idAds8',	'2026-09-27 12:35:26.144024',	'2026-09-27 12:35:26.144032'),
(37,	'chat-d624e4ca@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$dD5LZZemDvJtkNju3VfDsA$xRnC8SHcLwh3EN6GjxZisWE1snpUY6zQlOYXrOlMXkg',	'2026-09-27 12:35:26.403622',	'2026-09-27 12:35:26.403629'),
(38,	'chat-0d5acc97@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$KynQtnHapYHHgKRrz+n3pg$f8B2hYbYgxVTY4m4OAw6/s8KH2xmRlJb5m/X4JrITc0',	'2026-09-27 12:35:26.656247',	'2026-09-27 12:35:26.656253'),
(39,	'conversation-db48b3c4@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$lW5Mt7hM3zsQGoHUg2UsDQ$AP+LpOkOfSvm0rLGEUMzV6l5y87sIdoG30ZpboVMzW4',	'2026-09-27 12:35:26.891976',	'2026-09-27 12:35:26.891984'),
(40,	'conversation-e566de7e@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$fsHPMlscaNK83gRNKWViag$JiphLa1H0aIMvCBeRwr7aV/QCorIOYi+55ZMmvV9CwI',	'2026-09-27 12:35:27.178252',	'2026-09-27 12:35:27.178258'),
(41,	'conversation-f7f2c5c5@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$D3muRDAoO1RYTEpDwTD/rQ$o+U0pvOLrAvI3SelKZc28wDZ/hjz3t1k3tPqEyjhgFw',	'2026-09-27 12:35:27.342588',	'2026-09-27 12:35:27.342594'),
(42,	'conversation-6b1f59b9@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$B9zIfK1Vyr6iXG9Y28Mpvw$wDUgroqUflWN9bzjfgL75SzNkqqoAxiebEYS1kvlMJc',	'2026-09-27 12:35:27.525298',	'2026-09-27 12:35:27.525305'),
(43,	'conversation-e5032de0@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$33L9ttW03dYAT8Ipr/Y/SA$xQMczemmyrv2ytIldCmalJcTkCCdE+sOXd+8Loe9IcM',	'2026-09-27 12:35:27.803691',	'2026-09-27 12:35:27.803697'),
(44,	'conversation-33ad8451@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$fhfhZpk9FGKdEWo1NZ41AQ$XL8PCNs5oNf0C0wsp1Ip8p8621vWLAmtUF/LiKhXE98',	'2026-09-27 12:35:27.969093',	'2026-09-27 12:35:27.969099');

ALTER TABLE ONLY "public"."conversations" ADD CONSTRAINT "fk_conversations_user_id_users" FOREIGN KEY (user_id) REFERENCES users(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."messages" ADD CONSTRAINT "messages_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES conversations(id) NOT DEFERRABLE;

-- 2026-09-29 15:47:14 UTC
