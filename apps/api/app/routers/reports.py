from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from datetime import datetime, date
import io
import csv
import json

from app.database import get_db
from app.models.alert import Alert
from app.models.detection import Detection
from app.models.sensor import Sensor
from app.core.security import get_current_active_user

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORT_TEMPLATES = [
    {"id": "vegetation_health", "name": "Vegetation Health Report", "description": "NDVI trends and coverage statistics", "formats": ["pdf", "csv"]},
    {"id": "threat_assessment", "name": "Threat Assessment Report", "description": "Detection events and severity analysis", "formats": ["pdf", "csv", "geojson"]},
    {"id": "sensor_network", "name": "Sensor Network Report", "description": "Sensor health, readings summary", "formats": ["csv", "pdf"]},
    {"id": "community_engagement", "name": "Community Engagement Report", "description": "Reports submitted and resolution rates", "formats": ["pdf", "csv"]},
    {"id": "compliance_audit", "name": "Compliance Audit Report", "description": "Full audit trail for compliance", "formats": ["pdf", "csv"]},
]


@router.get("/templates")
async def get_templates(_=Depends(get_current_active_user)):
    return REPORT_TEMPLATES


@router.get("/generate")
async def generate_report(
    template_id: str = Query(...),
    zone_id: Optional[UUID] = None,
    format: str = Query("csv", regex="^(csv|pdf|geojson)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        if template_id == "threat_assessment":
            writer.writerow(["ID", "Zone", "Type", "Confidence", "Severity", "Timestamp", "Verified"])
            query = select(Detection)
            if zone_id:
                query = query.where(Detection.zone_id == zone_id)
            result = await db.execute(query)
            for d in result.scalars().all():
                writer.writerow([str(d.id), str(d.zone_id), d.detection_type.value, d.confidence, d.severity.value, str(d.timestamp), d.verified])
        elif template_id == "sensor_network":
            writer.writerow(["ID", "Zone", "Type", "Name", "Battery", "Active", "Last Reading"])
            query = select(Sensor)
            if zone_id:
                query = query.where(Sensor.zone_id == zone_id)
            result = await db.execute(query)
            for s in result.scalars().all():
                writer.writerow([str(s.id), str(s.zone_id), s.sensor_type.value, s.name, s.battery_level, s.is_active, str(s.last_reading_at)])
        else:
            writer.writerow(["Report", "Generated At"])
            writer.writerow([template_id, str(datetime.utcnow())])

        csv_content = output.getvalue().encode("utf-8")
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=catguard_{template_id}.csv"},
        )

    elif format == "geojson":
        features = []
        if zone_id:
            query = select(Detection).where(Detection.zone_id == zone_id)
            result = await db.execute(query)
            for d in result.scalars().all():
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"id": str(d.id), "type": d.detection_type.value, "severity": d.severity.value, "confidence": d.confidence},
                })
        geojson = {"type": "FeatureCollection", "features": features}
        return Response(
            content=json.dumps(geojson).encode(),
            media_type="application/geo+json",
            headers={"Content-Disposition": f"attachment; filename=catguard_{template_id}.geojson"},
        )

    return {"message": "PDF generation requires ReportLab setup", "template": template_id}


@router.post("/schedule")
async def schedule_report(
    template_id: str,
    zone_id: Optional[UUID] = None,
    frequency: str = Query("weekly", regex="^(daily|weekly|monthly)$"),
    format: str = Query("csv"),
    _=Depends(get_current_active_user),
):
    return {"message": f"Report '{template_id}' scheduled {frequency}", "zone_id": str(zone_id) if zone_id else None, "format": format}
