import enum
from datetime import datetime

from app.extensions import db


class RoleType(str, enum.Enum):
    BENEFICIARY = "beneficiary"
    DONOR = "donor"
    CHARITY_ADMIN = "charity_admin"
    GOVERNMENT_ADMIN = "government_admin"
    PLATFORM_ADMIN = "platform_admin"


class CaseStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    NEEDS_INFO = "needs_info"
    APPROVED = "approved"
    REJECTED = "rejected"
    FUNDED = "funded"
    CLOSED = "closed"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(25), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    roles = db.relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class Organization(db.Model):
    __tablename__ = "organizations"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    org_type = db.Column(db.String(50), nullable=False)  # charity | government
    registration_no = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class UserRole(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.Enum(RoleType), nullable=False)
    organization_id = db.Column(db.BigInteger, db.ForeignKey("organizations.id"), nullable=True)

    user = db.relationship("User", back_populates="roles")
    organization = db.relationship("Organization")


class IdentityRecord(db.Model):
    __tablename__ = "identity_records"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    mpid = db.Column(db.String(64), nullable=False, unique=True)
    national_id_encrypted = db.Column(db.Text, nullable=False)
    national_id_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    golden_record_json = db.Column(db.JSON, nullable=False, default=dict)


class BeneficiaryProfile(db.Model):
    __tablename__ = "beneficiary_profiles"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, unique=True)
    household_size = db.Column(db.Integer, nullable=True)
    monthly_income = db.Column(db.Numeric(12, 2), nullable=True)
    region = db.Column(db.String(120), nullable=True)


class Case(db.Model):
    __tablename__ = "cases"
    id = db.Column(db.BigInteger, primary_key=True)
    beneficiary_id = db.Column(db.BigInteger, db.ForeignKey("beneficiary_profiles.id"), nullable=False)
    organization_id = db.Column(db.BigInteger, db.ForeignKey("organizations.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount_requested = db.Column(db.Numeric(12, 2), nullable=False)
    amount_funded = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.Enum(CaseStatus), default=CaseStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CaseReview(db.Model):
    __tablename__ = "case_reviews"
    id = db.Column(db.BigInteger, primary_key=True)
    case_id = db.Column(db.BigInteger, db.ForeignKey("cases.id"), nullable=False)
    reviewer_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    decision = db.Column(db.String(20), nullable=False)  # approved/rejected/needs_info
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    case_id = db.Column(db.BigInteger, db.ForeignKey("cases.id"), nullable=True)
    doc_type = db.Column(db.String(80), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Donation(db.Model):
    __tablename__ = "donations"
    id = db.Column(db.BigInteger, primary_key=True)
    donor_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    case_id = db.Column(db.BigInteger, db.ForeignKey("cases.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_status = db.Column(db.String(30), nullable=False, default="succeeded")
    is_anonymous = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.BigInteger, primary_key=True)
    actor_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.String(80), nullable=False)
    details = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
