from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.database import get_db
from app.models.community_report import CommunityReport, ReportStatus
from app.models.user import User
from app.core.security import get_current_active_user, require_roles
from app.schemas.community import CommunityReportCreate, CommunityReportResponse, LeaderboardEntry
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/community", tags=["Community"])


@router.post("/reports", response_model=CommunityReportResponse, status_code=201)
async def submit_report(
    data: CommunityReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    report = CommunityReport(
        zone_id=data.zone_id,
        reporter_id=None if data.is_anonymous else current_user.id,
        is_anonymous=data.is_anonymous,
        report_type=data.report_type,
        description=data.description,
        location=from_shape(Point(data.lng, data.lat), srid=4326),
        photo_urls=data.photo_urls,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/reports", response_model=PaginatedResponse[CommunityReportResponse])
async def list_reports(
    zone_id: Optional[UUID] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    query = select(CommunityReport)
    # Community reporters can only see their own reports
    if current_user.role.value == "community_reporter":
        query = query.where(CommunityReport.reporter_id == current_user.id)
    elif zone_id:
        query = query.where(CommunityReport.zone_id == zone_id)
    if status:
        query = query.where(CommunityReport.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.order_by(desc(CommunityReport.submitted_at)).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=result.scalars().all(), total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.get("/reports/{report_id}", response_model=CommunityReportResponse)
async def get_report_status(report_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    result = await db.execute(select(CommunityReport).where(CommunityReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/reports/{report_id}/status")
async def update_report_status(
    report_id: UUID,
    status: str = Query(...),
    resolution_notes: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("forest_manager", "field_officer", "administrator")),
):
    result = await db.execute(select(CommunityReport).where(CommunityReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = status
    if resolution_notes:
        report.resolution_notes = resolution_notes
    if status == "verified":
        report.verified_by = current_user.id
    await db.commit()
    return {"message": "Status updated", "status": status}


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    result = await db.execute(
        select(
            User.id,
            User.username,
            User.full_name,
            func.count(CommunityReport.id).label("total_reports"),
            func.sum(
                func.case((CommunityReport.status.in_(["verified", "resolved"]), 1), else_=0)
            ).label("verified_reports"),
        )
        .join(CommunityReport, CommunityReport.reporter_id == User.id, isouter=True)
        .group_by(User.id)
        .having(func.count(CommunityReport.id) > 0)
        .order_by(desc("total_reports"))
        .limit(limit)
    )
    rows = result.all()
    return [
        LeaderboardEntry(
            rank=i + 1,
            user_id=row.id,
            username=row.username,
            full_name=row.full_name,
            total_reports=row.total_reports or 0,
            verified_reports=int(row.verified_reports or 0),
            score=float((row.total_reports or 0) * 10 + (row.verified_reports or 0) * 5),
        )
        for i, row in enumerate(rows)
    ]


@router.get("/stats")
async def get_community_stats(db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    total = (await db.execute(select(func.count(CommunityReport.id)))).scalar()
    pending = (await db.execute(select(func.count(CommunityReport.id)).where(CommunityReport.status == "pending"))).scalar()
    resolved = (await db.execute(select(func.count(CommunityReport.id)).where(CommunityReport.status == "resolved"))).scalar()
    return {"total_reports": total, "pending": pending, "resolved": resolved, "resolution_rate": resolved / total if total else 0}
