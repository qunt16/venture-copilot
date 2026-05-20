from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    return {"success": True, "data": {"status": "ok", "version": "0.1.0", "iteration": 1}, "message": None}
