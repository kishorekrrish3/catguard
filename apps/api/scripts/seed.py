"""
CAT-Guard Database Seeder
Run from apps/api directory: python scripts/seed.py
"""
import asyncio, sys, os, random
from datetime import datetime, timedelta, date
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://catguard:catguard_secret@localhost:5432/catguard_db")

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, Polygon

from app.models.zone import Zone
from app.models.user import User, UserRole
from app.models.sensor import Sensor, SensorType, SensorProtocol
from app.models.sensor_reading import SensorReading, QualityFlag
from app.models.detection import Detection, DetectionType, DetectionSeverity
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus, AlertSource
from app.models.alert_rule import AlertRule, RuleOperator
from app.models.community_report import CommunityReport, ReportType, ReportStatus
from app.models.imagery import SatelliteImagery, ImagerySource, ProcessingStatus
from app.core.security import get_password_hash

ZONES = [
    {"name":"Silent Valley CAT Zone","description":"Primary tropical rainforest catchment area in Palakkad district","status":"active","area_hectares":8952.0,"polygon":[(76.38,11.08),(76.52,11.08),(76.52,11.20),(76.38,11.20),(76.38,11.08)],"center":(76.45,11.14)},
    {"name":"Parambikulam CAT Zone","description":"Tiger reserve and watershed management area","status":"active","area_hectares":6392.0,"polygon":[(76.68,10.38),(76.82,10.38),(76.82,10.52),(76.68,10.52),(76.68,10.38)],"center":(76.75,10.45)},
    {"name":"Periyar CAT Zone","description":"Biosphere reserve with intensive monitoring requirements","status":"monitoring","area_hectares":7751.0,"polygon":[(77.12,9.45),(77.28,9.45),(77.28,9.62),(77.12,9.62),(77.12,9.45)],"center":(77.20,9.53)},
]
SENSOR_UNITS={"soil_moisture":"%","soil_temperature":"C","soil_ph":"pH","air_temperature":"C","humidity":"%","precipitation":"mm","motion":"events","camera":"events","air_quality":"AQI"}
SENSOR_RANGES={"soil_moisture":(20,85),"soil_temperature":(18,32),"soil_ph":(5.5,7.5),"air_temperature":(18,38),"humidity":(60,98),"precipitation":(0,50),"motion":(0,10),"camera":(0,5),"air_quality":(25,150)}

