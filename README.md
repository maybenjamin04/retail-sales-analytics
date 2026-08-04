# Brazil E-commerce Data Analysis

## Dataset Used

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Installation

git clone https://github.com/maybenjamin04/retail-sales-analytics.git
cd retail-sales-analytics

## Usage

Download Dataset and move into data

cd python

python3 dataCleaning.py -> cleans data and stores into new csv files

python3 loadToPosgreSQL.py -> loads cleaned data into PostgreSQL database and validates data

cd sql

create_tables.sql -> holds structure for database and creates db tables

basic_qureies.sql -> basic queries used for debug and basic data analysis

analytical_queries -> used to create custom tables for tableau and used for data insights
