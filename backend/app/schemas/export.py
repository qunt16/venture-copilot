from pydantic import BaseModel


class ExportRequest(BaseModel):
    include_review: bool = False


class ExportResult(BaseModel):
    file_name: str
    download_url: str


class ExportFile(BaseModel):
    file_name: str
    download_url: str
    format: str
