#clean raw data csv files
import pandas as pd

#load raw data
customers = pd.read_csv('../data/raw/olist_customers_dataset.csv')
geolocation = pd.read_csv('../data/raw/olist_geolocation_dataset.csv')
order_items = pd.read_csv('../data/raw/olist_order_items_dataset.csv')
payments = pd.read_csv('../data/raw/olist_order_payments_dataset.csv')
reviews = pd.read_csv('../data/raw/olist_order_reviews_dataset.csv')
orders = pd.read_csv('../data/raw/olist_orders_dataset.csv')
products = pd.read_csv('../data/raw/olist_products_dataset.csv')
sellers = pd.read_csv('../data/raw/olist_sellers_dataset.csv')
translation = pd.read_csv('../data/raw/product_category_name_translation.csv')

#debug tool
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

#debug tool for all raw data
def print_raw_dataframe_info():
    for dataframe_name, dataframe in {
        'customers': customers,
        'geolocation': geolocation,
        'order_items': order_items,
        'payments': payments,
        'reviews': reviews,
        'orders': orders,
        'products': products,
        'sellers': sellers,
        'translation': translation
    }.items():
        inspect_dataframe(dataframe, dataframe_name)

'''
raw_customer_zips = set(customers['customer_zip_code_prefix'].astype(str))
raw_seller_zips = set(sellers['seller_zip_code_prefix'].astype(str))
raw_geolocation_zips = set(geolocation['geolocation_zip_code_prefix'].astype(str))

print("Raw customer zip codes subset of raw geolocation zip codes:", raw_customer_zips.issubset(raw_geolocation_zips))
print("Raw seller zip codes subset of raw geolocation zip codes:", raw_seller_zips.issubset(raw_geolocation_zips))
'''

#customers 
#inspect_dataframe(customers, 'customers')

#no missing values so fair to put into clean csv
cleaned_customers = customers.copy(deep=True)
cleaned_customers['customer_zip_code_prefix'] = cleaned_customers['customer_zip_code_prefix'].astype('str').fillna('').str.zfill(5)


assert cleaned_customers['customer_id'].is_unique
#assert cleaned_customers['customer_unique_id'].is_unique


assert cleaned_customers['customer_id'].notna().all()

cleaned_customers.columns = cleaned_customers.columns.str.removeprefix('customer_')
inspect_dataframe(cleaned_customers, 'customers')
#print(cleaned_customers)

#geolocation
# geolocation has many duplicates with slightly different lon and lats so just keep the first one 
# because there is no data to put customer/seller to specific lon and lat but state and city should be same
cleaned_geolocation = geolocation.drop_duplicates(subset='geolocation_zip_code_prefix', keep='first').copy(deep=True)
cleaned_geolocation['geolocation_zip_code_prefix'] = cleaned_geolocation['geolocation_zip_code_prefix'].astype('str').fillna('').str.zfill(5)

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
inspect_dataframe(cleaned_order_items, 'order_items')

#payments
# unsure if payment 0.0 means free? for now clean 
#inspect_dataframe(payments, 'payments')
cleaned_payments = payments.copy(deep=True)

assert not cleaned_payments.duplicated(subset=['order_id', 'payment_sequential']).any()
assert cleaned_payments['order_id'].notna().all()
assert cleaned_payments['payment_sequential'].notna().all()
assert (cleaned_payments['payment_value'] >= 0.0).all()

cleaned_payments.columns = [col.removeprefix('payment_') if col != 'payment_type' else col for col in cleaned_payments.columns]
inspect_dataframe(cleaned_payments, 'payments')

# reviews
#inspect_dataframe(reviews, 'reviews')

reviews_strings = reviews.select_dtypes(include=['object', 'string']).columns
replace_str_dict = {col: 'Unknown' for col in reviews_strings}
cleaned_reviews = reviews.fillna(value=replace_str_dict)

cleaned_reviews['review_creation_date'] = pd.to_datetime(cleaned_reviews['review_creation_date'])
cleaned_reviews['review_answer_timestamp'] = pd.to_datetime(cleaned_reviews['review_answer_timestamp'])


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

cleaned_orders.columns = [col.removeprefix('order_') if col != 'order_status' else col for col in cleaned_orders.columns]

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
cleaned_sellers['seller_zip_code_prefix'] = cleaned_sellers['seller_zip_code_prefix'].astype('str').fillna('').str.zfill(5)

assert cleaned_sellers['seller_id'].is_unique
assert cleaned_sellers['seller_id'].notna().all()

cleaned_sellers.columns = cleaned_sellers.columns.str.removeprefix('seller_')
inspect_dataframe(cleaned_sellers, 'sellers')


# Adding zips that are in customer and seller that aren't in geolocation with null lat and lgn
customer_only_zips = (
    cleaned_customers[['zip_code_prefix', 'city', 'state']]
    .drop_duplicates()
    .rename(columns={'zip_code_prefix': 'zip_code_prefix'})
)

seller_only_zips = (
    cleaned_sellers[['zip_code_prefix', 'city', 'state']]
    .drop_duplicates()
    .rename(columns={'zip_code_prefix': 'zip_code_prefix'})
)

missing_zips = pd.concat([customer_only_zips, seller_only_zips], ignore_index=True)
missing_zips = missing_zips.drop_duplicates(subset=['zip_code_prefix'])
missing_zips = missing_zips.loc[~missing_zips['zip_code_prefix'].isin(cleaned_geolocation['zip_code_prefix'])]

missing_zips['lat'] = pd.NA
missing_zips['lng'] = pd.NA
missing_zips = missing_zips.rename(columns={'zip_code_prefix': 'zip_code_prefix'})

cleaned_geolocation = pd.concat([cleaned_geolocation, missing_zips], ignore_index=True)

#new_geolocation_rows = cleaned_geolocation[cleaned_geolocation['lat'].isna() & cleaned_geolocation['lng'].isna()]
#print("New geolocation rows with null lat/lng:")
#print(new_geolocation_rows.to_string(index=False))


# Just a double check that all zips are now in geolocation
cleaned_customer_zips = set(cleaned_customers['zip_code_prefix'].astype(str))
cleaned_seller_zips = set(cleaned_sellers['zip_code_prefix'].astype(str))
cleaned_geolocation_zips = set(cleaned_geolocation['zip_code_prefix'].astype(str))

assert cleaned_customer_zips.issubset(cleaned_geolocation_zips)
assert cleaned_seller_zips.issubset(cleaned_geolocation_zips)

cleaned_customers = cleaned_customers.drop(columns=['city', 'state'])
cleaned_sellers = cleaned_sellers.drop(columns=['city', 'state'])

#print(cleaned_customers)
#print(cleaned_sellers)

#change cleaned_geolocation state name to state_code for SQL
cleaned_geolocation = cleaned_geolocation.rename(columns={'state': 'state_code'})
print(cleaned_geolocation)


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



# FOR LATER ADD ANALYTICAL FUNCITONS TO CREATE NEW CSVs