from flask import Blueprint, jsonify, request

from backend.models import Sale
from backend.services.sales_service import SaleError, create_sale

bp = Blueprint("sales", __name__, url_prefix="/api/sales")


def get_current_user_id():
    """TEMPORARY, for local testing only.

    Reads the cashier id from an X-User-Id header. Replace this one function
    with the real authentication once it is merged. Nothing else needs to change.
    """
    try:
        return int(request.headers.get("X-User-Id", ""))
    except ValueError:
        return None


@bp.post("")
def make_sale():
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Authentication required."}), 401

    payload = request.get_json(silent=True) or {}
    payment_method = str(payload.get("payment_method") or "cash").strip().lower()[:30]

    try:
        sale = create_sale(user_id, payload.get("items"), payment_method)
    except SaleError as err:
        return jsonify({"error": err.message}), err.status_code

    return jsonify(sale.to_dict()), 201


@bp.get("")
def list_sales():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return jsonify([sale.to_dict() for sale in sales])


@bp.get("/<int:sale_id>")
def get_sale(sale_id):
    return jsonify(Sale.query.get_or_404(sale_id).to_dict())
