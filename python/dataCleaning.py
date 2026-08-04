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







if __name__ == '__main__':
    #==================customers===================
    #inspect_dataframe(customers, 'customers')

    #no missing values so fair to put into clean csv
    cleaned_customers = customers.copy(deep=True)
    assert cleaned_customers['customer_id'].is_unique
    assert cleaned_customers['customer_id'].notna().all()

    cleaned_customers.columns = cleaned_customers.columns.str.removeprefix('customer_')
    inspect_dataframe(cleaned_customers, 'customers')




    #=================sellers======================
    #inspect_dataframe(sellers, 'sellers')
    cleaned_sellers = sellers.copy(deep=True)
    #cleaned_sellers['seller_zip_code_prefix'] = cleaned_sellers['seller_zip_code_prefix'].astype('str').fillna('').str.zfill(5)

    assert cleaned_sellers['seller_id'].is_unique
    assert cleaned_sellers['seller_id'].notna().all()

    cleaned_sellers.columns = cleaned_sellers.columns.str.removeprefix('seller_')
    #inspect_dataframe(cleaned_sellers, 'sellers')



    #==================geolocation==================
    # geolocation has many duplicates with slightly different lon and lats so just keep the first one 
    # because there is no data to put customer/seller to specific lon and lat but state and city should be same
    cleaned_geolocation = geolocation.copy(deep=True)
    cleaned_geolocation.columns = cleaned_geolocation.columns.str.removeprefix('geolocation_')

    # gets all different zips between customer and geolocation
    customer_zips_not_in_geo = cleaned_customers[~cleaned_customers['zip_code_prefix'].isin(cleaned_geolocation['zip_code_prefix'])]
    customer_zips_not_in_geo = customer_zips_not_in_geo[['zip_code_prefix', 'city', 'state']]
    customer_zips_not_in_geo.insert(1, 'lat', pd.NA)
    customer_zips_not_in_geo.insert(2, 'lng', pd.NA)

    #gets all different zips between seller and geolocation
    seller_zips_not_in_geo = cleaned_sellers[~cleaned_sellers['zip_code_prefix'].isin(cleaned_geolocation['zip_code_prefix'])]
    seller_zips_not_in_geo = seller_zips_not_in_geo[['zip_code_prefix', 'city', 'state']]
    seller_zips_not_in_geo.insert(1, 'lat', pd.NA)
    seller_zips_not_in_geo.insert(2, 'lng', pd.NA)

    #adds all known zips into geolocation
    cleaned_geolocation = pd.concat([cleaned_geolocation, customer_zips_not_in_geo, seller_zips_not_in_geo])

    #clear duplicates
    cleaned_geolocation = cleaned_geolocation.drop_duplicates(subset='zip_code_prefix', keep='first')

    #make sure zipcode keeps leading zeros
    cleaned_geolocation['zip_code_prefix'] = cleaned_geolocation['zip_code_prefix'].astype('str').fillna('').str.zfill(5)
    cleaned_customers['zip_code_prefix'] = cleaned_customers['zip_code_prefix'].astype('str').fillna('').str.zfill(5)
    cleaned_sellers['zip_code_prefix'] = cleaned_sellers['zip_code_prefix'].astype('str').fillna('').str.zfill(5)

    assert cleaned_geolocation['zip_code_prefix'].is_unique
    assert cleaned_geolocation['zip_code_prefix'].notna().all()

    assert cleaned_customers['zip_code_prefix'].isin(cleaned_geolocation['zip_code_prefix']).all()
    assert cleaned_sellers['zip_code_prefix'].isin(cleaned_geolocation['zip_code_prefix']).all()

    cleaned_customers = cleaned_customers.drop(columns=['city', 'state'])
    cleaned_sellers = cleaned_sellers.drop(columns=['city', 'state'])
    cleaned_geolocation = cleaned_geolocation.rename(columns={'state': 'state_code'})

    #inspect_dataframe(cleaned_geolocation, 'geolocation')
    #inspect_dataframe(cleaned_customers, 'customers')
    #inspect_dataframe(cleaned_sellers, 'sellers')




    #=====order items======
    #inspect_dataframe(order_items, 'order_items')
    cleaned_order_items = order_items.copy(deep=True)
    cleaned_order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'])

    # order_id + order_item_id are pk
    assert not cleaned_order_items.duplicated(subset=['order_id', 'order_item_id']).any()
    assert cleaned_order_items['order_id'].notna().all()
    assert cleaned_order_items['order_item_id'].notna().all()

    #inspect_dataframe(cleaned_order_items, 'order_items')






    #payments
    # unsure if payment 0.0 means free? for now clean 
    #inspect_dataframe(payments, 'payments')
    cleaned_payments = payments.copy(deep=True)

    assert not cleaned_payments.duplicated(subset=['order_id', 'payment_sequential']).any()
    assert cleaned_payments['order_id'].notna().all()
    assert cleaned_payments['payment_sequential'].notna().all()
    assert (cleaned_payments['payment_value'] >= 0.0).all()

    cleaned_payments.columns = [col.removeprefix('payment_') if col != 'payment_type' else col for col in cleaned_payments.columns]
    cleaned_payments = cleaned_payments.rename(columns={'value': 'amount'})
    #inspect_dataframe(cleaned_payments, 'payments')






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
    #inspect_dataframe(cleaned_reviews, 'reviews')






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

    #inspect_dataframe(cleaned_orders, 'orders')






    # products
    assert products['product_id'].is_unique
    assert products['product_id'].notna().all()

    #check if numbers are positive
    float_cols = products.select_dtypes(include=["float64"])
    if not float_cols.empty:
        assert products[float_cols > 0].all().all()

    #translation
    # merge translation and products so theres english translation for name
    cleaned_translated_products = pd.merge(products, translation, on='product_category_name', how='left')
    cleaned_translated_products.insert(2, 'product_category_name_english',cleaned_translated_products.pop('product_category_name_english'))
    cleaned_translated_products = cleaned_translated_products.rename(columns={'product_name_lenght': 'product_name_length', 'product_description_lenght': 'product_description_length'})

    #product name null to Unknown
    products_strings = cleaned_translated_products.select_dtypes(include=['object', 'string']).columns
    replace_str_dict = {col: 'Unknown' for col in products_strings}
    cleaned_translated_products = cleaned_translated_products.fillna(value=replace_str_dict)

    #nan values for 0 in float64 cols
    cleaned_translated_products = cleaned_translated_products.fillna(0)
    cleaned_translated_products["product_name_length"] = cleaned_translated_products["product_name_length"].astype(int)
    cleaned_translated_products["product_description_length"] = cleaned_translated_products["product_description_length"].astype(int)
    cleaned_translated_products["product_photos_qty"] = cleaned_translated_products["product_photos_qty"].astype(int)
    cleaned_translated_products["product_weight_g"] = cleaned_translated_products["product_weight_g"].astype(int)
    cleaned_translated_products["product_length_cm"] = cleaned_translated_products["product_length_cm"].astype(int)
    cleaned_translated_products["product_height_cm"] = cleaned_translated_products["product_height_cm"].astype(int)
    cleaned_translated_products["product_width_cm"] = cleaned_translated_products["product_width_cm"].astype(int)

    assert cleaned_translated_products['product_id'].is_unique
    assert cleaned_translated_products['product_id'].notna().all()

    cleaned_translated_products.columns = cleaned_translated_products.columns.str.removeprefix('product_')
    #inspect_dataframe(cleaned_translated_products, 'products')


    CLEANED_CSV = {
            'customers': cleaned_customers,
            'geolocation': cleaned_geolocation ,
            'order_items': cleaned_order_items.round(2),
            'payments': cleaned_payments.round(2),
            'reviews': cleaned_reviews,
            'orders': cleaned_orders,
            'products': cleaned_translated_products,
            'sellers': cleaned_sellers
        }


    # possible rewrite to have check on weather to append or to rewrite files 

    for filename, df in CLEANED_CSV.items():
        df.to_csv(f'../data/processed/cleaned/{filename}.csv', index=False)
        inspect_dataframe(df, filename)
