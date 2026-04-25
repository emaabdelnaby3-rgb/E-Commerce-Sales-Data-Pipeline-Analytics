from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Case, CaseStatus, Donation
from app.services.rbac import require_roles

bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@bp.get("/donation-trends")
@jwt_required()
@require_roles("charity_admin", "government_admin")
def donation_trends():
    rows = (
        db.session.query(
            func.date_trunc("month", Donation.created_at).label("month"),
            func.coalesce(func.sum(Donation.amount), 0).label("amount"),
        )
        .group_by(func.date_trunc("month", Donation.created_at))
        .order_by(func.date_trunc("month", Donation.created_at))
        .all()
    )
    return jsonify([{"month": r.month.date().isoformat(), "amount": float(r.amount)} for r in rows])


@bp.get("/kpis")
@jwt_required()
@require_roles("charity_admin", "government_admin")
def kpis():
    total_donations = db.session.query(func.coalesce(func.sum(Donation.amount), 0)).scalar() or 0
    total_beneficiaries = db.session.query(func.count(func.distinct(Case.beneficiary_id))).scalar() or 0
    total_cases = db.session.query(func.count(Case.id)).scalar() or 0
    successful = (
        db.session.query(func.count(Case.id))
        .filter(Case.status.in_([CaseStatus.FUNDED, CaseStatus.CLOSED]))
        .scalar()
        or 0
    )

    return jsonify(
        {
            "total_donations": float(total_donations),
            "number_of_beneficiaries": int(total_beneficiaries),
            "case_success_rate": round((successful / total_cases * 100) if total_cases else 0, 2),
        }
    )


@bp.get("/case-breakdown")
@jwt_required()
@require_roles("charity_admin", "government_admin")
def case_breakdown():
    org_id = request.args.get("organization_id", type=int)
    query = db.session.query(Case.status, func.count(Case.id)).group_by(Case.status)
    if org_id:
        query = query.filter(Case.organization_id == org_id)
    rows = query.all()
    return jsonify({status.value: int(count) for status, count in rows})
