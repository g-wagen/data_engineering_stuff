import pandas as pd
import database_connection


# Connect to the datalake
datalake_connection = database_connection.connect_to_datalake()

# Grab the data from somewhere and dataframe it
raw_data = pd.read_csv('DataAnalyst.csv')

# Load the data into the datalake
raw_data.to_sql('da_jobs', datalake_connection, if_exists='replace')

# Close the database connection
datalake_connection.close()