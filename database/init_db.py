"""Initialize database with sample data."""
import sys
import os
from datetime import datetime, timedelta

# Add python_backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
python_backend_path = os.path.join(parent_dir, "python_backend")
sys.path.insert(0, parent_dir)

from python_backend.database.db import init_db, SessionLocal
from python_backend.database.models import (
    User, CardDelivery, Transaction, Bill, Repayment, Collection
)

def create_sample_data():
    """Create sample data for testing."""
    db = SessionLocal()
    
    try:
        # Create sample user
        user = User(
            user_id="USER001",
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            card_number="4532-1234-5678-9010",
            card_status="active",
            credit_limit=50000.0,
            available_credit=35000.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create card delivery
        delivery = CardDelivery(
            user_id="USER001",
            tracking_number="TRACK123456",
            status="delivered",
            address="123 Main St, City, State 12345",
            estimated_delivery=datetime.now() - timedelta(days=5),
            actual_delivery=datetime.now() - timedelta(days=3)
        )
        db.add(delivery)
        
        # Create sample transactions
        transactions = [
            Transaction(
                user_id="USER001",
                transaction_id="TXN001",
                amount=1500.0,
                merchant="Amazon",
                category="shopping",
                date=datetime.now() - timedelta(days=2),
                status="completed",
                is_emi=False
            ),
            Transaction(
                user_id="USER001",
                transaction_id="TXN002",
                amount=25000.0,
                merchant="Electronics Store",
                category="electronics",
                date=datetime.now() - timedelta(days=10),
                status="completed",
                is_emi=True,
                emi_tenure=6,
                emi_amount=4166.67
            ),
            Transaction(
                user_id="USER001",
                transaction_id="TXN003",
                amount=500.0,
                merchant="Restaurant ABC",
                category="dining",
                date=datetime.now() - timedelta(days=1),
                status="completed",
                is_emi=False
            )
        ]
        for txn in transactions:
            db.add(txn)
        
        # Create sample bills
        bill = Bill(
            user_id="USER001",
            bill_id="BILL001",
            bill_date=datetime.now() - timedelta(days=15),
            due_date=datetime.now() + timedelta(days=5),
            total_amount=27000.0,
            minimum_due=2700.0,
            paid_amount=0.0,
            status="pending"
        )
        db.add(bill)
        
        # Create sample repayment
        repayment = Repayment(
            user_id="USER001",
            repayment_id="PAY001",
            amount=5000.0,
            payment_method="bank_transfer",
            status="completed",
            payment_date=datetime.now() - timedelta(days=20),
            bill_id="BILL000"
        )
        db.add(repayment)
        
        # Create collection record (for overdue scenario)
        collection = Collection(
            user_id="USER001",
            overdue_amount=0.0,
            days_overdue=0,
            status="resolved"
        )
        db.add(collection)
        
        db.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✅ Database initialized!")
    
    print("\nCreating sample data...")
    create_sample_data()
    print("\n✅ Database setup complete!")

