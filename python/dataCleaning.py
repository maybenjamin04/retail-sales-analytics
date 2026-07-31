import pandas as pd


# THINGS TO DO

# merge customers with geolocation
# 
# merge sellers with geolocation
#
# merge products with product translation



customers = pd.read_csv('../data/raw/olist_customers_dataset.csv')
geolocation = pd.read_csv('../data/raw/olist_geolocation_dataset.csv')
orders = pd.read_csv('../data/raw/olist_order_items_dataset.csv')
payments = pd.read_csv('../data/raw/olist_geolocation_dataset.csv')
geolocation = pd.read_csv('../data/raw/olist_geolocation_dataset.csv')
sellers = pd.read_csv('../data/raw/olist_sellers_dataset.csv')


print(customers.info())
print(len(customers))
#print(geolocation.info())
#print(sellers.info())