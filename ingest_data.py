import pandas as pd
from time import time
from sqlalchemy import create_engine
import argparse
import os


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    csv_name = "output.csv"
    
    os.system(f"wget {url} -O {csv_name}")

    # download the csv
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}", pool_pre_ping=True)

    df_iter = pd.read_csv(url, iterator = True, chunksize = 100000)
    #df_iter = pd.read_csv(csv_name, chunksize=100000, iterator=True, low_memory=False, dtype={6: str})
    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name = table_name, con = engine, if_exists='replace')
    df.to_sql(name = table_name, con = engine, if_exists='append')

    while True:
        try:
            t_start = time()

            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime) 

            df.to_sql(name=table_name, con=engine, if_exists="append")

            t_end = time()

            print("Inserted another chunk..., took %.3f second" % (t_end - t_start))

        except StopIteration:
            print("All chunks processed.")
            break  # Exit the loop when no more data is available


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Ingest CSV data to Postgres")

    # user
    # password
    # host
    # port
    # database name
    # table name
    # url of the csv

    parser.add_argument('--user', help="user name for postgres")
    parser.add_argument('--password', help="password for postgres")
    parser.add_argument('--host', help="host for postgres")
    parser.add_argument('--port', help="port for postgres")
    parser.add_argument('--db', help="database name for postgres")
    parser.add_argument('--table_name', help="name of the table where we will write the results to")
    parser.add_argument('--url', help="url of the CSV")

    args = parser.parse_args()

    main(args)