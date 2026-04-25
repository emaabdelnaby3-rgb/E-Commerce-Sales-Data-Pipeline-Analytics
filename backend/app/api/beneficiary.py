import os
import uuid
from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import BeneficiaryProfile, Case, CaseStatus, Document, UserRole
from app.services.rbac import require_roles

bp = Blueprint("beneficiary", __name__, url_prefix="/beneficiary")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def _get_beneficiary_profile(user_id: int):
    profile = BeneficiaryProfile.query.filter_by(user_id=user_id).first()
    return profile


@bp.post("/requests")
@jwt_required()
@require_roles("beneficiary")
def submit_request():
    user_id = int(get_jwt_identity())
    profile = _get_beneficiary_profile(user_id)
    if not profile:
        return jsonify({"error": "beneficiary profile missing"}), 400

    payload = request.get_json() or {}
    required = ["organization_id", "category", "title", "description", "amount_requested"]
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400

    case = Case(
        beneficiary_id=profile.id,
        organization_id=payload["organization_id"],
        category=payload["category"],
        title=payload["title"],
        description=payload["description"],
        amount_requested=Decimal(str(payload["amount_requested"])),
        status=CaseStatus.PENDING,
    )
    db.session.add(case)
    db.session.commit()
    return jsonify({"case_id": case.id, "status": case.status.value}), 201


@bp.post("/documents/upload")
@jwt_required()
@require_roles("beneficiary")
def upload_document():
    file = request.files.get("file")
    doc_type = request.form.get("doc_type")
    case_id = request.form.get("case_id")
    user_id = int(get_jwt_identity())

    if not file or not doc_type:
        return jsonify({"error": "file and doc_type are required"}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "unsupported file format"}), 400

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({"error": "file too large"}), 400

    os.makedirs(current_app.config["UPLOAD_DIR"], exist_ok=True)
    unique_name = f"{uuid.uuid4()}_{filename}"
    save_path = os.path.join(current_app.config["UPLOAD_DIR"], unique_name)
    file.save(save_path)

    document = Document(
        user_id=user_id,
        case_id=int(case_id) if case_id else None,
        doc_type=doc_type,
        file_name=filename,
        file_path=save_path,
    )
    db.session.add(document)
    db.session.commit()
    return jsonify({"document_id": document.id, "path": save_path}), 201


@bp.get("/status")
@jwt_required()
@require_roles("beneficiary")
def view_status():
    user_id = int(get_jwt_identity())
    profile = _get_beneficiary_profile(user_id)
    if not profile:
        return jsonify([])

    cases = Case.query.filter_by(beneficiary_id=profile.id).order_by(Case.created_at.desc()).all()
    data = [
        {
            "case_id": c.id,
            "title": c.title,
            "status": c.status.value,
            "amount_requested": float(c.amount_requested),
            "amount_funded": float(c.amount_funded),
        }
        for c in cases
    ]
    return jsonify(data)
