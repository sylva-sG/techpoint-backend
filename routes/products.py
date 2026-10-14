from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from extensions import db
from models import Category, Product

bp = Blueprint("products", __name__, url_prefix="/api/products")


def _json_payload():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None
    return payload


def _unsupported_fields(payload):
    supported = {
        "title",
        "name",
        "brand",
        "description",
        "price",
        "stock_quantity",
        "low_stock_threshold",
        "thumbnail",
        "category_id",
    }
    unsupported = sorted(set(payload) - supported)
    if unsupported:
        return jsonify(
            {"error": f"Unsupported field(s): {', '.join(unsupported)}."}
        ), 400
    return None


def _parse_non_negative_integer(value, field):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a non-negative integer.")
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{field} must be a non-negative integer.") from error
    if parsed < 0 or (isinstance(value, float) and not value.is_integer()):
        raise ValueError(f"{field} must be a non-negative integer.")
    return parsed


def _parse_price(value):
    try:
        price = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError("Price must be a valid number.") from error
    if not price.is_finite():
        raise ValueError("Price must be a valid number.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    return price


def _get_category(category_id):
    if category_id is None:
        return None
    try:
        parsed_id = _parse_non_negative_integer(category_id, "Category ID")
    except ValueError:
        return None
    return db.session.get(Category, parsed_id)


@bp.get("")
def get_products():
    products = Product.query.order_by(Product.title.asc()).all()
    return jsonify([product.to_dict() for product in products])


@bp.get("/<int:product_id>")
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@bp.post("")
def create_product():
    payload = _json_payload()
    if payload is None:
        return jsonify({"error": "A JSON object is required."}), 400
    unsupported_response = _unsupported_fields(payload)
    if unsupported_response:
        return unsupported_response

    title = payload.get("title", payload.get("name"))
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Product title is required."}), 400

    try:
        price = _parse_price(payload.get("price", "0.00"))
        stock_quantity = _parse_non_negative_integer(
            payload.get("stock_quantity", 0), "Stock quantity"
        )
        low_stock_threshold = _parse_non_negative_integer(
            payload.get("low_stock_threshold", 5), "Low-stock threshold"
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    category_id = payload.get("category_id")
    category = _get_category(category_id)
    if category_id is not None and category is None:
        return jsonify({"error": "Invalid category reference."}), 400

    for field in ("brand", "description", "thumbnail"):
        value = payload.get(field)
        if value is not None and not isinstance(value, str):
            label = field.replace("_", " ").capitalize()
            return jsonify({"error": f"{label} must be a string or null."}), 400

    product = Product(
        title=title.strip(),
        brand=payload.get("brand"),
        description=payload.get("description"),
        price=price,
        stock_quantity=stock_quantity,
        low_stock_threshold=low_stock_threshold,
        thumbnail=payload.get("thumbnail"),
        category=category,
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@bp.put("/<int:product_id>")
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    payload = _json_payload()
    if payload is None:
        return jsonify({"error": "A JSON object is required."}), 400
    unsupported_response = _unsupported_fields(payload)
    if unsupported_response:
        return unsupported_response

    if "title" in payload or "name" in payload:
        title = payload.get("title", payload.get("name"))
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "Product title cannot be empty."}), 400
        product.title = title.strip()

    for field in ("brand", "description", "thumbnail"):
        if field in payload:
            value = payload[field]
            if value is not None and not isinstance(value, str):
                label = field.replace("_", " ").capitalize()
                return jsonify(
                    {"error": f"{label} must be a string or null."}
                ), 400
            setattr(product, field, value)

    if "price" in payload:
        try:
            product.price = _parse_price(payload["price"])
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    for field, label in (
        ("stock_quantity", "Stock quantity"),
        ("low_stock_threshold", "Low-stock threshold"),
    ):
        if field in payload:
            try:
                setattr(
                    product,
                    field,
                    _parse_non_negative_integer(payload[field], label),
                )
            except ValueError as error:
                return jsonify({"error": str(error)}), 400

    if "category_id" in payload:
        category_id = payload["category_id"]
        category = _get_category(category_id)
        if category_id is not None and category is None:
            return jsonify({"error": "Invalid category reference."}), 400
        product.category = category

    db.session.commit()
    return jsonify(product.to_dict())
