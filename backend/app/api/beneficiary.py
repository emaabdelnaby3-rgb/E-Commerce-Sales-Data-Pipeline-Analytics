import os
import uuid
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import BeneficiaryProfile, Case, CaseStatus, CaseStatusHistory, Document
from app.services.audit import write_audit_log
from app.services.rbac import require_roles

bp = Blueprint("beneficiary", __name__, url_prefix="/beneficiary")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def _get_beneficiary_profile(user_id: int):
    return BeneficiaryProfile.query.filter_by(user_id=user_id).first()


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

    try:
        amount_requested = Decimal(str(payload["amount_requested"]))
    except InvalidOperation:
        return jsonify({"error": "amount_requested must be numeric"}), 400

    if amount_requested <= 0:
        return jsonify({"error": "amount_requested must be positive"}), 400

    case = Case(
        beneficiary_id=profile.id,
        organization_id=int(payload["organization_id"]),
        category=payload["category"],
        title=payload["title"],
        description=payload["description"],
        amount_requested=amount_requested,
        status=CaseStatus.PENDING,
    )
    db.session.add(case)
    db.session.flush()

    db.session.add(
        CaseStatusHistory(
            case_id=case.id,
            from_status=None,
            to_status=CaseStatus.PENDING,
            changed_by_user_id=user_id,
            reason="initial submission",
        )
    )
    write_audit_log(user_id, "case_submitted", "case", case.id, {"status": case.status.value})
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

    if case_id:
        case = db.session.get(Case, int(case_id))
        if not case:
            return jsonify({"error": "case not found"}), 404

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
    db.session.flush()
    write_audit_log(user_id, "document_uploaded", "document", document.id, {"doc_type": doc_type})
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
    return jsonify(
        [
            {
                "case_id": c.id,
                "title": c.title,
                "status": c.status.value,
                "amount_requested": float(c.amount_requested),
                "amount_funded": float(c.amount_funded),
            }
            for c in cases
        ]
    )
