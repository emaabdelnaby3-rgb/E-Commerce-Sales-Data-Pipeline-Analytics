import uuid
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Case, CaseStatus, CaseStatusHistory, Donation, PaymentTransaction
from app.services.audit import write_audit_log
from app.services.rbac import require_roles

bp = Blueprint("donor", __name__, url_prefix="/donor")


@bp.get("/cases")
@jwt_required()
@require_roles("donor", "charity_admin", "government_admin")
def list_cases():
    status_value = request.args.get("status", CaseStatus.APPROVED.value)
    page = request.args.get("page", 1, type=int)
    page_size = min(request.args.get("page_size", 20, type=int), 100)

    try:
        status = CaseStatus(status_value)
    except ValueError:
        return jsonify({"error": "invalid status filter"}), 400

    query = Case.query.filter(Case.status == status)

    category = request.args.get("category")
    if category:
        query = query.filter(Case.category == category)

    org_id = request.args.get("organization_id")
    if org_id:
        query = query.filter(Case.organization_id == int(org_id))

    total = query.count()
    rows = query.order_by(Case.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return jsonify(
        {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": [
                {
                    "case_id": c.id,
                    "title": c.title,
                    "category": c.category,
                    "organization_id": c.organization_id,
                    "amount_requested": float(c.amount_requested),
                    "amount_funded": float(c.amount_funded),
                }
                for c in rows
            ],
        }
    )


@bp.post("/donate")
@jwt_required()
@require_roles("donor")
def donate():
    payload = request.get_json() or {}
    case_id = payload.get("case_id")
    amount = payload.get("amount")
    if not case_id or amount is None:
        return jsonify({"error": "case_id and amount are required"}), 400

    case = db.session.get(Case, case_id)
    if not case or case.status not in {CaseStatus.APPROVED, CaseStatus.FUNDED}:
        return jsonify({"error": "case unavailable for donations"}), 400

    try:
        amount_decimal = Decimal(str(amount))
    except InvalidOperation:
        return jsonify({"error": "amount must be numeric"}), 400

    if amount_decimal <= 0:
        return jsonify({"error": "amount must be positive"}), 400

    donor_user_id = int(get_jwt_identity())
    donation = Donation(
        donor_user_id=donor_user_id,
        case_id=case.id,
        amount=amount_decimal,
        payment_status="pending",
        is_anonymous=bool(payload.get("is_anonymous", False)),
    )
    db.session.add(donation)
    db.session.flush()

    transaction = PaymentTransaction(
        donation_id=donation.id,
        provider=payload.get("provider", "internal_sim"),
        provider_ref=f"txn_{uuid.uuid4().hex[:16]}",
        status="initiated",
        metadata_json={"channel": payload.get("payment_method", "card")},
    )
    db.session.add(transaction)

    write_audit_log(donor_user_id, "donation_initiated", "donation", donation.id, {"amount": str(amount_decimal)})
    db.session.commit()
    return jsonify({"donation_id": donation.id, "transaction_ref": transaction.provider_ref, "payment_status": donation.payment_status}), 201


@bp.post("/donations/<int:donation_id>/confirm")
@jwt_required()
@require_roles("donor")
def confirm_donation(donation_id: int):
    donation = db.session.get(Donation, donation_id)
    if not donation:
        return jsonify({"error": "donation not found"}), 404

    actor_id = int(get_jwt_identity())
    if donation.donor_user_id != actor_id:
        return jsonify({"error": "forbidden"}), 403

    if donation.payment_status == "succeeded":
        return jsonify({"message": "already confirmed"})

    tx = PaymentTransaction.query.filter_by(donation_id=donation_id).first()
    if not tx:
        return jsonify({"error": "transaction missing"}), 409

    previous_status = donation.payment_status
    donation.payment_status = "succeeded"
    tx.status = "succeeded"

    case = db.session.get(Case, donation.case_id)
    prior_case_status = case.status
    case.amount_funded = Decimal(str(case.amount_funded)) + Decimal(str(donation.amount))
    if case.amount_funded >= case.amount_requested:
        case.status = CaseStatus.FUNDED

    if case.status != prior_case_status:
        db.session.add(
            CaseStatusHistory(
                case_id=case.id,
                from_status=prior_case_status,
                to_status=case.status,
                changed_by_user_id=actor_id,
                reason="donation confirmed",
            )
        )

    write_audit_log(actor_id, "donation_confirmed", "donation", donation.id, {"from": previous_status, "to": donation.payment_status})
    db.session.commit()
    return jsonify({"donation_id": donation.id, "payment_status": donation.payment_status, "case_status": case.status.value})


@bp.get("/donations")
@jwt_required()
@require_roles("donor")
def track_donations():
    donor_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    page_size = min(request.args.get("page_size", 20, type=int), 100)

    query = Donation.query.filter_by(donor_user_id=donor_id)
    total = query.count()
    rows = query.order_by(Donation.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return jsonify(
        {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": [
                {
                    "donation_id": d.id,
                    "case_id": d.case_id,
                    "amount": float(d.amount),
                    "payment_status": d.payment_status,
                    "created_at": d.created_at.isoformat(),
                }
                for d in rows
            ],
        }
    )
