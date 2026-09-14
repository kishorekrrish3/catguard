"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-09-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
import geoalchemy2

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_enum_safe(name: str, values: list[str]) -> None:
    vals = ", ".join(f"'{v}'" for v in values)
    op.execute(f"DO $$ BEGIN CREATE TYPE {name} AS ENUM ({vals}); EXCEPTION WHEN duplicate_object THEN null; END $$;")


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    # Enums
    create_enum_safe("zone_status_enum", ["active", "monitoring", "restricted", "archived"])
    create_enum_safe("user_role_enum", ["forest_manager", "field_officer", "data_analyst", "community_reporter", "administrator"])
    create_enum_safe("imagery_source_enum", ["sentinel2", "landsat9", "commercial", "drone"])
    create_enum_safe("processing_status_enum", ["pending", "processing", "completed", "failed"])
    create_enum_safe("detection_type_enum", ["illegal_logging", "encroachment", "fire_risk", "vegetation_loss", "suspicious_activity", "flood_risk"])
    create_enum_safe("detection_severity_enum", ["critical", "high", "medium", "low"])
    create_enum_safe("sensor_type_enum", ["soil_moisture", "soil_temperature", "soil_ph", "air_temperature", "humidity", "precipitation", "motion", "camera", "air_quality"])
    create_enum_safe("sensor_protocol_enum", ["lorawan", "nb_iot", "wifi", "cellular"])
    create_enum_safe("quality_flag_enum", ["good", "suspect", "bad"])
    create_enum_safe("alert_type_enum", ["vegetation_loss", "illegal_activity", "sensor_anomaly", "unauthorized_access", "fire_risk", "weather_extreme"])
    create_enum_safe("alert_severity_enum", ["critical", "high", "medium", "low"])
    create_enum_safe("alert_status_enum", ["active", "acknowledged", "resolved", "false_positive"])
    create_enum_safe("alert_source_enum", ["ml_detection", "sensor_threshold", "community_report", "manual"])
    create_enum_safe("rule_operator_enum", ["gt", "lt", "gte", "lte", "eq", "neq"])
    create_enum_safe("report_type_enum", ["illegal_logging", "encroachment", "fire", "poaching", "waste_dumping", "other"])
    create_enum_safe("report_status_enum", ["pending", "under_review", "verified", "resolved", "rejected"])

    # zones
    op.create_table(
        "zones",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("geom", geoalchemy2.types.Geometry("POLYGON", srid=4326), nullable=True),
        sa.Column("status", ENUM(name="zone_status_enum", create_type=False), nullable=False, server_default="active"),
        sa.Column("area_hectares", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_zones_name", "zones", ["name"])

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", ENUM(name="user_role_enum", create_type=False), nullable=False),
        sa.Column("zone_id", sa.UUID(), sa.ForeignKey("zones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("preferences", sa.JSON(), server_default="{}"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    # satellite_imagery
    op.create_table(
        "satellite_imagery",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("zone_id", sa.UUID(), sa.ForeignKey("zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("acquisition_date", sa.Date(), nullable=False),
        sa.Column("cloud_cover_percent", sa.Float(), nullable=True),
        sa.Column("ndvi_mean", sa.Float(), nullable=True),
        sa.Column("ndvi_min", sa.Float(), nullable=True),
        sa.Column("ndvi_max", sa.Float(), nullable=True),
        sa.Column("savi_mean", sa.Float(), nullable=True),
        sa.Column("source", ENUM(name="imagery_source_enum", create_type=False), server_default="sentinel2"),
        sa.Column("path_url", sa.String(1024), nullable=True),
        sa.Column("thumbnail_url", sa.String(1024), nullable=True),
        sa.Column("processing_status", ENUM(name="processing_status_enum", create_type=False), server_default="pending"),
        sa.Column("metadata_json", sa.JSON(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # detections
    op.create_table(
        "detections",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("zone_id", sa.UUID(), sa.ForeignKey("zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("detection_type", ENUM(name="detection_type_enum", create_type=False), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("location", geoalchemy2.types.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("bounding_box", geoalchemy2.types.Geometry("POLYGON", srid=4326), nullable=True),
        sa.Column("severity", ENUM(name="detection_severity_enum", create_type=False), nullable=False),
        sa.Column("model_version", sa.String(50), server_default="v1.0"),
        sa.Column("image_url", sa.String(1024), nullable=True),
        sa.Column("verified", sa.Boolean(), server_default="false"),
        sa.Column("verified_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column("metadata_json", sa.JSON(), server_default="{}"),
    )

    # sensors
    op.create_table(
        "sensors",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("zone_id", sa.UUID(), sa.ForeignKey("zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sensor_type", ENUM(name="sensor_type_enum", create_type=False), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", geoalchemy2.types.Geometry("POINT", srid=4326), nullable=False),
        sa.Column("protocol", ENUM(name="sensor_protocol_enum", create_type=False), server_default="lorawan"),
        sa.Column("battery_level", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("last_reading_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_value", sa.Float(), nullable=True),
        sa.Column("calibration_offset", sa.Float(), server_default="0"),
        sa.Column("installed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("metadata_json", sa.JSON(), server_default="{}"),
    )

    # sensor_readings (TimescaleDB hypertable)
    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("sensor_id", sa.UUID(), sa.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), primary_key=True, nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("quality_flag", ENUM(name="quality_flag_enum", create_type=False), server_default="good"),
        sa.Column("raw_value", sa.Float(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), server_default="{}"),
    )
    op.create_index("ix_sensor_readings_sensor_timestamp", "sensor_readings", ["sensor_id", "timestamp"])
    # Convert to TimescaleDB hypertable
    op.execute("SELECT create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE)")

    # alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("zone_id", sa.UUID(), sa.ForeignKey("zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alert_type", ENUM(name="alert_type_enum", create_type=False), nullable=False),
        sa.Column("severity", ENUM(name="alert_severity_enum", create_type=False), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", ENUM(name="alert_status_enum", create_type=False), server_default="active"),
        sa.Column("source_type", ENUM(name="alert_source_enum", create_type=False), server_default="ml_detection"),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("location", geoalchemy2.types.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("acknowledged_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column("metadata_json", sa.JSON(), server_default="{}"),
    )

    # alert_rules
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("zone_id", sa.UUID(), sa.ForeignKey("zones.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("alert_type", sa.String(100), nullable=False),
        sa.Column("condition_field", sa.String(100), nullable=False),
        sa.Column("condition_operator", ENUM(name="rule_operator_enum", create_type=False), nullable=False),
        sa.Column("condition_value", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(20), server_default="medium"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("cooldown_minutes", sa.Integer(), server_default="60"),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # community_reports
    op.create_table(
        "community_reports",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("zone_id", sa.UUID(), sa.ForeignKey("zones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reporter_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_anonymous", sa.Boolean(), server_default="false"),
        sa.Column("report_type", ENUM(name="report_type_enum", create_type=False), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", geoalchemy2.types.Geometry("POINT", srid=4326), nullable=False),
        sa.Column("photo_urls", sa.JSON(), server_default="[]"),
        sa.Column("audio_url", sa.String(1024), nullable=True),
        sa.Column("status", ENUM(name="report_status_enum", create_type=False), server_default="pending"),
        sa.Column("assigned_to", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("changes_json", sa.JSON(), server_default="{}"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("integrity_hash", sa.String(64), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("community_reports")
    op.drop_table("alert_rules")
    op.drop_table("alerts")
    op.drop_table("sensor_readings")
    op.drop_table("sensors")
    op.drop_table("detections")
    op.drop_table("satellite_imagery")
    op.drop_table("users")
    op.drop_table("zones")
    for enum in ["zone_status_enum", "user_role_enum", "imagery_source_enum", "processing_status_enum",
                 "detection_type_enum", "detection_severity_enum", "sensor_type_enum", "sensor_protocol_enum",
                 "quality_flag_enum", "alert_type_enum", "alert_severity_enum", "alert_status_enum",
                 "alert_source_enum", "rule_operator_enum", "report_type_enum", "report_status_enum"]:
        op.execute(f"DROP TYPE IF EXISTS {enum}")
