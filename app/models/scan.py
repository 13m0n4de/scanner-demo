from pydantic import BaseModel


class ScanCreate(BaseModel):
    target: str
