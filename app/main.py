from fastapi import FastAPI
from gpt_bigquery.tags import tags_metadata
from gpt_bigquery.routers import gpt_router

app = FastAPI(title="ChatGPT BigQuery API",
              description="API for connecting ChatGPT to BigQuery",
              version="1",
              openapi_tags=tags_metadata)

app.include_router(gpt_router)