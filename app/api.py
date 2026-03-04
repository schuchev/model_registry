from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_conn
from app.s3 import generate_upload_url
from app.services import promote_to_production, log_audit

router = APIRouter()

class ModelCreate(BaseModel):
    name: str
    description: str = ""

class VersionCreate(BaseModel):
    model_id: int
    version_number: int
    created_by: int

class PromoteRequest(BaseModel):
    model_id: int
    user_id: int

@router.post("/models")
async def create_model(data: ModelCreate):
    conn = await get_conn()
    model_id = await conn.fetchval(
        "INSERT INTO models(name, description) VALUES($1,$2) RETURNING id",
        data.name, data.description
    )
    await log_audit("model", model_id, "create", user_id=1)
    await conn.close()
    return {"id": model_id, "name": data.name, "description": data.description}

@router.post("/versions")
async def create_version(data: VersionCreate):
    conn = await get_conn()
    version_id = await conn.fetchval(
        "INSERT INTO model_versions(model_id, version_number, created_by) VALUES($1,$2,$3) RETURNING id",
        data.model_id, data.version_number, data.created_by
    )
    upload_url = generate_upload_url(f"models/{version_id}")
    await log_audit("version", version_id, "create", user_id=data.created_by)
    await conn.close()
    return {"id": version_id, "upload_url": upload_url}

@router.patch("/versions/{version_id}/promote")
async def promote_version(version_id: int, req: PromoteRequest):
    await promote_to_production(version_id, req.model_id, req.user_id)
    return {"version_id": version_id, "stage": "production"}