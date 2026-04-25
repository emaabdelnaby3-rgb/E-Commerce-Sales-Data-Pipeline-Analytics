from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Case, CaseStatus, Donation
from app.services.rbac import require_roles

bp = Blueprint("donor", __name__, url_prefix="/donor")


@bp.get("/cases")
@jwt_required()
@require_roles("donor", "charity_admin", "government_admin")
def list_cases():
    status = request.args.get("status", CaseStatus.APPROVED.value)
    query = Case.query.filter(Case.status == CaseStatus(status))

    category = request.args.get("category")
    if category:
        query = query.filter(Case.category == category)

    org_id = request.args.get("organization_id")
    if org_id:
        query = query.filter(Case.organization_id == int(org_id))

    rows = query.order_by(Case.created_at.desc()).all()
    return jsonify(
        [
            {
                "case_id": c.id,
                "title": c.title,
                "category": c.category,
                "organization_id": c.organization_id,
                "amount_requested": float(c.amount_requested),
                "amount_funded": float(c.amount_funded),
            }
            for c in rows
        ]
    )


@bp.post("/donate")
@jwt_required()
@require_roles("donor")
def donate():
    payload = request.get_json() or {}
    case_id = payload.get("case_id")
    amount = payload.get("amount")
    if not case_id or not amount:
        return jsonify({"error": "case_id and amount are required"}), 400

    case = Case.query.get(case_id)
    if not case or case.status not in {CaseStatus.APPROVED, CaseStatus.FUNDED}:
        return jsonify({"error": "case unavailable for donations"}), 400

    amount_decimal = Decimal(str(amount))
    donation = Donation(
        donor_user_id=int(get_jwt_identity()),
        case_id=case.id,
        amount=amount_decimal,
        payment_status="succeeded",
        is_anonymous=bool(payload.get("is_anonymous", False)),
    )
    case.amount_funded = Decimal(str(case.amount_funded)) + amount_decimal
    if case.amount_funded >= case.amount_requested:
        case.status = CaseStatus.FUNDED

    db.session.add(donation)
    db.session.commit()
    return jsonify({"donation_id": donation.id, "case_status": case.status.value}), 201


@bp.get("/donations")
@jwt_required()
@require_roles("donor")
def track_donations():
    donor_id = int(get_jwt_identity())
    rows = Donation.query.filter_by(donor_user_id=donor_id).order_by(Donation.created_at.desc()).all()
    return jsonify(
        [
            {
                "donation_id": d.id,
                "case_id": d.case_id,
                "amount": float(d.amount),
                "payment_status": d.payment_status,
                "created_at": d.created_at.isoformat(),
            }
            for d in rows
        ]
    )
