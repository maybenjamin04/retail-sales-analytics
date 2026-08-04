/*

These sql queries give good analytics for data you can export these
by using \copy (one-of-the-queries-below) TO 'desired/path' WITH (FORMAT CSV, HEADER);

*/


--Monthly Sales
SELECT 
    TO_CHAR(t1.purchase_timestamp, 'YYYY-MM') AS year_month,
    ROUND(SUM(t2.price::numeric), 2) AS total_item_value,
    ROUND(SUM(t2.freight_value::numeric), 2) AS total_freight_value,
    ROUND(SUM(t2.price::numeric + COALESCE(t2.freight_value::numeric, 0)), 2) AS total_revenue
FROM orders t1
INNER JOIN order_items t2 
    ON t1.id = t2.order_id
GROUP BY TO_CHAR(t1.purchase_timestamp, 'YYYY-MM')
ORDER BY year_month DESC;

--Reavanue by product category
SELECT t1.category_name_english,
       COUNT(t2.product_id) as num_items, 
       ROUND(SUM(t2.price::numeric + COALESCE(t2.freight_value::numeric, 0)), 2) as revenue
FROM products t1
    INNER JOIN order_items t2 
    ON t2.product_id = t1.id
GROUP BY t1.category_name_english
ORDER BY revenue DESC;

--Delivery Performance
SELECT id, approved_at,
delivered_customer_date::timestamp - approved_at::timestamp as delivery_time, 
estimated_delivery_date::timestamp - approved_at::timestamp as estimated_delivery_time,
delivered_customer_date::timestamp - estimated_delivery_date::timestamp as delay_time, 
order_status
FROM orders;

--Seller Performance
SELECT t1.id,
       t5.state_code,
       t6.category_name_english,
       COUNT(t2.product_id) as num_products_sold,
       ROUND(SUM(t2.price::numeric + COALESCE(t2.freight_value::numeric, 0)), 2) as revenue,
       ROUND(AVG(t4.score), 2) as avg_review_score,
       COUNT(DISTINCT t4.id) as num_reviews
FROM sellers t1
    INNER JOIN order_items t2 ON t1.id = t2.seller_id
    INNER JOIN orders t3 ON t2.order_id = t3.id
    INNER JOIN products t6 ON t2.product_id = t6.id
    LEFT JOIN reviews t4 ON t3.id = t4.order_id
    INNER JOIN geolocation t5 ON t1.zip_code_prefix = t5.zip_code_prefix
GROUP BY t1.id, t5.state_code, t6.category_name_english
ORDER BY t1.id, revenue DESC;

--Date Revenue
SELECT 
    t1.id,
    t1.purchase_timestamp,
    ROUND(SUM(t2.price::numeric), 2) AS total_item_value,
    ROUND(SUM(t2.freight_value::numeric), 2) AS total_freight_value,
    ROUND(SUM(t2.price::numeric + COALESCE(t2.freight_value::numeric, 0)), 2) AS total_revenue
FROM orders t1
INNER JOIN order_items t2 
    ON t1.id = t2.order_id
GROUP BY t1.id, t1.purchase_timestamp
ORDER BY t1.purchase_timestamp DESC;

