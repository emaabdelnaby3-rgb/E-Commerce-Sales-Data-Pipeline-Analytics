from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Case, CaseStatus, Donation, Organization
from app.services.rbac import require_roles

bp = Blueprint("government", __name__, url_prefix="/government")


@bp.get("/organizations/overview")
@jwt_required()
@require_roles("government_admin")
def organization_overview():
    rows = (
        db.session.query(
            Organization.id,
            Organization.name,
            func.count(Case.id).label("cases_count"),
            func.coalesce(func.sum(Donation.amount), 0).label("donations_total"),
        )
        .outerjoin(Case, Case.organization_id == Organization.id)
        .outerjoin(Donation, Donation.case_id == Case.id)
        .group_by(Organization.id, Organization.name)
        .all()
    )

    return jsonify(
        [
            {
                "organization_id": r.id,
                "name": r.name,
                "cases_count": int(r.cases_count),
                "donations_total": float(r.donations_total),
            }
            for r in rows
        ]
    )


@bp.get("/analytics/system")
@jwt_required()
@require_roles("government_admin")
def system_analytics():
    total_orgs = db.session.query(func.count(Organization.id)).scalar() or 0
    total_cases = db.session.query(func.count(Case.id)).scalar() or 0
    success_cases = (
        db.session.query(func.count(Case.id))
        .filter(Case.status.in_([CaseStatus.FUNDED, CaseStatus.CLOSED]))
        .scalar()
        or 0
    )
    total_donations = db.session.query(func.coalesce(func.sum(Donation.amount), 0)).scalar() or 0

    success_rate = (success_cases / total_cases * 100) if total_cases else 0
    return jsonify(
        {
            "total_organizations": int(total_orgs),
            "total_cases": int(total_cases),
            "total_donations": float(total_donations),
            "case_success_rate": round(success_rate, 2),
        }
    )
