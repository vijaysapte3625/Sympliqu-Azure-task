import json
from azure.functions import HttpRequest, HttpResponse
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import logging

COSMOS_CONN = "*****;"
BLOB_CONN = "*****"
DB_NAME = "billingdb"
COL_NAME = "records"
ARCHIVE_CONTAINER = "billing-archive"

cosmos = CosmosClient.from_connection_string(COSMOS_CONN)
container = cosmos.get_database_client(DB_NAME).get_container_client(COL_NAME)
archive = BlobServiceClient.from_connection_string(BLOB_CONN).get_container_client(ARCHIVE_CONTAINER)

def main(req: HttpRequest) -> HttpResponse:
    record_id = req.route_params.get("id")
    pk = req.params.get("partitionKey")
    try:
        doc = container.read_item(record_id, partition_key=pk)
        return HttpResponse(json.dumps(doc), status_code=200, mimetype="application/json")
    except Exception:
        try:
            blob = archive.download_blob(f"{record_id}.json")
            doc = json.loads(blob.readall())
            return HttpResponse(json.dumps(doc), status_code=200, mimetype="application/json")
        except Exception as ex:
            logging.error(f"Not found: {record_id}")
            return HttpResponse("Not Found", status_code=404)
