-- Adminer 5.4.1 PostgreSQL 17.11 dump

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
(36,	'FastAPI Learning',	'2026-09-25 11:52:21.317598',	'2026-09-25 11:52:21.3176',	71);

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

In short: FastAPI is an excellent choice when you need high-performance, type-safe APIs in Python with fast developer iteration and built-in docs.',	'gpt-5-mini-2025-08-07',	26,	652,	'2026-09-25 12:22:07.454581');

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
(71,	'testdev@example.com',	'$argon2id$v=19$m=65536,t=3,p=4$CJki9PYvgTD7YWPNB+wVmw$I9ArnsPgznh7avVpcQdmXD0XjrgTe6oD8wPQLH6aRlk',	'2026-09-25 11:49:16.338849',	'2026-09-25 11:49:16.338852');

ALTER TABLE ONLY "public"."conversations" ADD CONSTRAINT "fk_conversations_user_id_users" FOREIGN KEY (user_id) REFERENCES users(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."messages" ADD CONSTRAINT "messages_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES conversations(id) NOT DEFERRABLE;

-- 2026-09-25 12:37:57 UTC
