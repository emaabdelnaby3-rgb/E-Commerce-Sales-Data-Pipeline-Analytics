from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import BeneficiaryProfile, Case, CaseReview, CaseStatus, Donation
from app.services.rbac import require_roles

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.post("/cases/<int:case_id>/review")
@jwt_required()
@require_roles("charity_admin")
def review_case(case_id: int):
    payload = request.get_json() or {}
    decision = payload.get("decision")
    notes = payload.get("notes")
    if decision not in {"approved", "rejected", "needs_info"}:
        return jsonify({"error": "invalid decision"}), 400

    case = Case.query.get(case_id)
    if not case:
        return jsonify({"error": "case not found"}), 404

    mapping = {
        "approved": CaseStatus.APPROVED,
        "rejected": CaseStatus.REJECTED,
        "needs_info": CaseStatus.NEEDS_INFO,
    }
    case.status = mapping[decision]

    review = CaseReview(
        case_id=case.id,
        reviewer_user_id=int(get_jwt_identity()),
        decision=decision,
        notes=notes,
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"case_id": case.id, "status": case.status.value})


@bp.get("/beneficiaries")
@jwt_required()
@require_roles("charity_admin")
def manage_beneficiaries():
    rows = BeneficiaryProfile.query.all()
    return jsonify(
        [
            {
                "beneficiary_id": b.id,
                "user_id": b.user_id,
                "household_size": b.household_size,
                "monthly_income": float(b.monthly_income) if b.monthly_income is not None else None,
                "region": b.region,
            }
            for b in rows
        ]
    )


@bp.get("/stats")
@jwt_required()
@require_roles("charity_admin")
def admin_stats():
    total_cases = db.session.query(func.count(Case.id)).scalar() or 0
    approved_cases = db.session.query(func.count(Case.id)).filter(Case.status == CaseStatus.APPROVED).scalar() or 0
    funded_cases = db.session.query(func.count(Case.id)).filter(Case.status == CaseStatus.FUNDED).scalar() or 0
    total_donations = db.session.query(func.coalesce(func.sum(Donation.amount), 0)).scalar() or 0

    return jsonify(
        {
            "total_cases": int(total_cases),
            "approved_cases": int(approved_cases),
            "funded_cases": int(funded_cases),
            "total_donations": float(total_donations),
        }
    )
