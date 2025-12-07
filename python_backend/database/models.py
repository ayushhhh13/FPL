"""Database models for credit card assistant."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User account information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    password_hash = Column(String)  # Hashed password
    card_number = Column(String, unique=True, index=True)
    card_status = Column(String)  # active, blocked, expired
    credit_limit = Column(Float)
    available_credit = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    bills = relationship("Bill", back_populates="user")
    repayments = relationship("Repayment", back_populates="user")


class CardDelivery(Base):
    """Card delivery tracking information."""
    __tablename__ = "card_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    tracking_number = Column(String, unique=True)
    status = Column(String)  # processing, shipped, in_transit, delivered
    address = Column(Text)
    estimated_delivery = Column(DateTime)
    actual_delivery = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    """Transaction records."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    transaction_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    merchant = Column(String)
    category = Column(String)  # groceries, dining, travel, etc.
    date = Column(DateTime)
    status = Column(String)  # pending, completed, failed, refunded
    is_emi = Column(Boolean, default=False)
    emi_tenure = Column(Integer, nullable=True)  # months
    emi_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class Bill(Base):
    """Bill and statement records."""
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    bill_id = Column(String, unique=True, index=True)
    bill_date = Column(DateTime)
    due_date = Column(DateTime)
    total_amount = Column(Float)
    minimum_due = Column(Float)
    paid_amount = Column(Float, default=0.0)
    status = Column(String)  # pending, paid, overdue
    statement_pdf_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bills")


class Repayment(Base):
    """Repayment records."""
    __tablename__ = "repayments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    repayment_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    payment_method = Column(String)  # bank_transfer, upi, debit_card
    status = Column(String)  # pending, processing, completed, failed
    payment_date = Column(DateTime)
    bill_id = Column(String, ForeignKey("bills.bill_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="repayments")


class Collection(Base):
    """Collections information for overdue accounts."""
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    overdue_amount = Column(Float)
    days_overdue = Column(Integer)
    last_contact_date = Column(DateTime, nullable=True)
    payment_plan_offered = Column(Boolean, default=False)
    status = Column(String)  # active, resolved, escalated
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

