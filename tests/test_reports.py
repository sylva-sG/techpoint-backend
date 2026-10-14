from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app import create_app
from config import TestConfig
from extensions import db
from models import User, Product, Sale, SaleItem


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        manager = User(
            username="manager",
            name="Test Manager",
            role="manager",
        )
        manager.set_password("Manager123!")

        cashier = User(
            username="cashier",
            name="Test Cashier",
            role="cashier",
        )
        cashier.set_password("Cashier123!")

        db.session.add_all([manager, cashier])
        db.session.flush()

        keyboard = Product(
            title="Keyboard",
            price=Decimal("50.00"),
            stock_quantity=2,
            low_stock_threshold=5,
        )

        mouse = Product(
            title="Mouse",
            price=Decimal("25.00"),
            stock_quantity=20,
            low_stock_threshold=5,
        )

        db.session.add_all([keyboard, mouse])
        db.session.flush()

        sale = Sale(
            user_id=cashier.id,
            total_amount=Decimal("175.00"),
            payment_method="cash",
            created_at=datetime(
                2026, 10, 14, 12, 0, tzinfo=timezone.utc
            ),
        )
        db.session.add(sale)
        db.session.flush()

        db.session.add_all([
            SaleItem(
                sale_id=sale.id,
                product_id=keyboard.id,
                quantity=2,
                unit_price=Decimal("50.00"),
                subtotal=Decimal("100.00"),
            ),
            SaleItem(
                sale_id=sale.id,
                product_id=mouse.id,
                quantity=3,
                unit_price=Decimal("25.00"),
                subtotal=Decimal("75.00"),
            ),
        ])

        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def manager_headers(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "manager",
            "password": "Manager123!",
        },
    )
    assert response.status_code == 200

    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def cashier_headers(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "cashier",
            "password": "Cashier123!",
        },
    )
    assert response.status_code == 200

    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_reports_require_authentication(client):
    response = client.get("/api/reports/summary")

    assert response.status_code == 401


def test_cashier_cannot_access_manager_reports(client):
    headers = cashier_headers(client)

    response = client.get(
        "/api/reports/summary",
        headers=headers,
    )

    assert response.status_code == 403


def test_sales_summary(client):
    headers = manager_headers(client)

    response = client.get(
        "/api/reports/summary",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["total_revenue"] == "175.00"
    assert data["transaction_count"] == 1


def test_sales_by_cashier(client):
    headers = manager_headers(client)

    response = client.get(
        "/api/reports/sales-by-cashier",
        headers=headers,
    )

    assert response.status_code == 200
    results = response.get_json()["results"]

    assert len(results) == 1
    assert results[0]["username"] == "cashier"
    assert results[0]["total_revenue"] == "175.00"
    assert results[0]["transaction_count"] == 1


def test_sales_by_date(client):
    headers = manager_headers(client)

    response = client.get(
        "/api/reports/sales-by-date?start_date=2026-10-14&end_date=2026-10-14",
        headers=headers,
    )

    assert response.status_code == 200
    results = response.get_json()["results"]

    assert len(results) == 1
    assert results[0]["date"] == "2026-10-14"
    assert results[0]["total_revenue"] == "175.00"


def test_best_selling_products(client):
    headers = manager_headers(client)

    response = client.get(
        "/api/reports/best-selling-products",
        headers=headers,
    )

    assert response.status_code == 200
    results = response.get_json()["results"]

    assert results[0]["product_title"] == "Mouse"
    assert results[0]["quantity_sold"] == 3
    assert results[1]["product_title"] == "Keyboard"
    assert results[1]["quantity_sold"] == 2


def test_dashboard_summary(client):
    headers = manager_headers(client)

    response = client.get(
        "/api/reports/dashboard",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["total_revenue"] == "175.00"
    assert data["transaction_count"] == 1
    assert data["product_count"] == 2
    assert data["cashier_count"] == 1
    assert data["low_stock_count"] == 1
    assert data["low_stock_products"][0]["title"] == "Keyboard"


def test_invalid_date_format_returns_400(client):
    headers = manager_headers(client)

    response = client.get(
        "/api/reports/summary?start_date=not-a-date",
        headers=headers,
    )

    assert response.status_code == 400


def test_start_date_after_end_date_returns_400(client):
    headers = manager_headers(client)

    response = client.get(
        "/api/reports/summary?start_date=2026-10-15&end_date=2026-10-14",
        headers=headers,
    )

    assert response.status_code == 400