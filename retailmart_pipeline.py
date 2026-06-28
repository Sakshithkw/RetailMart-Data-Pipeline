# ============================================================
# RetailMart Pvt. Ltd. — Junior Data Engineer Assignment
# ============================================================

import pandas as pd
import numpy as np
import sqlite3
import os

# ============================================================
# STEP 0: Create Sample CSV Files (10-15 rows each)
# ============================================================

# --- products.csv - 12 rows ---
products_data = pd.DataFrame({
    'product_id':   [201,202,203,204,205,206,207,208,209,210,211,212],
    'product_name': ['Basmati Rice 5kg','Sunflower Oil 1L','Whole Wheat Atta 10kg','Sugar 1kg',
                     'Tata Salt 1kg','Aashirvaad Atta 5kg','Fortune Oil 2L','Amul Butter 500g',
                     'Maggi Noodles 70g','Bournvita 500g','Lays Chips 26g','Parle-G Biscuit 800g'],
    'category':     ['Grains','Oils','Grains','Sweeteners','Spices','Grains','Oils',
                     'Dairy','Snacks','Beverages','Snacks','Snacks'],
    'price':        [250.0,120.0,180.0,45.0,25.0,220.0,210.0,240.0,14.0,320.0,20.0,65.0]
})

# --- stores.csv - 10 rows ---
stores_data = pd.DataFrame({
    'store_id':   [101,102,103,104,105,106,107,108,109,110],
    'store_name': ['RetailMart Jaipur Central','RetailMart Mumbai West','RetailMart Delhi North',
                   'RetailMart Bengaluru South','RetailMart Chennai East','RetailMart Pune Main',
                   'RetailMart Hyderabad West','RetailMart Kolkata North','RetailMart Ahmedabad',
                   'RetailMart Surat'],
    'city':       ['Jaipur','Mumbai','Delhi','Bengaluru','Chennai','Pune','Hyderabad','Kolkata','Ahmedabad','Surat'],
    'region':     ['North','West','North','South','South','West','South','East','West','West']
})

# --- sales_data.csv - 15 rows + 2 duplicates, with missing values ---
sales_data = pd.DataFrame({
    'sale_id':    [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15, 3,7],
    'store_id':   [101,102,101,103,102,104,103,101,104,102,103,104,105,106,107, 101,103],
    'product_id': [201,202,203,201,204,202,203,204,201,203,202,204,205,206,207, 203,203],
    'quantity':   [2,None,5,3,None,4,2,6,1,3,None,5,4,2,3, 5,2],
    'sale_date':  ['2024-06-01','2024-06-01','2024-06-02','2024-06-02','2024-06-03',
                   '2024-06-03','2024-06-04','2024-06-04','2024-06-05','2024-06-05',
                   '2024-06-06','2024-06-06','2024-06-07','2024-06-07','2024-06-08',
                   '2024-06-02','2024-06-04'],
    'amount':     [500.0,300.0,None,750.0,200.0,480.0,None,960.0,
                   250.0,450.0,360.0,700.0,100.0,440.0,630.0, None,None]
})

products_data.to_csv('products.csv', index=False)
stores_data.to_csv('stores.csv', index=False)
sales_data.to_csv('sales_data.csv', index=False)

print("=" * 60)
print("CSV FILES CREATED SUCCESSFULLY")
print(f"  sales_data : {len(sales_data)} rows (includes 2 duplicates + missing values)")
print(f"  products   : {len(products_data)} rows")
print(f"  stores     : {len(stores_data)} rows")
print("=" * 60)


# ============================================================
# TASK 1: Data Ingestion
# ============================================================
print("\n" + "=" * 60)
print("TASK 1: DATA INGESTION")
print("=" * 60)

sales = pd.read_csv('sales_data.csv')
products = pd.read_csv('products.csv')
stores = pd.read_csv('stores.csv')

print("\n--- sales_data.csv ---")
print("Shape:", sales.shape)
print(sales.head())

print("\n--- products.csv ---")
print("Shape:", products.shape)
print(products.head())

print("\n--- stores.csv ---")
print("Shape:", stores.shape)
print(stores.head())

print("\n--- Missing Values Summary ---")
print("\nsales_data missing values:")
print(sales.isnull().sum())
print("\nproducts missing values:")
print(products.isnull().sum())
print("\nstores missing values:")
print(stores.isnull().sum())


# ============================================================
# TASK 2: Data Cleaning
# ============================================================
print("\n" + "=" * 60)
print("TASK 2: DATA CLEANING")
print("=" * 60)

before = len(sales)
sales = sales.drop_duplicates()
after = len(sales)
print(f"\nDuplicates found and removed: {before - after}")
print(f"Rows after removing duplicates: {after}")

sales['quantity'] = sales['quantity'].fillna(0)
sales = sales.dropna(subset=['amount'])
print(f"\nAfter filling quantity nulls and dropping null amount rows:")
print("Cleaned DataFrame shape:", sales.shape)
print(sales)

