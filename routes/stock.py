from flask import Blueprint, jsonify, request

from services.stock_service import (
    ServiceError,
    adjust_stock,
    get_all_stock,
    get_low_stock,
    get_movements,
    get_movements_for_product,
    get_out_of_stock,
    restock_product,
)

bp = Blueprint("stock", __name__, url_prefix="/api/stock")


@bp.get("")
def list_stock():
    return jsonify(get_all_stock()), 200


@bp.get("/low")
def low_stock():
    return jsonify(get_low_stock()), 200


@bp.get("/out")
def out_of_stock():
    return jsonify(get_out_of_stock()), 200


@bp.get("/movements")
def all_movements():
    return jsonify(get_movements()), 200


@bp.get("/movements/<int:product_id>")
def movements_for_product(product_id):
    try:
        return jsonify(get_movements_for_product(product_id)), 200
    except ServiceError as e:
        return jsonify({"status": "error", "message": str(e)}), e.status_code


@bp.post("/restock")
def restock():
    payload = request.get_json(silent=True) or {}
    try:
        result = restock_product(payload)
    except ServiceError as e:
        return jsonify({"status": "error", "message": str(e)}), e.status_code
    return jsonify(result), 201


@bp.post("/adjust")
def adjust():
    payload = request.get_json(silent=True) or {}
    try:
        result = adjust_stock(payload)
    except ServiceError as e:
        return jsonify({"status": "error", "message": str(e)}), e.status_code
    return jsonify(result), 201
