from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Case, CaseStatus, Donation
from app.services.rbac import require_roles
from app.services.tenancy import get_claim_org_ids, get_claim_roles

bp = Blueprint("analytics", __name__, url_prefix="/analytics")


def _org_filter_from_claims():
    roles = get_claim_roles()
    requested_org = request.args.get("organization_id", type=int)
    if "government_admin" in roles or "platform_admin" in roles:
        return requested_org

    allowed_orgs = get_claim_org_ids()
    if requested_org and requested_org in allowed_orgs:
        return requested_org
    return None if not allowed_orgs else min(allowed_orgs)


@bp.get("/donation-trends")
@jwt_required()
@require_roles("charity_admin", "government_admin", "platform_admin")
def donation_trends():
    org_id = _org_filter_from_claims()
    query = db.session.query(
        func.date_trunc("month", Donation.created_at).label("month"),
        func.coalesce(func.sum(Donation.amount), 0).label("amount"),
    ).join(Case, Case.id == Donation.case_id)

    if org_id:
        query = query.filter(Case.organization_id == org_id)

    rows = query.group_by(func.date_trunc("month", Donation.created_at)).order_by(func.date_trunc("month", Donation.created_at)).all()
    return jsonify([{"month": r.month.date().isoformat(), "amount": float(r.amount)} for r in rows])


@bp.get("/kpis")
@jwt_required()
@require_roles("charity_admin", "government_admin", "platform_admin")
def kpis():
    org_id = _org_filter_from_claims()

    donation_query = db.session.query(func.coalesce(func.sum(Donation.amount), 0)).join(Case, Case.id == Donation.case_id)
    case_query = db.session.query(func.count(Case.id))
    beneficiaries_query = db.session.query(func.count(func.distinct(Case.beneficiary_id)))
    successful_query = db.session.query(func.count(Case.id)).filter(Case.status.in_([CaseStatus.FUNDED, CaseStatus.CLOSED]))

    if org_id:
        donation_query = donation_query.filter(Case.organization_id == org_id)
        case_query = case_query.filter(Case.organization_id == org_id)
        beneficiaries_query = beneficiaries_query.filter(Case.organization_id == org_id)
        successful_query = successful_query.filter(Case.organization_id == org_id)

    total_donations = donation_query.scalar() or 0
    total_beneficiaries = beneficiaries_query.scalar() or 0
    total_cases = case_query.scalar() or 0
    successful = successful_query.scalar() or 0

    return jsonify(
        {
            "total_donations": float(total_donations),
            "number_of_beneficiaries": int(total_beneficiaries),
            "case_success_rate": round((successful / total_cases * 100) if total_cases else 0, 2),
        }
    )


@bp.get("/case-breakdown")
@jwt_required()
@require_roles("charity_admin", "government_admin", "platform_admin")
def case_breakdown():
    org_id = _org_filter_from_claims()
    query = db.session.query(Case.status, func.count(Case.id)).group_by(Case.status)
    if org_id:
        query = query.filter(Case.organization_id == org_id)
    rows = query.all()
    return jsonify({status.value: int(count) for status, count in rows})
