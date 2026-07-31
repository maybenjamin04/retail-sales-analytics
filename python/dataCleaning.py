import pandas as pd


# THINGS TO DO

# merge customers with geolocation
# 
# merge sellers with geolocation
#
# merge products with product translation

#geolocation, reviews later

#load everything
customers = pd.read_csv('../data/raw/olist_customers_dataset.csv')
geolocation = pd.read_csv('../data/raw/olist_geolocation_dataset.csv')
order_items = pd.read_csv('../data/raw/olist_order_items_dataset.csv')
payments = pd.read_csv('../data/raw/olist_order_payments_dataset.csv')
reviews = pd.read_csv('../data/raw/olist_order_reviews_dataset.csv')
orders = pd.read_csv('../data/raw/olist_orders_dataset.csv')
products = pd.read_csv('../data/raw/olist_products_dataset.csv')
sellers = pd.read_csv('../data/raw/olist_sellers_dataset.csv')
translation = pd.read_csv('../data/raw/product_category_name_translation.csv')


def inspect_dataframe(df, name):
    print(f"\n=== {name} ===")
    print(df.info())
    print("Missing values:")
    print(df.isna().sum())
    print(f"Duplicate rows: {df.duplicated().sum()}")

    key_candidates = [col for col in df.columns if col.endswith('_id') or col == 'id']
    if key_candidates:
        key_col = key_candidates[0]
        print(f"Unique {key_col}: {df[key_col].nunique()}")

    print(f"Row count: {len(df)}")

def print_raw_dataframe_info():
    for dataframe_name, dataframe in {
        'customers': customers,
        'geolocation': geolocation,
        'order_items': order_items,
        'payments': payments,
        'orders': orders,
        'products': products,
        'sellers': sellers,
        'translation': translation
    }.items():
        inspect_dataframe(dataframe, dataframe_name)


# customers 
#inspect_dataframe(customers, 'customers')

#no missing values so fair to put into clean csv
cleaned_customers = customers.copy(deep=True)
cleaned_customers['customer_zip_code_prefix'] = cleaned_customers['customer_zip_code_prefix'].astype('string').fillna('').str.zfill(5)


assert cleaned_customers['customer_id'].is_unique
assert cleaned_customers['customer_id'].notna().all()

cleaned_customers.columns = cleaned_customers.columns.str.removeprefix('customer_')
inspect_dataframe(cleaned_customers, 'customers')
#print(cleaned_customers)

#geolocation

#geolocation has many duplicates
cleaned_geolocation = geolocation.drop_duplicates(subset='geolocation_zip_code_prefix', keep='first').copy(deep=True)
cleaned_geolocation['geolocation_zip_code_prefix'] = cleaned_geolocation['geolocation_zip_code_prefix'].astype('string').fillna('').str.zfill(5)

assert cleaned_geolocation['geolocation_zip_code_prefix'].is_unique
assert cleaned_geolocation['geolocation_zip_code_prefix'].notna().all()

cleaned_geolocation.columns = cleaned_geolocation.columns.str.removeprefix('geolocation_')
inspect_dataframe(cleaned_geolocation, 'geolocation')
#print(cleaned_geolocation)

#order items
#inspect_dataframe(order_items, 'order_items')
cleaned_order_items = order_items.copy(deep=True)
cleaned_order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'])

# order_id + order_item_id are pk
assert not cleaned_order_items.duplicated(subset=['order_id', 'order_item_id']).any()
assert cleaned_order_items['order_id'].notna().all()
assert cleaned_order_items['order_item_id'].notna().all()


#payments
# unsure if payment 0.0 means free? for now clean 
#inspect_dataframe(payments, 'payments')
cleaned_payments = payments.copy(deep=True)

assert not cleaned_payments.duplicated(subset=['order_id', 'payment_sequential']).any()
assert cleaned_payments['order_id'].notna().all()
assert cleaned_payments['payment_sequential'].notna().all()

