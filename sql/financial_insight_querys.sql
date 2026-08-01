-- Most valuable months
SELECT SUM(total_price) as date_price, purchase_date FROM
(SELECT t1.id, 
MAX(t2.order_item_id) * t2.price as total_price, 
t1.purchase_timestamp as purchase_date
FROM orders t1  
RIGHT JOIN order_items t2 
ON t1.id = t2.order_id 
GROUP BY t2.price, t1.id) GROUP BY purchase_date ORDER BY purchase_date;