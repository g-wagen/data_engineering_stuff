import pandas as pd
import database_connection
import cleanup_da_jobs


# Connect to datalake
datalake_connection = database_connection.connect_to_datalake()

# Grab the whole table
raw_data = pd.read_sql('SELECT * FROM da_jobs', datalake_connection)

# Disconnect from the datalake
datalake_connection.close()


# The big data cleanup part comes here
clean_data = cleanup_da_jobs.cleanup(raw_data)


# Connect to the datawarehouse
datawarehouse_connection = database_connection.connect_to_datawarehouse()

# Load the data into the datawarehouse
clean_data.to_sql('da_jobs', datawarehouse_connection, if_exists='append')

# Close the database connection
datawarehouse_connection.close()
