from flask import Blueprint, jsonify, request

from extensions import db
from models import Category

bp = Blueprint("categories", __name__, url_prefix="/api/categories")


def _json_payload():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None
    return payload


def _unsupported_fields(payload):
    unsupported = sorted(set(payload) - {"name"})
    if unsupported:
        return jsonify(
            {"error": f"Unsupported field(s): {', '.join(unsupported)}."}
        ), 400
    return None


@bp.get("")
@bp.get("/read")
def get_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return jsonify([category.to_dict() for category in categories])


@bp.get("/<int:category_id>")
@bp.get("/read/<int:category_id>")
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict())


@bp.post("")
@bp.post("/create")
def create_category():
    payload = _json_payload()
    if payload is None:
        return jsonify({"error": "A JSON object is required."}), 400
    unsupported_response = _unsupported_fields(payload)
    if unsupported_response:
        return unsupported_response

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Category name is required."}), 400
    name = name.strip()

    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category with this name already exists."}), 409

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@bp.put("/<int:category_id>")
@bp.put("/update/<int:category_id>")
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    payload = _json_payload()
    if payload is None:
        return jsonify({"error": "A JSON object is required."}), 400
    unsupported_response = _unsupported_fields(payload)
    if unsupported_response:
        return unsupported_response

    if "name" in payload:
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Category name cannot be empty."}), 400
        name = name.strip()
        if Category.query.filter(
            Category.id != category_id, Category.name == name
        ).first():
            return jsonify({"error": "Category with this name already exists."}), 409
        category.name = name

    db.session.commit()
    return jsonify(category.to_dict())


@bp.delete("/<int:category_id>")
@bp.delete("/delete/<int:category_id>")
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products:
        return jsonify(
            {"error": "Cannot delete a category that still has products."}
        ), 409

    category_name = category.name
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": f"Category '{category_name}' deleted successfully."})
