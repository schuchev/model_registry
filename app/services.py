from app.db import get_conn

async def log_audit(entity_type: str, entity_id: int, action: str, user_id: int):
    conn = await get_conn()
    await conn.execute(
        "INSERT INTO audit_logs(entity_type, entity_id, action, performed_by) VALUES($1,$2,$3,$4)",
        entity_type, entity_id, action, user_id
    )
    await conn.close()

async def promote_to_production(version_id: int, model_id: int, user_id: int):
    conn = await get_conn()
    async with conn.transaction():
        await conn.execute("""
            UPDATE model_versions
            SET stage='archived'
            WHERE model_id=$1 AND stage='production'
        """, model_id)
        await conn.execute("""
            UPDATE model_versions
            SET stage='production'
            WHERE id=$1
        """, version_id)
        await log_audit("version", version_id, "promote_to_production", user_id)
    await conn.close()