sales['sale_date'] = pd.to_datetime(sales['sale_date'])
sales['amount'] = sales['amount'].astype(float)
print("\nData types after conversion:")
print(sales.dtypes)


# ============================================================
# TASK 3: Data Transformation
# ============================================================
print("\n" + "=" * 60)
print("TASK 3: DATA TRANSFORMATION")
print("=" * 60)

final_df = sales.merge(stores, on='store_id', how='left') \
                .merge(products, on='product_id', how='left')

print("\nFinal Merged DataFrame:")
print(final_df.to_string())

final_df['total_revenue'] = final_df['quantity'] * final_df['price']

revenue_array = final_df['total_revenue'].to_numpy()
print(f"\nTotal Revenue Stats (NumPy):")
print(f"  Mean : Rs.{np.mean(revenue_array):.2f}")
print(f"  Max  : Rs.{np.max(revenue_array):.2f}")
print(f"  Min  : Rs.{np.min(revenue_array):.2f}")

city_revenue = final_df.groupby('city')['total_revenue'].sum().reset_index()
city_revenue = city_revenue.sort_values('total_revenue', ascending=False)
print("\nTotal Revenue per City:")
print(city_revenue.to_string(index=False))


# ============================================================
# TASK 4: Data Loading (SQL)
# ============================================================
print("\n" + "=" * 60)
print("TASK 4: DATA LOADING TO SQLite")
print("=" * 60)

conn = sqlite3.connect('retailmart.db')
final_df.to_sql('retail_sales', conn, if_exists='replace', index=False)
print("\nData loaded into SQLite table 'retail_sales' successfully.")

query_top3 = """
SELECT product_name, SUM(quantity) AS total_quantity_sold
FROM retail_sales
GROUP BY product_name
ORDER BY total_quantity_sold DESC
LIMIT 3;
"""
print("\nTop 3 Best-Selling Products by Quantity:")
print(pd.read_sql_query(query_top3, conn).to_string(index=False))


# ============================================================
# TASK 5: Reporting & Insights
# ============================================================
print("\n" + "=" * 60)
print("TASK 5: REPORTING & INSIGHTS")
print("=" * 60)

query_store_day = """
SELECT store_name, sale_date, SUM(total_revenue) AS daily_revenue
FROM retail_sales
GROUP BY store_name, sale_date
ORDER BY store_name, sale_date;
"""
print("\nTotal Revenue per Store per Day:")
print(pd.read_sql_query(query_store_day, conn).to_string(index=False))

total_transactions = len(final_df)
total_revenue = final_df['total_revenue'].sum()
top_city = city_revenue.iloc[0]['city']
top_product = final_df.groupby('product_name')['quantity'].sum().idxmax()

print("\n--- Summary Report ---")
print(f"  Total Transactions : {total_transactions}")
print(f"  Total Revenue      : Rs.{total_revenue:.2f}")
print(f"  Top Selling City   : {top_city}")
print(f"  Top Selling Product: {top_product}")

conn.close()


# ============================================================
# TASK 6: Pipeline & Error Handling
# ============================================================
print("\n" + "=" * 60)
print("TASK 6: PIPELINE FUNCTION WITH ERROR HANDLING")
print("=" * 60)

def run_pipeline():
    try:
        print("\n[1] Loading CSV files...")
        if not os.path.exists('sales_data.csv'):
            raise FileNotFoundError("sales_data.csv not found!")
        if not os.path.exists('products.csv'):
            raise FileNotFoundError("products.csv not found!")
        if not os.path.exists('stores.csv'):
            raise FileNotFoundError("stores.csv not found!")

        sales = pd.read_csv('sales_data.csv')
        products = pd.read_csv('products.csv')
        stores = pd.read_csv('stores.csv')
        print("    Files loaded successfully.")

        print("[2] Cleaning data...")
        sales = sales.drop_duplicates()
        sales['quantity'] = sales['quantity'].fillna(0)
        sales = sales.dropna(subset=['amount'])
        sales['sale_date'] = pd.to_datetime(sales['sale_date'])
        sales['amount'] = sales['amount'].astype(float)
        print("    Data cleaned successfully.")

        print("[3] Transforming data...")
        merged = sales.merge(stores, on='store_id', how='left') \
                      .merge(products, on='product_id', how='left')
        merged['total_revenue'] = merged['quantity'] * merged['price']
        print("    Data transformed successfully.")

        print("[4] Loading to SQLite database...")
        conn = sqlite3.connect('retailmart.db')
        merged.to_sql('retail_sales', conn, if_exists='replace', index=False)
        conn.close()
        print("    Data loaded to database successfully.")

        print("\n Pipeline completed successfully!")

    except FileNotFoundError as e:
        print(f"\n ERROR: {e}")
        print("   Please make sure all CSV files are present in the working directory.")
    except Exception as e:
        print(f"\n Unexpected error: {e}")

run_pipeline()