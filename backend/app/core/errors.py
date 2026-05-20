from fastapi import HTTPException


def not_found(resource: str = "Resource") -> HTTPException:
    return HTTPException(status_code=404, detail=f"{resource} not found")


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)