cleaned_payments.columns = cleaned_payments.columns.str.removeprefix('payment_')
inspect_dataframe(cleaned_payments, 'payments')

# reviews
#inspect_dataframe(reviews, 'reviews')

reviews_strings = reviews.select_dtypes(include=['object', 'string']).columns
replace_str_dict = {col: 'Unknown' for col in reviews_strings}
cleaned_reviews = reviews.fillna(value=replace_str_dict)


assert not cleaned_reviews.duplicated(subset=['review_id', 'order_id']).any()
assert cleaned_reviews['order_id'].notna().all()
assert cleaned_reviews['review_id'].notna().all()


cleaned_reviews.columns = cleaned_reviews.columns.str.removeprefix('review_')
inspect_dataframe(cleaned_reviews, 'reviews')

#orders
#inspect_dataframe(orders, 'orders')

cleaned_orders = orders.copy(deep=True)
cleaned_orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
cleaned_orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])
cleaned_orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'])
cleaned_orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
cleaned_orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])


assert cleaned_orders['order_id'].is_unique
assert cleaned_orders['order_id'].notna().all()

cleaned_orders.columns = cleaned_orders.columns.str.removeprefix('order_')
inspect_dataframe(cleaned_orders, 'orders')


# products
assert products['product_id'].is_unique
assert products['product_id'].notna().all()

#check if numbers are positive
float_cols = products.select_dtypes(include=["float64"])
if not float_cols.empty:
    assert products[float_cols > 0].all().all()

#translation
#assert translation['product_category_name'].is_unique
#assert translation["product_category_name"].notna().all()

# merge translation and products so theres english translation for name
cleaned_translated_products = pd.merge(products, translation, on='product_category_name', how='left')
cleaned_translated_products.insert(2, 'product_category_name_english',cleaned_translated_products.pop('product_category_name_english'))
cleaned_translated_products = cleaned_translated_products.rename(columns={'product_name_lenght': 'product_name_length', 'product_description_lenght': 'product_description_length'})
#print(cleaned_translated_products.info())

#product name null to Unknown
products_strings = cleaned_translated_products.select_dtypes(include=['object', 'string']).columns
replace_str_dict = {col: 'Unknown' for col in products_strings}
cleaned_translated_products = cleaned_translated_products.fillna(value=replace_str_dict)
#print(len(cleaned_translated_products[cleaned_translated_products['product_category_name'] == 'Unknown']))

#nan values for 0 in float64 cols
cleaned_translated_products = cleaned_translated_products.fillna(0.0)

#print(len(cleaned_translated_products[cleaned_translated_products.eq(0.0).any(axis=1)]))

assert cleaned_translated_products['product_id'].is_unique
assert cleaned_translated_products['product_id'].notna().all()

cleaned_translated_products.columns = cleaned_translated_products.columns.str.removeprefix('product_')
inspect_dataframe(cleaned_translated_products, 'products')

#sellers
#inspect_dataframe(sellers, 'sellers')
cleaned_sellers = sellers.copy(deep=True)
cleaned_sellers['seller_zip_code_prefix'] = cleaned_sellers['seller_zip_code_prefix'].astype('string').fillna('').str.zfill(5)

assert cleaned_sellers['seller_id'].is_unique
assert cleaned_sellers['seller_id'].notna().all()

cleaned_sellers.columns = cleaned_sellers.columns.str.removeprefix('seller_')
inspect_dataframe(cleaned_sellers, 'sellers')


CLEANED_CSV = {
        'customers': cleaned_customers,
        'geolocation': cleaned_geolocation ,
        'order_items': cleaned_order_items,
        'payments': cleaned_payments,
        'reviews': cleaned_reviews,
        'orders': cleaned_orders,
        'products': cleaned_translated_products,
        'sellers': cleaned_sellers
    }


for filename, df in CLEANED_CSV.items():
    df.to_csv(f'../data/processed/cleaned/{filename}.csv', index=False)