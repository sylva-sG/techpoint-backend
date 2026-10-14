from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from extensions import db
from models import Product, Sale, SaleItem, User
from utils.auth import manager_required

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def filtered_sales_query():
    query = Sale.query

    try:
        start_text = request.args.get("start_date")
        end_text = request.args.get("end_date")
        start_date = date.fromisoformat(start_text) if start_text else None
        end_date = date.fromisoformat(end_text) if end_text else None
    except ValueError:
        return None, (
            jsonify(status="error", message="Dates must use YYYY-MM-DD format"),
            400,
        )

    if start_date and end_date and start_date > end_date:
        return None, (
            jsonify(status="error", message="start_date cannot be after end_date"),
            400,
        )

    if start_date:
        query = query.filter(
            Sale.created_at
            >= datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        )

    if end_date:
        query = query.filter(
            Sale.created_at
            < datetime.combine(
                end_date + timedelta(days=1),
                time.min,
                tzinfo=timezone.utc,
            )
        )

    return query, None


def money(value):
    return str(Decimal(str(value)))


@bp.get("/summary")
@manager_required
def sales_summary():
    query, error = filtered_sales_query()
    if error:
        return error

    revenue, count = query.with_entities(
        func.coalesce(func.sum(Sale.total_amount), 0),
        func.count(Sale.id),
    ).one()

    return jsonify(
        status="success",
        total_revenue=money(revenue),
        transaction_count=int(count),
    ), 200


@bp.get("/sales-by-cashier")
@manager_required
def sales_by_cashier():
    query, error = filtered_sales_query()
    if error:
        return error

    rows = query.join(User, User.id == Sale.user_id).with_entities(
        User.id.label("user_id"),
        User.username,
        User.name,
        func.sum(Sale.total_amount).label("total_revenue"),
        func.count(Sale.id).label("transaction_count"),
    ).group_by(
        User.id, User.username, User.name
    ).order_by(func.sum(Sale.total_amount).desc()).all()

    return jsonify(status="success", results=[
        {
            "user_id": row.user_id,
            "username": row.username,
            "name": row.name,
            "total_revenue": money(row.total_revenue),
            "transaction_count": int(row.transaction_count),
        }
        for row in rows
    ]), 200


@bp.get("/sales-by-date")
@manager_required
def sales_by_date():
    query, error = filtered_sales_query()
    if error:
        return error

    rows = query.with_entities(
        func.date(Sale.created_at).label("sale_date"),
        func.sum(Sale.total_amount).label("total_revenue"),
        func.count(Sale.id).label("transaction_count"),
    ).group_by(
        func.date(Sale.created_at)
    ).order_by(func.date(Sale.created_at).asc()).all()

    return jsonify(status="success", results=[
        {
            "date": str(row.sale_date),
            "total_revenue": money(row.total_revenue),
            "transaction_count": int(row.transaction_count),
        }
        for row in rows
    ]), 200


@bp.get("/best-selling-products")
@manager_required
def best_selling_products():
    query, error = filtered_sales_query()
    if error:
        return error

    rows = query.join(
        SaleItem, SaleItem.sale_id == Sale.id
    ).join(
        Product, Product.id == SaleItem.product_id
    ).with_entities(
        Product.id.label("product_id"),
        Product.title.label("product_title"),
        func.sum(SaleItem.quantity).label("quantity_sold"),
        func.sum(SaleItem.subtotal).label("total_revenue"),
    ).group_by(
        Product.id, Product.title
    ).order_by(
        func.sum(SaleItem.quantity).desc(),
        Product.title.asc(),
    ).all()

    return jsonify(status="success", results=[
        {
            "product_id": row.product_id,
            "product_title": row.product_title,
            "quantity_sold": int(row.quantity_sold),
            "total_revenue": money(row.total_revenue),
        }
        for row in rows
    ]), 200


@bp.get("/dashboard")
@manager_required
def dashboard_summary():
    query, error = filtered_sales_query()
    if error:
        return error

    revenue, count = query.with_entities(
        func.coalesce(func.sum(Sale.total_amount), 0),
        func.count(Sale.id),
    ).one()

    low_stock = Product.query.filter(
        Product.stock_quantity <= Product.low_stock_threshold
    ).order_by(
        Product.stock_quantity.asc(),
        Product.title.asc(),
    ).all()

    return jsonify(
        status="success",
        total_revenue=money(revenue),
        transaction_count=int(count),
        product_count=Product.query.count(),
        low_stock_count=len(low_stock),
        low_stock_products=[
            {
                "id": product.id,
                "title": product.title,
                "stock_quantity": product.stock_quantity,
                "low_stock_threshold": product.low_stock_threshold,
            }
            for product in low_stock
        ],
        cashier_count=User.query.filter_by(role="cashier").count(),
    ), 200
