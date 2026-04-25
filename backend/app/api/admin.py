from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import BeneficiaryProfile, Case, CaseReview, CaseStatus, CaseStatusHistory, Donation
from app.services.audit import write_audit_log
from app.services.rbac import require_roles
from app.services.tenancy import get_claim_org_ids

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

    case = db.session.get(Case, case_id)
    if not case:
        return jsonify({"error": "case not found"}), 404

    allowed_orgs = get_claim_org_ids()
    if case.organization_id not in allowed_orgs:
        return jsonify({"error": "forbidden for organization scope"}), 403

    mapping = {
        "approved": CaseStatus.APPROVED,
        "rejected": CaseStatus.REJECTED,
        "needs_info": CaseStatus.NEEDS_INFO,
    }

    previous = case.status
    case.status = mapping[decision]

    review = CaseReview(
        case_id=case.id,
        reviewer_user_id=int(get_jwt_identity()),
        decision=decision,
        notes=notes,
    )
    db.session.add(review)
    db.session.add(
        CaseStatusHistory(
            case_id=case.id,
            from_status=previous,
            to_status=case.status,
            changed_by_user_id=int(get_jwt_identity()),
            reason=notes,
        )
    )
    write_audit_log(int(get_jwt_identity()), "case_reviewed", "case", case.id, {"decision": decision})
    db.session.commit()
    return jsonify({"case_id": case.id, "status": case.status.value})


@bp.get("/beneficiaries")
@jwt_required()
@require_roles("charity_admin")
def manage_beneficiaries():
    allowed_orgs = get_claim_org_ids()

    rows = (
        db.session.query(BeneficiaryProfile, Case.organization_id)
        .join(Case, Case.beneficiary_id == BeneficiaryProfile.id)
        .filter(Case.organization_id.in_(allowed_orgs))
        .distinct(BeneficiaryProfile.id)
        .all()
    )

    return jsonify(
        [
            {
                "beneficiary_id": b.id,
                "user_id": b.user_id,
                "household_size": b.household_size,
                "monthly_income": float(b.monthly_income) if b.monthly_income is not None else None,
                "region": b.region,
                "organization_id": org_id,
            }
            for b, org_id in rows
        ]
    )


@bp.get("/stats")
@jwt_required()
@require_roles("charity_admin")
def admin_stats():
    allowed_orgs = get_claim_org_ids()

    total_cases = db.session.query(func.count(Case.id)).filter(Case.organization_id.in_(allowed_orgs)).scalar() or 0
    approved_cases = (
        db.session.query(func.count(Case.id))
        .filter(Case.organization_id.in_(allowed_orgs), Case.status == CaseStatus.APPROVED)
        .scalar()
        or 0
    )
    funded_cases = (
        db.session.query(func.count(Case.id))
        .filter(Case.organization_id.in_(allowed_orgs), Case.status == CaseStatus.FUNDED)
        .scalar()
        or 0
    )
    total_donations = (
        db.session.query(func.coalesce(func.sum(Donation.amount), 0))
        .join(Case, Case.id == Donation.case_id)
        .filter(Case.organization_id.in_(allowed_orgs))
        .scalar()
        or 0
    )

    return jsonify(
        {
            "total_cases": int(total_cases),
            "approved_cases": int(approved_cases),
            "funded_cases": int(funded_cases),
            "total_donations": float(total_donations),
        }
    )
