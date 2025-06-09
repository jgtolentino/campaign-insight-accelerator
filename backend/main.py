from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from functools import wraps

from . import models, db
from .db import get_db

app = FastAPI(title="CES Monitor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT verification
def verify_jwt(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Tenant-aware database session
def get_tenant_session(token_payload: dict = Depends(verify_jwt)):
    tenant = token_payload.get("tenant_id", "scout")  # Default to 'scout' if not specified
    db_session = next(get_db())
    db_session.execute(f"SET app.current_tenant = '{tenant}'")
    return db_session

@app.get("/api/sensors")
def get_sensors(db: Session = Depends(get_tenant_session)):
    sensors = db.query(models.Sensor).all()
    return [
        {
            "id": sensor.id,
            "name": sensor.name,
            "status": sensor.status.value,
            "lastRun": sensor.last_run.isoformat(),
            "metrics": [
                {
                    "accuracy": metric.accuracy,
                    "latency": metric.latency,
                    "throughput": metric.throughput,
                    "timestamp": metric.timestamp.isoformat()
                }
                for metric in sensor.metrics
            ] if sensor.metrics else None
        }
        for sensor in sensors
    ]

@app.get("/api/metrics/history")
def get_metric_history(
    hours: int = 24,
    db: Session = Depends(get_tenant_session)
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    metrics = (
        db.query(models.SensorMetrics)
        .filter(models.SensorMetrics.timestamp >= cutoff)
        .order_by(models.SensorMetrics.timestamp)
        .all()
    )
    
    return [
        {
            "timestamp": metric.timestamp.isoformat(),
            "accuracy": metric.accuracy,
            "latency": metric.latency,
            "throughput": metric.throughput
        }
        for metric in metrics
    ]

@app.post("/api/retrain")
def trigger_retrain(db: Session = Depends(get_tenant_session)):
    tenant = db.execute("SELECT current_setting('app.current_tenant')").scalar()
    job = models.RetrainingJob(
        id=str(uuid.uuid4()),
        tenant_id=tenant,
        status=models.RetrainingStatus.PENDING,
        started_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    
    # Here you would trigger your actual retraining process
    # For now, we'll just return the job ID
    return {"jobId": job.id}

@app.get("/api/model/status")
def get_model_status(db: Session = Depends(get_tenant_session)):
    status = db.query(models.ModelStatus).order_by(models.ModelStatus.updated_at.desc()).first()
    if not status:
        raise HTTPException(status_code=404, detail="No model status found")
    
    return {
        "status": status.status,
        "lastTrained": status.last_trained.isoformat(),
        "metrics": {
            "accuracy": status.accuracy,
            "latency": status.latency,
            "throughput": status.throughput
        }
    }

@app.get("/api/retraining/jobs")
def get_retraining_jobs(db: Session = Depends(get_tenant_session)):
    jobs = db.query(models.RetrainingJob).order_by(models.RetrainingJob.created_at.desc()).all()
    return [
        {
            "id": job.id,
            "status": job.status.value,
            "startedAt": job.started_at.isoformat(),
            "completedAt": job.completed_at.isoformat() if job.completed_at else None,
            "errorMessage": job.error_message
        }
        for job in jobs
    ] 