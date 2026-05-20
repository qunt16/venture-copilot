from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    message: Optional[str] = None


def ok(data: Any = None, message: Optional[str] = None) -> dict:
    return ApiResponse(success=True, data=data, message=message).model_dump()


def err(message: str, data: Any = None) -> dict:
    return ApiResponse(success=False, data=data, message=message).model_dump()