from pydantic import BaseModel

class TableInfo(BaseModel):
    project: str
    dataset_id: str
    table_id: str
    
class DatasetInfo(BaseModel):
    project: str
    dataset_id: str