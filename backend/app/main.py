import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from backend.app.core.config import get_settings
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.core.security import hash_password
from backend.app.core.logging_config import logger
from backend.app.models.models import User, Machine, MaintenanceLog
from backend.app.core.constants import UserRole

from backend.app.api.auth import router as auth_router
from backend.app.api.upload import router as upload_router
from backend.app.api.documents import router as documents_router
from backend.app.api.chat import router as chat_router
from backend.app.api.maintenance import router as maintenance_router
from backend.app.api.compliance import router as compliance_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.graph import router as graph_router
from backend.app.api.dashboard import router as dashboard_router

settings = get_settings()


async def seed_data():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).limit(1))
        if existing.scalar_one_or_none():
            logger.info("Database already seeded, skipping")
            return

        logger.info("Seeding database with sample data...")

        users = [
            User(name="Admin User", email="admin@ikp.com", password_hash=hash_password("admin123"), role=UserRole.ADMIN),
            User(name="Rajesh Kumar", email="rajesh@ikp.com", password_hash=hash_password("rajesh123"), role=UserRole.MAINTENANCE_ENGINEER),
            User(name="Priya Sharma", email="priya@ikp.com", password_hash=hash_password("priya123"), role=UserRole.SAFETY_OFFICER),
            User(name="Amit Patel", email="amit@ikp.com", password_hash=hash_password("amit123"), role=UserRole.PLANT_MANAGER),
            User(name="Sneha Reddy", email="sneha@ikp.com", password_hash=hash_password("sneha123"), role=UserRole.PRODUCTION_ENGINEER),
            User(name="Viewer User", email="viewer@ikp.com", password_hash=hash_password("viewer123"), role=UserRole.VIEWER),
        ]
        for user in users:
            db.add(user)

        now = datetime.now(timezone.utc)
        machines = [
            Machine(
                name="CNC Machine",
                machine_type="CNC Milling",
                manufacturer="Siemens",
                model_number="SINUMERIK 840D",
                serial_number="SN-CNC-2024-001",
                location="Production Floor A",
                department="Manufacturing",
                installation_date=now - timedelta(days=730),
                last_maintenance_date=now - timedelta(days=15),
                status="operational",
                health_score=82.5,
                operating_hours=12500,
                specifications={"max_rpm": 12000, "axis": 5, "power_kw": 15},
            ),
            Machine(
                name="Hydraulic Press",
                machine_type="Hydraulic Press",
                manufacturer="Bosch Rexroth",
                model_number="HPX-500T",
                serial_number="SN-HP-2023-042",
                location="Production Floor A",
                department="Manufacturing",
                installation_date=now - timedelta(days=1095),
                last_maintenance_date=now - timedelta(days=30),
                status="operational",
                health_score=78.0,
                operating_hours=18200,
                specifications={"max_tonnage": 500, "bed_size_mm": "1200x800", "pressure_bar": 350},
            ),
            Machine(
                name="Conveyor Belt",
                machine_type="Belt Conveyor",
                manufacturer="FlexLink",
                model_number="XM-Series",
                serial_number="SN-CB-2024-015",
                location="Assembly Line B",
                department="Assembly",
                installation_date=now - timedelta(days=365),
                last_maintenance_date=now - timedelta(days=7),
                status="maintenance",
                health_score=65.0,
                operating_hours=6800,
                specifications={"belt_width_mm": 600, "speed_mps": 1.5, "length_m": 25},
            ),
            Machine(
                name="Industrial Robot",
                machine_type="Articulated Robot",
                manufacturer="ABB",
                model_number="IRB 6700",
                serial_number="SN-IR-2024-008",
                location="Assembly Line A",
                department="Assembly",
                installation_date=now - timedelta(days=180),
                last_maintenance_date=now - timedelta(days=45),
                status="operational",
                health_score=92.0,
                operating_hours=3200,
                specifications={"payload_kg": 150, "reach_mm": 2650, "axes": 6},
            ),
            Machine(
                name="Boiler",
                machine_type="Industrial Boiler",
                manufacturer="Thermax",
                model_number="TBW-2000",
                serial_number="SN-BL-2022-003",
                location="Utility Room",
                department="Utilities",
                installation_date=now - timedelta(days=1460),
                last_maintenance_date=now - timedelta(days=60),
                status="operational",
                health_score=71.0,
                operating_hours=24000,
                specifications={"capacity_tph": 2, "pressure_bar": 10, "fuel": "Natural Gas"},
            ),
            Machine(
                name="Compressor",
                machine_type="Screw Compressor",
                manufacturer="Atlas Copco",
                model_number="GA-55",
                serial_number="SN-CP-2023-011",
                location="Utility Room",
                department="Utilities",
                installation_date=now - timedelta(days=900),
                last_maintenance_date=now - timedelta(days=20),
                status="operational",
                health_score=88.0,
                operating_hours=14500,
                specifications={"capacity_cfm": 250, "pressure_bar": 8, "power_kw": 55},
            ),
        ]
        for machine in machines:
            db.add(machine)
        await db.flush()

        machine_ids = {m.name: m.id for m in machines}

        maintenance_logs = [
            MaintenanceLog(
                machine_id=machine_ids["CNC Machine"], issue="Spindle bearing wear detected",
                issue_type="preventive", severity="medium", action_taken="Replaced spindle bearings with SKF-6205 series. Realigned spindle assembly. Test run completed successfully.",
                engineer="Rajesh Kumar", spare_parts_used=["SKF-6205 Bearing", "Spindle Oil"], downtime_hours=4.5, cost=12500, status="completed",
                date=now - timedelta(days=15),
            ),
            MaintenanceLog(
                machine_id=machine_ids["CNC Machine"], issue="Coolant pump failure",
                issue_type="corrective", severity="high", action_taken="Replaced coolant pump motor. Flushed and refilled coolant system. Checked all hoses for leaks.",
                engineer="Rajesh Kumar", spare_parts_used=["Coolant Pump Motor", "Coolant Fluid 20L"], downtime_hours=6.0, cost=18000, status="completed",
                date=now - timedelta(days=45),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Hydraulic Press"], issue="Hydraulic seal leakage in main cylinder",
                issue_type="corrective", severity="high", action_taken="Replaced hydraulic seals on main cylinder. Topped up hydraulic fluid. Pressure tested to 350 bar.",
                engineer="Rajesh Kumar", spare_parts_used=["Hydraulic Seal Kit HS-400", "Hydraulic Fluid 50L"], downtime_hours=8.0, cost=22000, status="completed",
                date=now - timedelta(days=30),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Hydraulic Press"], issue="Overheating detected during continuous operation",
                issue_type="corrective", severity="critical", action_taken="Cleaned heat exchanger. Replaced clogged oil filter. Added auxiliary cooling fan. Temperature now within limits.",
                engineer="Sneha Reddy", spare_parts_used=["Oil Filter HF-200", "Cooling Fan Assembly"], downtime_hours=5.0, cost=15000, status="completed",
                date=now - timedelta(days=90),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Conveyor Belt"], issue="Belt misalignment causing material spillage",
                issue_type="corrective", severity="medium", action_taken="Adjusted tracking rollers. Replaced worn belt section. Aligned drive and tail pulleys.",
                engineer="Rajesh Kumar", spare_parts_used=["Conveyor Belt Section 3m", "Tracking Roller"], downtime_hours=3.0, cost=8500, status="completed",
                date=now - timedelta(days=7),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Conveyor Belt"], issue="Motor overheating due to overload",
                issue_type="corrective", severity="high", action_taken="Replaced overloaded motor with higher capacity unit. Installed overload protection relay.",
                engineer="Sneha Reddy", spare_parts_used=["Drive Motor 5HP", "Overload Relay"], downtime_hours=6.5, cost=25000, status="in_progress",
                date=now - timedelta(days=2),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Industrial Robot"], issue="Scheduled calibration and software update",
                issue_type="preventive", severity="low", action_taken="Performed 6-axis calibration. Updated firmware to v5.2.1. Verified all safety interlocks.",
                engineer="Amit Patel", spare_parts_used=[], downtime_hours=2.0, cost=5000, status="completed",
                date=now - timedelta(days=45),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Boiler"], issue="Annual inspection and tube cleaning",
                issue_type="preventive", severity="medium", action_taken="Chemical cleaning of boiler tubes. Replaced safety valve. Tested emergency shutdown system. Obtained regulatory compliance certificate.",
                engineer="Priya Sharma", spare_parts_used=["Safety Valve SV-100", "Descaling Chemical 10L"], downtime_hours=12.0, cost=35000, status="completed",
                date=now - timedelta(days=60),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Boiler"], issue="Flame sensor malfunction",
                issue_type="corrective", severity="critical", action_taken="Replaced faulty flame sensor. Cleaned burner assembly. Tested ignition sequence 10 times successfully.",
                engineer="Rajesh Kumar", spare_parts_used=["Flame Sensor FS-300", "Ignition Electrode"], downtime_hours=4.0, cost=12000, status="completed",
                date=now - timedelta(days=120),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Compressor"], issue="Air filter replacement and oil change",
                issue_type="preventive", severity="low", action_taken="Replaced intake air filter. Changed compressor oil. Checked all pressure gauges and safety valves.",
                engineer="Rajesh Kumar", spare_parts_used=["Air Filter AF-55", "Compressor Oil 10L"], downtime_hours=2.0, cost=6000, status="completed",
                date=now - timedelta(days=20),
            ),
            MaintenanceLog(
                machine_id=machine_ids["Compressor"], issue="Unusual vibration from drive coupling",
                issue_type="corrective", severity="medium", action_taken="Replaced worn coupling element. Realigned motor shaft. Vibration levels returned to normal.",
                engineer="Sneha Reddy", spare_parts_used=["Flexible Coupling FC-55", "Alignment Shims"], downtime_hours=3.5, cost=9000, status="completed",
                date=now - timedelta(days=75),
            ),
        ]
        for log in maintenance_logs:
            db.add(log)

        await db.commit()
        logger.info("Database seeded successfully with users, machines, and maintenance logs")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Industrial Knowledge Intelligence Platform...")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(settings.SQLITE_DB) or ".", exist_ok=True)

    await init_db()
    await seed_data()

    logger.info("Platform started successfully")
    yield
    logger.info("Platform shutting down...")


app = FastAPI(
    title="Industrial Knowledge Intelligence Platform",
    description="AI-powered Unified Operations Brain for manufacturing industries",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(maintenance_router)
app.include_router(compliance_router)
app.include_router(analytics_router)
app.include_router(graph_router)
app.include_router(dashboard_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "error_code": "INTERNAL_ERROR"},
    )


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
    }
