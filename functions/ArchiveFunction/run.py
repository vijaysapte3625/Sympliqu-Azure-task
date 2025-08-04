import datetime, json
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
import logging

COSMOS_CONN = "*****"
BLOB_CONN = "*****"
DB_NAME = "billingdb"
COL_NAME = "records"
ARCHIVE_CONTAINER = "billing-archive"

def main(mytimer):
    cosmos = CosmosClient.from_connection_string(COSMOS_CONN)
    container = cosmos.get_database_client(DB_NAME).get_container_client(COL_NAME)
    blob = BlobServiceClient.from_connection_string(BLOB_CONN).get_container_client(ARCHIVE_CONTAINER)
    blob.create_container_if_not_exists()
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()
    query = f"SELECT * FROM c WHERE c.timestamp < '{cutoff}'"
    for doc in container.query_items(query, enable_cross_partition_query=True):
        blob.upload_blob(f"{doc['id']}.json", data=json.dumps(doc), overwrite=True)
        container.delete_item(doc['id'], partition_key=doc['partitionKey'])
        logging.info(f"Archived {doc['id']}")
