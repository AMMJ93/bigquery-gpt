from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from gpt_bigquery.data_models import TableInfo, DatasetInfo
from fastapi.security import APIKeyHeader
from google.cloud import secretmanager
import os

# Set API Key Header
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# Function to fetch the API key from GCP Secret Manager
def get_api_key_from_secret_manager(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/1"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

def validate_api_key(api_key: str = Depends(api_key_header)):
    API_KEY = get_api_key_from_secret_manager(os.getenv("API_PROJECT_ID"), os.getenv("API_SECRET_ID"))
    
    if api_key != API_KEY: # Simple check between secret and provided x-api-key
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )

gpt_router = APIRouter(tags=["GPT"])

@gpt_router.get("/")
async def index(api_key: str = Depends(validate_api_key)):
  return "Hello to ChatGPT BigQuery"

@gpt_router.get('/openapi.yaml')
async def serve_openapi_yaml():
    return FileResponse('/app/files/openapi.yaml', media_type='text/yaml')

@gpt_router.post("/get-table-schema")
async def get_table_schema(table_info: TableInfo, api_key: str = Depends(validate_api_key)):
    client = bigquery.Client(project=table_info.project)

    table_ref = f"{table_info.project}.{table_info.dataset_id}.{table_info.table_id}"

    try:
        table = client.get_table(table_ref)  # Make an API request.
    except NotFound:
        raise HTTPException(status_code=404, detail="Table not found")

    schema = [{"name": field.name, "type": field.field_type, "mode": field.mode} for field in table.schema]
    return {"schema": schema}

@gpt_router.post("/get-dataset")
async def get_dataset(dataset_info: DatasetInfo, api_key: str = Depends(validate_api_key)):
    client = bigquery.Client(project=dataset_info.project)

    dataset_ref = f"{dataset_info.project}.{dataset_info.dataset_id}"

    try:
        dataset = client.get_dataset(dataset_ref)  # Make an API request.
    except NotFound:
        raise HTTPException(status_code=404, detail="Dataset not found")

    tables = list(client.list_tables(dataset))
    
    return {"dataset_description": dataset.description, "dataset_labels": dataset.labels, "tables": tables}