async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        print("Starting CAT-Guard database seed...")
        zone_objects = []
        for z in ZONES:
            zone = Zone(id=uuid4(), name=z["name"], description=z["description"], status=z["status"],
                        area_hectares=z["area_hectares"], geom=from_shape(Polygon(z["polygon"]), srid=4326))
            session.add(zone)
            zone_objects.append((zone, z["center"]))
        await session.flush()
        print(f"  Created {len(zone_objects)} zones")

        ph = get_password_hash("CatGuard@123")
        users_data = [
            {"username":"manager1","email":"manager@catguard.com","full_name":"Arjun Nair","role":UserRole.forest_manager},
            {"username":"officer1","email":"officer@catguard.com","full_name":"Priya Menon","role":UserRole.field_officer},
            {"username":"analyst1","email":"analyst@catguard.com","full_name":"Rahul Varma","role":UserRole.data_analyst},
            {"username":"reporter1","email":"reporter@catguard.com","full_name":"Ananya Kumar","role":UserRole.community_reporter},
            {"username":"admin1","email":"admin@catguard.com","full_name":"System Admin","role":UserRole.administrator},
        ]
        user_objects = []
        for u in users_data:
            user = User(id=uuid4(), hashed_password=ph, zone_id=zone_objects[0][0].id, **u)
            session.add(user)
            user_objects.append(user)
        await session.flush()
        print(f"  Created {len(user_objects)} users")

        sensor_types = list(SensorType)
        sensor_objects = []
        for zone, center in zone_objects:
            for i in range(10):
                st = sensor_types[i % len(sensor_types)]
                sensor = Sensor(id=uuid4(), zone_id=zone.id, sensor_type=st, name=f"{st.value.replace('_',' ').title()} {i+1}",
                    location=from_shape(Point(center[0]+random.uniform(-0.06,0.06), center[1]+random.uniform(-0.06,0.06)), srid=4326),
                    protocol=random.choice(list(SensorProtocol)), battery_level=random.uniform(15,100),
                    is_active=random.random()>0.1, installed_at=datetime.utcnow()-timedelta(days=random.randint(30,365)))
                session.add(sensor)
                sensor_objects.append((sensor, st))
        await session.flush()
        print(f"  Created {len(sensor_objects)} sensors")

        reading_count = 0
        now = datetime.utcnow()
        for sensor, st in sensor_objects[:20]:
            lo, hi = SENSOR_RANGES.get(st.value, (0,100))
            unit = SENSOR_UNITS.get(st.value, "unit")
            base = random.uniform(lo, hi)
            for h in range(7*24*2):
                ts = now - timedelta(minutes=h*30)
                val = max(lo, min(hi, base + random.gauss(0, (hi-lo)*0.05)))
                reading = SensorReading(id=uuid4(), sensor_id=sensor.id, timestamp=ts, value=round(val,2), unit=unit,
                    quality_flag=QualityFlag.good if random.random()>0.05 else QualityFlag.suspect)
                session.add(reading)
                reading_count += 1
        await session.flush()
        print(f"  Created {reading_count} sensor readings")

        for zone, _ in zone_objects:
            for days_ago in [0,7,14,30,45,60]:
                acq = date.today()-timedelta(days=days_ago)
                base_ndvi = random.uniform(0.45,0.75)
                img = SatelliteImagery(id=uuid4(), zone_id=zone.id, acquisition_date=acq,
                    cloud_cover_percent=random.uniform(0,30), ndvi_mean=round(base_ndvi,4),
                    ndvi_min=round(base_ndvi-random.uniform(0.1,0.2),4), ndvi_max=round(min(base_ndvi+0.15,0.95),4),
                    savi_mean=round(base_ndvi*0.85,4), source=random.choice(list(ImagerySource)),
                    processing_status=ProcessingStatus.completed)
                session.add(img)
        print("  Created satellite imagery records")

        det_types, det_sevs = list(DetectionType), list(DetectionSeverity)
        for zone, center in zone_objects:
            for _ in range(50):
                d = Detection(id=uuid4(), zone_id=zone.id, detection_type=random.choice(det_types),
                    confidence=round(random.uniform(0.55,0.99),3), severity=random.choice(det_sevs),
                    location=from_shape(Point(center[0]+random.uniform(-0.05,0.05), center[1]+random.uniform(-0.05,0.05)), srid=4326),
                    verified=random.random()>0.7, timestamp=now-timedelta(days=random.randint(0,90), hours=random.randint(0,23)))
                session.add(d)
        print("  Created 150 detections")

        al_types, al_sevs, al_stats = list(AlertType), list(AlertSeverity), list(AlertStatus)
        for zone, center in zone_objects:
            for _ in range(20):
                at, asev, astat = random.choice(al_types), random.choice(al_sevs), random.choice(al_stats)
                a = Alert(id=uuid4(), zone_id=zone.id, alert_type=at, severity=asev,
                    title=f"{at.value.replace('_',' ').title()} Detected", description=f"Automated detection in {zone.name}",
                    status=astat, source_type=random.choice(list(AlertSource)),
                    location=from_shape(Point(center[0]+random.uniform(-0.04,0.04), center[1]+random.uniform(-0.04,0.04)), srid=4326),
                    created_at=now-timedelta(days=random.randint(0,30)),
                    acknowledged_at=now-timedelta(days=random.randint(0,5)) if astat!=AlertStatus.active else None)
                session.add(a)
        print("  Created 60 alerts")

        rep_types, rep_stats = list(ReportType), list(ReportStatus)
        for zone, center in zone_objects:
            for _ in range(10):
                r = CommunityReport(id=uuid4(), zone_id=zone.id, reporter_id=user_objects[3].id,
                    is_anonymous=random.random()>0.7, report_type=random.choice(rep_types),
                    description="Observed suspicious activity near zone boundary.",
                    location=from_shape(Point(center[0]+random.uniform(-0.05,0.05), center[1]+random.uniform(-0.05,0.05)), srid=4326),
                    status=random.choice(rep_stats), submitted_at=now-timedelta(days=random.randint(0,60)))
                session.add(r)
        print("  Created 30 community reports")

        rules = [
            AlertRule(id=uuid4(), name="Low NDVI Alert", alert_type="vegetation_loss", condition_field="ndvi_mean", condition_operator=RuleOperator.lt, condition_value=0.3, severity="high", created_by=user_objects[0].id),
            AlertRule(id=uuid4(), name="High Confidence Detection", alert_type="illegal_activity", condition_field="confidence", condition_operator=RuleOperator.gt, condition_value=0.85, severity="critical", created_by=user_objects[0].id),
            AlertRule(id=uuid4(), name="Low Battery Sensor", alert_type="sensor_anomaly", condition_field="battery_level", condition_operator=RuleOperator.lt, condition_value=15, severity="medium", created_by=user_objects[0].id),
            AlertRule(id=uuid4(), name="High Soil Moisture Flood Risk", alert_type="weather_extreme", condition_field="soil_moisture", condition_operator=RuleOperator.gt, condition_value=90, severity="low", created_by=user_objects[0].id),
            AlertRule(id=uuid4(), name="Unauthorized Access Motion", alert_type="unauthorized_access", condition_field="motion_events", condition_operator=RuleOperator.gt, condition_value=5, severity="high", created_by=user_objects[0].id),
        ]
        for rule in rules:
            session.add(rule)
        await session.commit()
        print(f"  Created {len(rules)} alert rules")
        print("")
        print("Seed completed! Login credentials (all: CatGuard@123):")
        for u in users_data:
            print(f"  {u['role'].value:25} | {u['email']}")

if __name__ == "__main__":
    asyncio.run(seed())
