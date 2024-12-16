CREATE TABLE IF NOT EXISTS product_category (
	"category_id" int4 NOT NULL PRIMARY KEY,
	"name" varchar(512) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
	"product_id" varchar(36) NOT NULL PRIMARY KEY,
	"name" varchar(512) NOT NULL,
	"category_id" int4 NOT NULL,
	"weight" decimal NULL,
	"price" decimal NOT NULL,
    FOREIGN KEY("category_id") REFERENCES product_category("category_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS customers (
	"customer_id" varchar(36) NOT NULL PRIMARY KEY,
	"name" varchar(64) NULL,
	"surname" varchar(64) NULL,
	"address" varchar(256) NOT NULL,
	"state" varchar(2) NOT NULL,
	"gender" char DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS orders (
	"order_id" varchar(36) NOT NULL PRIMARY KEY,
	"customer_id" varchar(36) NOT NULL,
	"order_time" timestamp DEFAULT NULL,
	"shipping_time" timestamp DEFAULT NULL,
	"status" varchar(24) NOT NULL,
	FOREIGN KEY("customer_id") REFERENCES customers("customer_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS plans (
	"plan_id" int4 NOT NULL PRIMARY KEY,
	"name" varchar(64) NOT NULL,
	"max_parallel_sessions" int4 NOT NULL
);

CREATE TABLE IF NOT EXISTS sellers (
	"seller_id" varchar(36) NOT NULL PRIMARY KEY,
	"password" varchar(64) NOT NULL,
	"session_count" int4 NOT NULL,
	"plan_id" int4 NOT NULL,
	FOREIGN KEY("plan_id") REFERENCES plans("plan_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS shopping_carts (
	"order_id" varchar(36) NOT NULL,
	"product_id" varchar(36) NOT NULL,
	"seller_id" varchar(36) NOT NULL,
	"amount" int4 NOT NULL,
	FOREIGN KEY("order_id") REFERENCES orders("order_id") ON DELETE CASCADE,
	FOREIGN KEY("product_id") REFERENCES products("product_id") ON DELETE CASCADE,
	FOREIGN KEY("seller_id") REFERENCES sellers("seller_id") ON DELETE CASCADE,
	CONSTRAINT shopping_carts_un UNIQUE (order_id, product_id, seller_id)
);


CREATE TABLE IF NOT EXISTS stocks (
	"product_id" varchar(36) NOT NULL,
	"seller_id" varchar(36) NOT NULL,
	"stock_count" int4 NOT NULL,
	FOREIGN KEY("product_id") REFERENCES products("product_id") ON DELETE CASCADE,
	FOREIGN KEY("seller_id") REFERENCES sellers("seller_id") ON DELETE CASCADE,
	CONSTRAINT stocks_un UNIQUE (product_id, seller_id)
);