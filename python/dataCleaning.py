import pandas as pd


# THINGS TO DO

# merge customers with geolocation
# 
# merge products with product translation

def load_raw_data(path):
    df = pd.read_csv(path)
    return df



customers = load_raw_data('../data/raw/olist_customers_dataset.csv')
geolocation = load_raw_data('../data/raw/olist_geolocation_dataset.csv')
sellers = load_raw_data('../data/raw/olist_sellers_dataset.csv')


print(customers.info())
print(len(customers))
#print(geolocation.info())
#print(sellers.info())