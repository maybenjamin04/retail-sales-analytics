DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS geolocation CASCADE;

CREATE TABLE geolocation (
    zip_code_prefix char(5) PRIMARY KEY,
    lat double precision NULL,
    lng double precision NULL,
    city varchar(255),
    state_code varchar(2)
);

CREATE TABLE customers (
    id char(32) PRIMARY KEY,
    unique_id char(32),
    zip_code_prefix char(5) REFERENCES geolocation(zip_code_prefix)
);

CREATE TABLE sellers (
    id char(32) PRIMARY KEY,
    zip_code_prefix char(5) REFERENCES geolocation(zip_code_prefix)
);

CREATE TABLE orders (
    id char(32) PRIMARY KEY,
    customer_id char(32) REFERENCES customers(id),
    order_status varchar(255),
    purchase_timestamp timestamp,
    approved_at timestamp,
    delivered_carrier_date timestamp,
    delivered_customer_date timestamp,
    estimated_delivery_date timestamp
);

CREATE TABLE products (
    id char(32) PRIMARY KEY,
    category_name varchar(255),
    category_name_english varchar(255),
    name_length int,
    description_length int,
    photos_qty int,
    weight_g int,
    length_cm int,
    height_cm int,
    width_cm int
);

CREATE TABLE order_items (
    order_id char(32),
    order_item_id int,
    product_id char(32) REFERENCES products(id),
    seller_id char(32) REFERENCES sellers(id),
    shipping_limit_date timestamp,
    price double precision,
    freight_value double precision,

    PRIMARY KEY (order_id, order_item_id),

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
);

CREATE TABLE payments (
    order_id char(32),
    sequential int,
    payment_type varchar(255),
    installments int,
    amount double precision,

    PRIMARY KEY (order_id, sequential),

    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
);

CREATE TABLE reviews (
    id char(32),
    order_id char(32),
    score int,
    comment_title varchar(255),
    comment_message varchar(255),
    creation_date timestamp,
    answer_timestamp timestamp,

    PRIMARY KEY (id, order_id),

    CONSTRAINT fk_review_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
);