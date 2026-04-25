from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import bcrypt, db
from app.models import BeneficiaryProfile, IdentityRecord, RoleType, User, UserRole
from app.services.audit import write_audit_log
from app.services.identity import (
    build_mpid,
    encrypt_national_id,
    hash_national_id,
    identity_exists,
)

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/register")
def register():
    payload = request.get_json() or {}
    required = ["email", "password", "full_name", "phone", "role", "national_id"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400

    role_value = payload["role"]
    if role_value not in {r.value for r in RoleType}:
        return jsonify({"error": "invalid role"}), 400

    if User.query.filter_by(email=payload["email"]).first():
        return jsonify({"error": "email already exists"}), 409

    national_id_hash = hash_national_id(payload["national_id"])
    if role_value == RoleType.BENEFICIARY.value and identity_exists(national_id_hash):
        return jsonify({"error": "duplicate beneficiary identity detected"}), 409

    user = User(
        email=payload["email"].strip().lower(),
        password_hash=bcrypt.generate_password_hash(payload["password"]).decode("utf-8"),
        full_name=payload["full_name"].strip(),
        phone=payload["phone"].strip(),
    )
    db.session.add(user)
    db.session.flush()

    organization_id = payload.get("organization_id")
    role = UserRole(user_id=user.id, role=RoleType(role_value), organization_id=organization_id)
    db.session.add(role)

    identity = IdentityRecord(
        user_id=user.id,
        mpid=build_mpid(national_id_hash),
        national_id_encrypted=encrypt_national_id(payload["national_id"], current_app.config["NATIONAL_ID_KEY"]),
        national_id_hash=national_id_hash,
        golden_record_json={
            "full_name": payload["full_name"],
            "phone": payload["phone"],
            "email": payload["email"],
        },
    )
    db.session.add(identity)

    if role_value == RoleType.BENEFICIARY.value:
        profile = BeneficiaryProfile(
            user_id=user.id,
            household_size=payload.get("household_size"),
            monthly_income=payload.get("monthly_income"),
            region=payload.get("region"),
        )
        db.session.add(profile)

    write_audit_log(user.id, "register", "user", user.id, {"role": role_value, "organization_id": organization_id})
    db.session.commit()
    return jsonify({"message": "registered", "user_id": user.id}), 201


@bp.post("/login")
def login():
    payload = request.get_json() or {}
    user = User.query.filter_by(email=payload.get("email", "").strip().lower()).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, payload.get("password", "")):
        return jsonify({"error": "invalid credentials"}), 401

    roles = [r.role.value for r in user.roles]
    organization_ids = [r.organization_id for r in user.roles if r.organization_id is not None]
    claims = {"roles": roles, "organization_ids": organization_ids}
    access = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(user.id), additional_claims=claims)
    write_audit_log(user.id, "login", "user", user.id, {"roles": roles})
    db.session.commit()
    return jsonify({"access_token": access, "refresh_token": refresh, "roles": roles})


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_access():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "invalid token user"}), 404

    roles = [r.role.value for r in user.roles]
    organization_ids = [r.organization_id for r in user.roles if r.organization_id is not None]
    access = create_access_token(identity=str(user.id), additional_claims={"roles": roles, "organization_ids": organization_ids})
    return jsonify({"access_token": access})
