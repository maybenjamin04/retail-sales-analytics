--total revanue
SELECT 
    SUM(price + COALESCE(freight_value, 0)) as revenue
FROM order_items;

/*FROM orders t1
INNER JOIN order_items t2 
    ON t1.id = t2.order_id;*/

--number of orders
SELECT COUNT(*) orders;

--number of items sold
SELECT COUNT(*) order_items;

--average value of orders
SELECT 
    AVG(order_total) AS avg_order_value
FROM (
    SELECT 
        t1.id,
        SUM(t2.price + COALESCE(t2.freight_value, 0)) AS order_total
    FROM orders t1
    INNER JOIN order_items t2 
        ON t1.id = t2.order_id
    GROUP BY t1.id
) order_totals;

--Monthly Revanue
SELECT 
    SUM(t2.price + COALESCE(t2.freight_value, 0)) as revenue,
    t1.purchase_timestamp
FROM orders t1
INNER JOIN order_items t2
     ON t1.id = t2.order_id
GROUP BY DATE(t1.purchase_timestamp)
ORDER BY DATE(t1.purchase_timestamp);


--canceled orders
SELECT * orders WHERE order_status = 'canceled';



--Revanue by state
/*SELECT t1.id,
        MAX(t2.order_item_id) * t2.price AS total_order_price,
        t1.purchase_timestamp AS purchase_date
    FROM orders t1
    RIGHT JOIN order_items t2
        ON t1.id = t2.order_id
    GROUP BY t1.id, t2.price;*?


/*SELECT t1.state_code, MAX(t4.order_item_id) * t4.price as total_order_price, t2.id as customer_id, t3.id as order_id 
FROM geolocation t1 
LEFT JOIN customers t2 ON t1.zip_code_prefix = t2.zip_code_prefix
INNER JOIN orders t3 ON t2.id = t3.customer_id
LEFT JOIN order_items t4 ON t3.id = t4.order_id
GROUP BY t1.state_code, t2.id, t3.id, t4.price;*/

--checking if joins are correct

/*SELECT COUNT(*)
FROM geolocation t1 
LEFT JOIN customers t2 ON t1.zip_code_prefix = t2.zip_code_prefix*/

/*SELECT COUNT(DISTINCT t2.id) as num_customers, COUNT(DISTINCT t3.id) as num_orders 
FROM customers t2
INNER JOIN orders t3 ON t2.id = t3.customer_id;*/

SELECT COUNT(*)
FROM orders t3 
RIGHT JOIN order_items t4 ON t3.id = t4.order_id;

--MAX(order_item_id) * price = total order price
