#loading the cleaned data in postgreSQL database
import pandas as pd
import os
import subprocess

from sqlalchemy import create_engine


def validate_data_load(df1,df2,key):
    df1_sorted = df1.sort_values(by=key).reset_index(drop=True)
    df2_sorted = df2.sort_values(by=key).reset_index(drop=True)
    print(df1_sorted.compare(df2_sorted))
    assert df1_sorted.equals(df2_sorted)

# read .env variables
with open("../.env") as f:
    for line in f:
        # Skip empty lines or comments
        if line.strip() and not line.startswith("#"):
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

postgres_url = os.environ.get("DATABASE_URL")

engine = create_engine(postgres_url)

customers = pd.read_csv('../data/processed/cleaned/customers.csv',
                        dtype={
                            'id': str,
                            'unique_id':str,
                            'zip_code_prefix':str
                        })
geolocation = pd.read_csv('../data/processed/cleaned/geolocation.csv',
                        dtype={
                            'zip_code_prefix': str,
                            'lat': 'float64',
                            'lng': 'float64',
                            'city': str,
                            'state_code': str
                        })
order_items = pd.read_csv('../data/processed/cleaned/order_items.csv',
                        dtype={
                            'order_id': str,
                            'order_item_id': int,
                            'product_id': str,
                            'seller_id': str,
                            'price': 'float64',
                            'freight_value': 'float64'
                        },
                        parse_dates=['shipping_limit_date'])
payments = pd.read_csv('../data/processed/cleaned/payments.csv',
                        dtype={
                            'order_id': str,
                            'sequential': int,
                            'payment_type': str,
                            'installments': int,
                            'amount': 'float64'
                        })
reviews = pd.read_csv('../data/processed/cleaned/reviews.csv',
                        dtype={
                            "id": str,
                            "order_id": str,
                            "score": int,
                            "comment_title": str,
                            "comment_message": str,
                        },
                        parse_dates=['creation_date', 'answer_timestamp'])
orders = pd.read_csv('../data/processed/cleaned/orders.csv', 
                        dtype={
                            "id": str,
                            "customer_id": str,
                            "status": str,
                        },
                        parse_dates=["purchase_timestamp","approved_at","delivered_carrier_date","delivered_customer_date","estimated_delivery_date"])
products = pd.read_csv('../data/processed/cleaned/products.csv', 
                       dtype={
                           "id": str,
                           "category_name": str,
                           "name_length": int,
                           "description_length": int,
                           "product_photos_qty": int,
                           "product_weight_g": int,
                           "product_length_cm": int,
                           "product_height_cm": int,
                           "product_width_cm": int
                       })
sellers = pd.read_csv('../data/processed/cleaned/sellers.csv',
                        dtype={
                            'id': str,
                            'zip_code_prefix':str
                        })

load_order = {
    'geolocation': geolocation,
    'customers': customers,
    'sellers': sellers,
    'products': products,
    'orders': orders,
    'order_items': order_items,
    'payments': payments,
    'reviews': reviews,   
}

primary_keys = {
    'geolocation': ['zip_code_prefix'],
    'customers': ['id'],
    'sellers': ['id'],
    'products': ['id'],
    'orders': ['id'],
    'order_items': ['order_id', 'order_item_id'],
    'payments': ['order_id', 'sequential'],
    'reviews': ['id', 'order_id'],   
}

subprocess.run(
    ['psql', '-U', 'data_analyst', '-d', 'olist', '-f', '../sql/create_tables.sql'],
    check=True
)

print('\n')

for table, df in load_order.items():
    df.to_sql(
        table, 
        con=engine, 
        if_exists="append", 
        index=False
    )

    sql_df = pd.read_sql(f'SELECT * FROM {table}', con=engine)
    print(f'validating {table}')
    validate_data_load(df, sql_df, primary_keys[table])
    print(f'{table} validated')
    print()

print('\nALL DATA VALIDATED AND NO ERRORS')