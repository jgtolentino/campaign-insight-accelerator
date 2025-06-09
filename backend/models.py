from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey, Float, Enum, func, Table, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

# Association tables for many-to-many relationships
campaign_tags = Table(
    'campaign_tags',
    Base.metadata,
    Column('campaign_id', Integer, ForeignKey('campaigns.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

asset_tags = Table(
    'asset_tags',
    Base.metadata,
    Column('asset_id', Integer, ForeignKey('assets.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class SensorStatus(enum.Enum):
    OK = "OK"
    FAIL = "FAIL"

class RetrainingStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    status = Column(Enum(SensorStatus), nullable=False)
    last_run = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    metrics = relationship("SensorMetrics", back_populates="sensor")

class SensorMetrics(Base):
    __tablename__ = "sensor_metrics"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=False)
    accuracy = Column(Float, nullable=False)
    latency = Column(Float, nullable=False)
    throughput = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sensor = relationship("Sensor", back_populates="metrics")

class ModelStatus(Base):
    __tablename__ = "model_status"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    last_trained = Column(DateTime(timezone=True), nullable=False)
    accuracy = Column(Float, nullable=False)
    latency = Column(Float, nullable=False)
    throughput = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class RetrainingJob(Base):
    __tablename__ = "retraining_jobs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)
    status = Column(Enum(RetrainingStatus), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    campaigns = relationship('Campaign', secondary=campaign_tags, back_populates='tags')
    assets = relationship('Asset', secondary=asset_tags, back_populates='tags')

class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tags = relationship('Tag', secondary=campaign_tags, back_populates='campaigns')
    assets = relationship('Asset', back_populates='campaign')

class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    file_path = Column(String(255))
    file_type = Column(String(50))
    file_size = Column(Integer)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    campaign = relationship('Campaign', back_populates='assets')
    tags = relationship('Tag', secondary=asset_tags, back_populates='assets') 