from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from .database import Base
import uuid

def gen_id():
    return str(uuid.uuid4())[:12]

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_id = Column(String, nullable=True)
    category = Column(String, default="其他")
    job_type = Column(String, default="校招")
    description = Column(Text, default="")
    requirements = Column(Text, default="")
    education_req = Column(String, nullable=True)
    major_req = Column(String, nullable=True)
    experience_req = Column(String, nullable=True)
    skills = Column(JSON, default=list)
    salary_raw = Column(String, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_unit = Column(String, default="month")
    salary_currency = Column(String, default="CNY")
    salary_negotiable = Column(Boolean, default=False)
    location_raw = Column(String, nullable=True)
    location_province = Column(String, nullable=True)
    location_city = Column(String, nullable=True)
    location_district = Column(String, nullable=True)
    remote_allowed = Column(Boolean, default=False)
    recruit_number = Column(Integer, nullable=True)
    deadline = Column(String, nullable=True)
    source = Column(String, default="hnust")
    source_url = Column(String, default="")
    source_type = Column(String, default="careers")
    status = Column(String, default="ACTIVE")
    publish_date = Column(String, nullable=True)
    crawl_time = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False)
    industry = Column(String, nullable=True)
    sub_industry = Column(String, nullable=True)
    staff_count_range = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    risk_score = Column(Integer, nullable=True)
    overall_score = Column(String, nullable=True)
    basic_info = Column(JSON, nullable=True)
    risk_assessment = Column(JSON, nullable=True)
    research_time = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    student_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    major = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    preferred_cities = Column(JSON, default=list)
    preferred_categories = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
