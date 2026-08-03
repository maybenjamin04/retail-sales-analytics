import pandas as pd
from loadToPostgreSQL import load_cleaned_data
from dataCleaning import inspect_dataframe
cleaned_data = load_cleaned_data()

orders = cleaned_data['orders']
order_items = cleaned_data['order_items']
reviews = cleaned_data['reviews']
customers = cleaned_data['customers']

orders = orders.rename(columns={'id': 'order_id'})
customers = customers.rename(columns={'id': 'customer_id', 'unique_id': 'customer_unique_id'})
#reviews = reviews.rename(columns={'score': 'review_score'})

inspect_dataframe(orders, 'orders')
inspect_dataframe(order_items, 'order_items')
#inspect_dataframe(reviews, 'reviews')


# ORDERS SUMMARY

orders_summary = pd.merge(orders, order_items, on='order_id', how='right')

num_items_in_order = orders_summary.value_counts(orders_summary['order_id'])
#print(num_items_in_order)
orders_summary['item_count'] = orders_summary['order_id'].map(orders_summary['order_id'].value_counts())
orders_summary = orders_summary.drop_duplicates(subset=['order_id']) 


orders_summary = pd.merge(orders_summary, customers, on='customer_id', how='inner')

#orders_summary = pd.merge(orders_summary, reviews, on='order_id', how='inner')

#print(orders_summary[['delivered_carrier_date', 'delivered_customer_date', 'estimated_delivery_date','shipping_limit_date']])
# Delivery time in days
#inspect_dataframe(orders_summary, 'order summary')
orders_summary['delivery_time'] = orders_summary['delivered_customer_date'] - orders_summary['approved_at']
orders_summary['estimated_delivery_time'] = orders_summary['estimated_delivery_date'] - orders_summary['approved_at']
orders_summary['delivery_delay'] = orders_summary['delivered_customer_date'] - orders_summary['estimated_delivery_date']
#orders_summary[]
#delivery_in_days = (orders_summary['delivered_customer_date'] - orders_summary['approved_at']).sort_values(ascending=False)

# Delivery time estimated
#estimated_delivery_in_days = (orders_summary['delivered_customer_date'] - orders_summary['estimated_delivery_date']).sort_values(ascending=False)

'''print(delivery_in_days)
print(estimated_delivery_in_days)
print(delivery_in_days - estimated_delivery_in_days)'''

#print(orders_summary[['delivery_delay', 'delivery_time', 'estimated_delivery_time', 'order_status']].sort_values('delivery_time', ascending=False))
#print(orders_summary[['delivery_delay', 'delivery_time', 'estimated_delivery_time', 'order_status']].sort_values('delivery_time', ascending=True))
'delivery_delay'

#print(orders_summary['order_status'].unique())
orders_summary = orders_summary.drop(columns=['order_item_id', 'customer_id', 'product_id','seller_id', 'zip_code_prefix'])
                                     #'id', 'creation_date', 'answer_timestamp', 'comment_title', 'comment_message'])

#print(orders_summary)

orders_summary.to_csv(f'../data/processed/analytics/orders_summary.csv', index=False)
inspect_dataframe(orders_summary, 'orders_summary')
