from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from uuid import UUID
from datetime import date
import uuid as uuid_module
import json

from app.database import get_db
from app.models.imagery import SatelliteImagery, ProcessingStatus
from app.core.security import get_current_active_user, require_roles
from app.core.storage import upload_file
from app.core.redis_client import set_cache, get_cache
from app.ml.detection_engine import detection_engine
from app.schemas.imagery import ImageryCreate, ImageryResponse, ImageryProcessRequest
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/imagery", tags=["Imagery"])


@router.get("/history", response_model=PaginatedResponse[ImageryResponse])
async def get_imagery_history(
    zone_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(SatelliteImagery)
    if zone_id:
        query = query.where(SatelliteImagery.zone_id == zone_id)
    if start_date:
        query = query.where(SatelliteImagery.acquisition_date >= start_date)
    if end_date:
        query = query.where(SatelliteImagery.acquisition_date <= end_date)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.order_by(desc(SatelliteImagery.acquisition_date)).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=result.scalars().all(), total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.post("/process")
async def trigger_processing(
    data: ImageryProcessRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "data_analyst", "administrator")),
):
    result = await db.execute(select(SatelliteImagery).where(SatelliteImagery.id == data.imagery_id))
    imagery = result.scalar_one_or_none()
    if not imagery:
        raise HTTPException(status_code=404, detail="Imagery record not found")
    job_id = str(uuid_module.uuid4())
    imagery.processing_status = ProcessingStatus.processing
    await db.commit()

    # Simulate processing with mock NDVI values
    ndvi_data = detection_engine.generate_mock_ndvi(str(imagery.zone_id), str(imagery.acquisition_date))
    imagery.ndvi_mean = ndvi_data["ndvi_mean"]
    imagery.ndvi_min = ndvi_data["ndvi_min"]
    imagery.ndvi_max = ndvi_data["ndvi_max"]
    imagery.savi_mean = ndvi_data["savi_mean"]
    imagery.processing_status = ProcessingStatus.completed
    await db.commit()

    await set_cache(f"job:{job_id}", {"status": "completed", "imagery_id": str(data.imagery_id)})
    return {"job_id": job_id, "status": "completed"}


@router.get("/status/{job_id}")
async def get_job_status(job_id: str, _=Depends(get_current_active_user)):
    cached = await get_cache(f"job:{job_id}")
    if not cached:
        return {"job_id": job_id, "status": "not_found"}
    return cached


@router.get("/tiles/{z}/{x}/{y}")
async def get_map_tile(z: int, x: int, y: int):
    # In production: proxy to MinIO/S3 tile storage or tile server
    return {"message": f"Tile z={z} x={x} y={y} - proxy to tile server in production"}


@router.post("/upload")
async def upload_imagery(
    zone_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "administrator")),
):
    content = await file.read()
    key = f"imagery/{zone_id}/{uuid_module.uuid4()}/{file.filename}"
    url = upload_file(content, key, file.content_type or "image/tiff")
    imagery = SatelliteImagery(
        zone_id=zone_id,
        acquisition_date=date.today(),
        path_url=url,
        source="drone",
    )
    db.add(imagery)
    await db.commit()
    await db.refresh(imagery)
    return {"message": "Uploaded", "imagery_id": str(imagery.id), "url": url}
