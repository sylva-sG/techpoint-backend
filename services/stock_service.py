from decimal import Decimal, InvalidOperation

from extensions import db
from models import Product, Restock, StockMovement, User


class ServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


# --------------------------------------------------
# Read-only
# --------------------------------------------------

def get_all_stock():
    products = Product.query.order_by(Product.title.asc()).all()
    return [p.to_dict() for p in products]


def get_low_stock():
    products = (
        Product.query
        .filter(Product.stock_quantity > 0)
        .filter(Product.stock_quantity <= Product.low_stock_threshold)
        .order_by(Product.stock_quantity.asc())
        .all()
    )
    return [p.to_dict() for p in products]


def get_out_of_stock():
    products = (
        Product.query
        .filter(Product.stock_quantity <= 0)
        .order_by(Product.title.asc())
        .all()
    )
    return [p.to_dict() for p in products]


def get_movements():
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).all()
    return [m.to_dict() for m in movements]


def get_movements_for_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        raise ServiceError(f"Product {product_id} not found", 404)
    movements = (
        StockMovement.query
        .filter_by(product_id=product_id)
        .order_by(StockMovement.created_at.desc())
        .all()
    )
    return [m.to_dict() for m in movements]


def list_restocks():
    restocks = Restock.query.order_by(Restock.created_at.desc()).all()
    return [r.to_dict() for r in restocks]


def get_restock_by_id(restock_id):
    restock = db.session.get(Restock, restock_id)
    if not restock:
        raise ServiceError(f"Restock {restock_id} not found", 404)
    return restock.to_dict()


# --------------------------------------------------
# Writes
# --------------------------------------------------

def restock_product(payload):
    product_id = payload.get("product_id")
    quantity = payload.get("quantity")
    user_id = payload.get("user_id")
    unit_cost_raw = payload.get("unit_cost")
    supplier = payload.get("supplier")
    invoice_number = payload.get("invoice_number")
    note = payload.get("note")

    _require_positive_int(product_id, "product_id")
    _require_positive_int(quantity, "quantity")
    _require_positive_int(user_id, "user_id")

    unit_cost = None
    if unit_cost_raw is not None:
        try:
            unit_cost = Decimal(str(unit_cost_raw))
        except (InvalidOperation, ValueError):
            raise ServiceError("unit_cost must be a valid number")
        if unit_cost < 0:
            raise ServiceError("unit_cost cannot be negative")

    product = db.session.get(Product, product_id)
    if not product:
        raise ServiceError(f"Product {product_id} not found", 404)

    user = db.session.get(User, user_id)
    if not user:
        raise ServiceError(f"User {user_id} not found", 404)

    before = product.stock_quantity
    after = before + quantity

    restock = Restock(
        product_id=product.id,
        user_id=user.id,
        quantity=quantity,
        unit_cost=unit_cost,
        supplier=supplier,
        invoice_number=invoice_number,
        note=note,
    )
    db.session.add(restock)
    db.session.flush()

    product.stock_quantity = after

    movement = StockMovement(
        product_id=product.id,
        user_id=user.id,
        movement_type="restock",
        quantity_delta=quantity,
        stock_before=before,
        stock_after=after,
        restock_id=restock.id,
        note=note or f"Linked to restock {restock.invoice_number or restock.id}",
    )
    db.session.add(movement)
    db.session.commit()

    return {
        "restock": restock.to_dict(),
        "product": product.to_dict(),
        "movement": movement.to_dict(),
    }


def adjust_stock(payload):
    product_id = payload.get("product_id")
    delta = payload.get("delta")
    user_id = payload.get("user_id")
    note = payload.get("note")

    _require_positive_int(product_id, "product_id")
    _require_positive_int(user_id, "user_id")
    if not isinstance(delta, int) or delta == 0:
        raise ServiceError("delta must be a non-zero integer")

    product = db.session.get(Product, product_id)
    if not product:
        raise ServiceError(f"Product {product_id} not found", 404)

    user = db.session.get(User, user_id)
    if not user:
        raise ServiceError(f"User {user_id} not found", 404)

    before = product.stock_quantity
    after = before + delta
    if after < 0:
        raise ServiceError(
            f"Adjustment would put stock below zero ({before} -> {after})"
        )

    product.stock_quantity = after

    movement = StockMovement(
        product_id=product.id,
        user_id=user.id,
        movement_type="adjustment",
        quantity_delta=delta,
        stock_before=before,
        stock_after=after,
        note=note or None,
    )
    db.session.add(movement)
    db.session.commit()

    return {"product": product.to_dict(), "movement": movement.to_dict()}


def deduct_stock(product_id, quantity, user_id, sale_id=None, note=None):
    """
    Called internally by the sales service when a sale is completed.
    Does NOT commit — caller is responsible.
    """
    _require_positive_int(quantity, "quantity")
    product = db.session.get(Product, product_id)
    if not product:
        raise ServiceError(f"Product {product_id} not found", 404)

    if product.stock_quantity < quantity:
        raise ServiceError(
            f"Insufficient stock for '{product.title}': "
            f"requested {quantity}, available {product.stock_quantity}"
        )

    before = product.stock_quantity
    product.stock_quantity = before - quantity

    movement = StockMovement(
        product_id=product.id,
        user_id=user_id,
        movement_type="sale",
        quantity_delta=-quantity,
        stock_before=before,
        stock_after=product.stock_quantity,
        note=note or (f"Sale #{sale_id}" if sale_id else None),
    )
    db.session.add(movement)
    return movement


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _require_positive_int(value, field):
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ServiceError(f"{field} must be a positive integer")
