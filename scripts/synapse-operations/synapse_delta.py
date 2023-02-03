
## These commands can be manually inputted into a Synapse notebook
# The goal is to convert the parquet files in `listings` into delta files and save them in `customer-reviews`

# Load the dataframe
get_ipython().run_cell_magic('pyspark', '', "df =
                             spark.read.load('abfss://reviews@<storage
                                             account>.dfs.core.windows.net/listings/*.parquet', format='parquet', header=True)\r\ndisplay(df.limit(10))\n")

# Ensure the count is accurate
print(df.count())
assert df.count() == 10000

# Create a delta table from the parquet files
# delta_table_path = "./sample/my-directory/"
df.write.format("delta").save('abfss://reviews@<storage account>.dfs.core.windows.net/customer-reviews/')

## OTHER SAMPLE COMMANDS
# #!/usr/bin/env python
# # coding: utf-8
#
# # ## Notebook 1
# # 
# # 
# # 
#
# # In[2]:
#
#
# get_ipython().run_cell_magic('pyspark', '', "df = spark.read.load('abfss://files@datalakef0djesu.dfs.core.windows.net/products/products.csv', format='csv'\r\n## If\u202fheader\u202fexists\u202funcomment\u202fline\u202fbelow\r\n, header=True\r\n)\r\ndisplay(df.limit(10))\n")
#
#
# # In[3]:
#
#
# # Create a delta table
# delta_table_path = "/delta/products-delta"
# df.write.format("delta").save(delta_table_path)
#
#
# # In[4]:
#
#
# from delta.tables import *
# from pyspark.sql.functions import *
#
# # Create a deltaTable object
# deltaTable = DeltaTable.forPath(spark, delta_table_path)
#
# # Update the table (reduce price of product 771 by 10%)
# deltaTable.update(
#      condition = "ProductID == 771",
#      set = { "ListPrice": "ListPrice * 0.9" })
#
# # View the updated data as a dataframe
# deltaTable.toDF().show(10)
#
#
# # In[5]:
#
#
# new_df = spark.read.format("delta").load(delta_table_path)
# new_df.show(10)
#
#
# # In[7]:
#
#
# # Time travel
# new_df = spark.read.format("delta").option("versionAsOf", 0).load(delta_table_path)
# new_df.show(10)
#
#
# # In[8]:
#
#
# deltaTable.history(10).show(20, False, True)
#
#
# # In[10]:
#
#
# # Define external tables
# spark.sql("CREATE DATABASE AdventureWorks")
# spark.sql("CREATE TABLE AdventureWorks.ProductsExternal USING DELTA LOCATION '{0}'".format(delta_table_path))
# spark.sql("DESCRIBE EXTENDED AdventureWorks.ProductsExternal").show(truncate=False)
#
#
# # In[11]:
#
#
# get_ipython().run_cell_magic('sql', '', '\nUSE AdventureWorks;\n\nSELECT * FROM ProductsExternal;\n')
#
#
# # In[12]:
#
#
# df.write.format("delta").saveAsTable("AdventureWorks.ProductsManaged")
# spark.sql("DESCRIBE EXTENDED AdventureWorks.ProductsManaged").show(truncate=False)
#
#
# # In[13]:
#
#
# get_ipython().run_cell_magic('sql', '', '\nUSE AdventureWorks;\n\nSELECT * FROM ProductsManaged;\n')
#
#
# # In[14]:
#
#
# get_ipython().run_cell_magic('sql', '', '\nUSE AdventureWorks;\n\nSHOW TABLES;\n')
#
#
# # In[15]:
#
#
# get_ipython().run_cell_magic('sql', '', '\nUSE AdventureWorks;\n\nDROP TABLE IF EXISTS ProductsExternal;\nDROP TABLE IF EXISTS ProductsManaged;\n')
#
#
# # In[16]:
#
#
# get_ipython().run_cell_magic('sql', '', "\nUSE AdventureWorks;\n\nCREATE TABLE Products\nUSING DELTA\nLOCATION '/delta/products-delta';\n")
#
#
# # In[17]:
#
#
# get_ipython().run_cell_magic('sql', '', '\nUSE AdventureWorks;\n\nSELECT * FROM Products;\n')
#
#
# # In[18]:
#
#
# from notebookutils import mssparkutils
# from pyspark.sql.types import *
# from pyspark.sql.functions import *
#
# # Create a folder
# inputPath = '/data/'
# mssparkutils.fs.mkdirs(inputPath)
#
# # Create a stream that reads data from the folder, using a JSON schema
# jsonSchema = StructType([
# StructField("device", StringType(), False),
# StructField("status", StringType(), False)
# ])
# iotstream = spark.readStream.schema(jsonSchema).option("maxFilesPerTrigger", 1).json(inputPath)
#
# # Write some event data to the folder
# device_data = '''{"device":"Dev1","status":"ok"}
# {"device":"Dev1","status":"ok"}
# {"device":"Dev1","status":"ok"}
# {"device":"Dev2","status":"error"}
# {"device":"Dev1","status":"ok"}
# {"device":"Dev1","status":"error"}
# {"device":"Dev2","status":"ok"}
# {"device":"Dev2","status":"error"}
# {"device":"Dev1","status":"ok"}'''
# mssparkutils.fs.put(inputPath + "data.txt", device_data, True)
# print("Source stream created...")
#
#
# # In[19]:
#
#
# # Write the stream to a delta table
# delta_stream_table_path = '/delta/iotdevicedata'
# checkpointpath = '/delta/checkpoint'
# deltastream = iotstream.writeStream.format("delta").option("checkpointLocation", checkpointpath).start(delta_stream_table_path)
# print("Streaming to delta sink...")
#
#
# # In[20]:
#
#
# # Read the data in delta format into a dataframe
# df = spark.read.format("delta").load(delta_stream_table_path)
# display(df)
#
#
# # In[21]:
#
#
# # create a catalog table based on the streaming sink
# spark.sql("CREATE TABLE IotDeviceData USING DELTA LOCATION '{0}'".format(delta_stream_table_path))
#
#
# # In[22]:
#
#
# get_ipython().run_cell_magic('sql', '', '\nSELECT * FROM IotDeviceData;\n')
#
#
# # In[23]:
#
#
# # Add more data to the source stream
# more_data = '''{"device":"Dev1","status":"ok"}
# {"device":"Dev1","status":"ok"}
# {"device":"Dev1","status":"ok"}
# {"device":"Dev1","status":"ok"}
# {"device":"Dev1","status":"error"}
# {"device":"Dev2","status":"error"}
# {"device":"Dev1","status":"ok"}'''
#
# mssparkutils.fs.put(inputPath + "more-data.txt", more_data, True)
#
#
# # In[24]:
#
#
# get_ipython().run_cell_magic('sql', '', '\nSELECT * FROM IotDeviceData;\n')
#
#
# # In[25]:
#
#
# deltastream.stop()
#
#
# # In[ ]:
#
#
# ## Query using serverless pool
# -- This is auto-generated code
# SELECT
#     TOP 100 *
# FROM
#     OPENROWSET(
#         BULK 'https://datalakexxxxxxx.dfs.core.windows.net/files/delta/products-delta/',
#         FORMAT = 'DELTA'
#     ) AS [result]
#
