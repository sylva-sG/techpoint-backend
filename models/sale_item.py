from extensions import db

class SaleItem(db.Model):
    __tablename__ = "sale_items"
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="ck_sale_items_quantity_positive"),
        db.CheckConstraint("unit_price >= 0", name="ck_sale_items_price_nonnegative"),
        db.CheckConstraint("subtotal >= 0", name="ck_sale_items_subtotal_nonnegative"),
    )
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    sale = db.relationship("Sale", back_populates="items")
    product = db.relationship("Product", back_populates="sale_items")

    def to_dict(self):
        return {"id": self.id, "sale_id": self.sale_id, "product_id": self.product_id,
                "product_title": self.product.title if self.product else None,
                "quantity": self.quantity, "unit_price": str(self.unit_price), "subtotal": str(self.subtotal)}
