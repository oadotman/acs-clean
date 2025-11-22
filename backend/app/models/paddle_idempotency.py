"""
Paddle Transaction Idempotency Model
Prevents duplicate transactions from multiple button clicks
"""

from sqlalchemy import Column, String, DateTime, Text, Index
from sqlalchemy.sql import func
from app.core.database import Base


class PaddleIdempotencyKey(Base):
    """
    Track used idempotency keys to prevent duplicate Paddle transactions.
    Keys expire after 24 hours.
    """
    __tablename__ = "paddle_idempotency_keys"

    idempotency_key = Column(String(255), primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    transaction_id = Column(String(255), nullable=True)  # Paddle transaction ID
    price_id = Column(String(255), nullable=False)
    response_data = Column(Text, nullable=True)  # JSON response stored
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Index for cleanup queries
    __table_args__ = (
        Index('idx_paddle_idempotency_expires', 'expires_at'),
    )

    def __repr__(self):
        return f"<PaddleIdempotencyKey(key='{self.idempotency_key}', user='{self.user_id}')>"
