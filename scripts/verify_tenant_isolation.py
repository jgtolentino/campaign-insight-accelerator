#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime, timedelta

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Sensor, SensorMetrics, ModelStatus, RetrainingJob, SensorStatus, RetrainingStatus
from backend.db import get_db

def verify_tenant_isolation():
    """Verify that tenant isolation is working correctly."""
    print("🔍 Verifying tenant isolation setup...")

    # Create test data for two tenants
    tenant1 = "agency123"
    tenant2 = "agency456"

    # Get database session
    db = next(get_db())

    try:
        # Test 1: Create data for tenant1
        print("\n📝 Creating test data for tenant1...")
        db.execute(text(f"SET app.current_tenant = '{tenant1}'"))
        
        sensor1 = Sensor(
            id=str(uuid.uuid4()),
            name="Test Sensor 1",
            status=SensorStatus.OK,
            last_run=datetime.utcnow(),
            tenant_id=tenant1
        )
        db.add(sensor1)
        db.commit()

        # Test 2: Create data for tenant2
        print("📝 Creating test data for tenant2...")
        db.execute(text(f"SET app.current_tenant = '{tenant2}'"))
        
        sensor2 = Sensor(
            id=str(uuid.uuid4()),
            name="Test Sensor 2",
            status=SensorStatus.OK,
            last_run=datetime.utcnow(),
            tenant_id=tenant2
        )
        db.add(sensor2)
        db.commit()

        # Test 3: Verify tenant1 can only see their data
        print("\n🔒 Testing tenant1 access...")
        db.execute(text(f"SET app.current_tenant = '{tenant1}'"))
        sensors = db.query(Sensor).all()
        print(f"Tenant1 sees {len(sensors)} sensors")
        for sensor in sensors:
            print(f"- {sensor.name} (tenant: {sensor.tenant_id})")

        # Test 4: Verify tenant2 can only see their data
        print("\n🔒 Testing tenant2 access...")
        db.execute(text(f"SET app.current_tenant = '{tenant2}'"))
        sensors = db.query(Sensor).all()
        print(f"Tenant2 sees {len(sensors)} sensors")
        for sensor in sensors:
            print(f"- {sensor.name} (tenant: {sensor.tenant_id})")

        # Test 5: Verify RLS policies
        print("\n🔍 Checking RLS policies...")
        policies = db.execute(text("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
            FROM pg_policies
            WHERE tablename IN ('sensors', 'sensor_metrics', 'model_status', 'retraining_jobs')
        """)).fetchall()
        
        for policy in policies:
            print(f"- {policy.tablename}: {policy.policyname}")

        print("\n✅ Tenant isolation verification complete!")

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        raise
    finally:
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        db.execute(text(f"SET app.current_tenant = '{tenant1}'"))
        db.query(Sensor).filter(Sensor.tenant_id == tenant1).delete()
        db.execute(text(f"SET app.current_tenant = '{tenant2}'"))
        db.query(Sensor).filter(Sensor.tenant_id == tenant2).delete()
        db.commit()
        db.close()

if __name__ == "__main__":
    verify_tenant_isolation() 