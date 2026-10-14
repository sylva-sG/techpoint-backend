from datetime import datetime, timezone
from decimal import Decimal
from extensions import db

class Sale(db.Model):
    __tablename__ = "sales"
    __table_args__ = (db.CheckConstraint("total_amount >= 0", name="ck_sales_total_nonnegative"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    payment_method = db.Column(db.String(30), nullable=False, default="cash")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", back_populates="sales")
    items = db.relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "total_amount": str(self.total_amount),
                "payment_method": self.payment_method, "created_at": self.created_at.isoformat(),
                "items": [item.to_dict() for item in self.items]}
