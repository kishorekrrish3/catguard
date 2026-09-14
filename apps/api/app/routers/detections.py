from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.models.detection import Detection
from app.core.security import get_current_active_user, require_roles
from app.schemas.detection import DetectionResponse, DetectionFeedback, DetectionAccuracy, DetectionTimelinePoint
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/detections", tags=["Detections"])


@router.get("/zone/{zone_id}", response_model=PaginatedResponse[DetectionResponse])
async def list_detections(
    zone_id: UUID,
    detection_type: Optional[str] = None,
    severity: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(Detection).where(Detection.zone_id == zone_id)
    if detection_type:
        query = query.where(Detection.detection_type == detection_type)
    if severity:
        query = query.where(Detection.severity == severity)
    if start:
        query = query.where(Detection.timestamp >= start)
    if end:
        query = query.where(Detection.timestamp <= end)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.order_by(desc(Detection.timestamp)).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=result.scalars().all(), total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.get("/timeline/{zone_id}", response_model=List[DetectionTimelinePoint])
async def get_detection_timeline(
    zone_id: UUID,
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    start = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Detection).where(Detection.zone_id == zone_id, Detection.timestamp >= start).order_by(Detection.timestamp)
    )
    detections = result.scalars().all()
    timeline: dict = {}
    for d in detections:
        day = d.timestamp.strftime("%Y-%m-%d")
        if day not in timeline:
            timeline[day] = {"date": day, "count": 0, "by_type": {}}
        timeline[day]["count"] += 1
        det_type = d.detection_type.value
        timeline[day]["by_type"][det_type] = timeline[day]["by_type"].get(det_type, 0) + 1
    return list(timeline.values())


@router.post("/feedback")
async def submit_feedback(
    feedback: DetectionFeedback,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("forest_manager", "field_officer", "data_analyst", "administrator")),
):
    result = await db.execute(select(Detection).where(Detection.id == feedback.detection_id))
    detection = result.scalar_one_or_none()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    detection.verified = feedback.verified
    detection.verified_by = current_user.id
    if feedback.notes:
        detection.notes = feedback.notes
    await db.commit()
    return {"message": "Feedback submitted"}


@router.get("/accuracy", response_model=DetectionAccuracy)
async def get_accuracy_metrics(
    zone_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(Detection)
    if zone_id:
        query = query.where(Detection.zone_id == zone_id)
    result = await db.execute(query)
    detections = result.scalars().all()
    total = len(detections)
    verified = sum(1 for d in detections if d.verified)
    precision = verified / total if total > 0 else None
    return DetectionAccuracy(
        zone_id=zone_id, total_detections=total, verified_count=verified,
        false_positive_count=0, precision=precision, recall=None, f1_score=None, by_type=[],
    )


@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(detection_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    result = await db.execute(select(Detection).where(Detection.id == detection_id))
    detection = result.scalar_one_or_none()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection
