from flask import Blueprint, jsonify, request

from services.stock_service import (
    ServiceError,
    get_restock_by_id,
    list_restocks,
    restock_product,
)

bp = Blueprint("restocks", __name__, url_prefix="/api/restocks")


@bp.get("")
def all_restocks():
    return jsonify(list_restocks()), 200


@bp.get("/<int:restock_id>")
def get_restock(restock_id):
    try:
        return jsonify(get_restock_by_id(restock_id)), 200
    except ServiceError as e:
        return jsonify({"status": "error", "message": str(e)}), e.status_code


@bp.post("")
def create_restock():
    payload = request.get_json(silent=True) or {}
    try:
        result = restock_product(payload)
    except ServiceError as e:
        return jsonify({"status": "error", "message": str(e)}), e.status_code
    return jsonify(result), 201
