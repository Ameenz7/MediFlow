#!/usr/bin/env python3
"""
Database setup script for MediFlow
Tests database connection and optionally migrates CSV data
"""

import os
import sys
from utils.database_manager import DatabaseManager
from utils.data_manager import DataManager
import pandas as pd

def test_database_connection():
    """Test database connection"""
    try:
        print("🔄 Testing database connection...")
        db_manager = DatabaseManager()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def migrate_csv_data():
    """Migrate existing CSV data to database"""
    try:
        print("🔄 Migrating CSV data to database...")

        # Initialize managers
        db_manager = DatabaseManager()
        csv_manager = DataManager()

        # Migrate medicines first
        medicines = csv_manager.load_medicines()
        if not medicines.empty:
            print(f"📦 Migrating {len(medicines)} medicines...")
            for _, medicine in medicines.iterrows():
                try:
                    medicine_data = {
                        'id': str(medicine['id']),
                        'name': str(medicine['name']),
                        'category': str(medicine['category']) if pd.notna(medicine['category']) else '',
                        'manufacturer': str(medicine['manufacturer']) if pd.notna(medicine['manufacturer']) else '',
                        'supplier': str(medicine['supplier']) if pd.notna(medicine['supplier']) else '',
                        'unit_price': float(medicine['unit_price']) if pd.notna(medicine['unit_price']) else 0,
                        'cost_price': float(medicine['cost_price']) if pd.notna(medicine['cost_price']) else 0,
                        'stock_quantity': int(medicine['stock_quantity']) if pd.notna(medicine['stock_quantity']) else 0,
                        'reorder_level': int(medicine['reorder_level']) if pd.notna(medicine['reorder_level']) else 10,
                        'expiry_date': str(medicine['expiry_date']) if pd.notna(medicine['expiry_date']) else None,
                        'description': str(medicine['description']) if pd.notna(medicine['description']) else '',
                        'date_added': str(medicine['date_added']) if pd.notna(medicine['date_added']) else pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    success = db_manager.add_medicine(medicine_data)
                    if not success:
                        print(f"⚠️ Warning: Could not add medicine {medicine_data['name']} (may already exist)")
                except Exception as e:
                    print(f"⚠️ Warning: Error adding medicine {medicine.get('name', 'Unknown')}: {e}")
            print("✅ Medicines migration completed!")

        # Migrate customers
        customers = csv_manager.load_customers()
        if not customers.empty:
            print(f"👥 Migrating {len(customers)} customers...")
            for _, customer in customers.iterrows():
                try:
                    customer_data = {
                        'customer_id': str(customer['customer_id']),
                        'name': str(customer['name']),
                        'date_of_birth': str(customer['date_of_birth']) if pd.notna(customer['date_of_birth']) else None,
                        'gender': str(customer['gender']) if pd.notna(customer['gender']) else '',
                        'blood_type': str(customer['blood_type']) if pd.notna(customer['blood_type']) else '',
                        'phone': str(customer['phone']) if pd.notna(customer['phone']) else '',
                        'email': str(customer['email']) if pd.notna(customer['email']) else '',
                        'address': str(customer['address']) if pd.notna(customer['address']) else '',
                        'allergies': str(customer['allergies']) if pd.notna(customer['allergies']) else '',
                        'medical_conditions': str(customer['medical_conditions']) if pd.notna(customer['medical_conditions']) else '',
                        'emergency_contact_name': str(customer['emergency_contact_name']) if pd.notna(customer['emergency_contact_name']) else '',
                        'emergency_contact_phone': str(customer['emergency_contact_phone']) if pd.notna(customer['emergency_contact_phone']) else '',
                        'date_registered': str(customer['date_registered']) if pd.notna(customer['date_registered']) else pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    success = db_manager.add_customer(customer_data)
                    if not success:
                        print(f"⚠️ Warning: Could not add customer {customer_data['name']} (may already exist)")
                except Exception as e:
                    print(f"⚠️ Warning: Error adding customer {customer.get('name', 'Unknown')}: {e}")
            print("✅ Customers migration completed!")

        # Migrate prescriptions
        prescriptions = csv_manager.load_prescriptions()
        if not prescriptions.empty:
            print(f"📋 Migrating {len(prescriptions)} prescriptions...")
            for _, prescription in prescriptions.iterrows():
                try:
                    prescription_data = {
                        'prescription_id': str(prescription['prescription_id']),
                        'customer_name': str(prescription['customer_name']),
                        'doctor_name': str(prescription['doctor_name']),
                        'medicine_name': str(prescription['medicine_name']),
                        'quantity': int(prescription['quantity']) if pd.notna(prescription['quantity']) else 1,
                        'dosage': str(prescription['dosage']) if pd.notna(prescription['dosage']) else '',
                        'instructions': str(prescription['instructions']) if pd.notna(prescription['instructions']) else '',
                        'date_prescribed': str(prescription['date_prescribed']) if pd.notna(prescription['date_prescribed']) else pd.Timestamp.now().strftime('%Y-%m-%d'),
                        'status': str(prescription['status']) if pd.notna(prescription['status']) else 'Pending',
                        'total_cost': float(prescription['total_cost']) if pd.notna(prescription['total_cost']) else 0,
                        'created_at': str(prescription['created_at']) if pd.notna(prescription['created_at']) else pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    success = db_manager.add_prescription(prescription_data)
                    if not success:
                        print(f"⚠️ Warning: Could not add prescription {prescription_data['prescription_id']} (customer/medicine not found)")
                except Exception as e:
                    print(f"⚠️ Warning: Error adding prescription {prescription.get('prescription_id', 'Unknown')}: {e}")
            print("✅ Prescriptions migration completed!")

        print("🎉 Data migration completed!")
        return True

    except Exception as e:
        print(f"❌ Data migration failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 MediFlow Database Setup")
    print("=" * 50)

    # Test database connection
    if not test_database_connection():
        print("\n❌ Setup failed! Please check your database connection string.")
        return False

    # Ask user if they want to migrate CSV data
    print("\n📊 Data Migration Options:")
    print("1. Migrate existing CSV data to database")
    print("2. Skip migration (start with empty database)")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        if migrate_csv_data():
            print("\n✅ Database setup completed successfully!")
            print("You can now run your MediFlow application with database support.")
        else:
            print("\n❌ Database setup completed but data migration failed.")
    else:
        print("\n✅ Database setup completed successfully!")
        print("Database is ready with empty tables.")

    return True

if __name__ == "__main__":
    main()