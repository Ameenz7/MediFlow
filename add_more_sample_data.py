#!/usr/bin/env python3
"""
Add More Sample Data to MediFlow Database
This script adds additional medicines, customers, and prescriptions for testing
"""

import pandas as pd
from datetime import datetime, timedelta
import uuid
from utils.database_manager import DatabaseManager

def add_sample_medicines():
    """Add more sample medicines to the database"""
    print("📦 Adding sample medicines...")

    additional_medicines = [
        {
            'id': 'MED006',
            'name': 'Lisinopril',
            'category': 'ACE Inhibitor',
            'manufacturer': 'Pfizer',
            'supplier': 'CardioMed Supplies',
            'unit_price': 25.50,
            'cost_price': 18.75,
            'stock_quantity': 200,
            'reorder_level': 30,
            'expiry_date': '2025-08-15',
            'description': 'ACE inhibitor for hypertension treatment',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'MED007',
            'name': 'Metformin',
            'category': 'Diabetes Medication',
            'manufacturer': 'Bristol Myers',
            'supplier': 'Diabeticare Ltd',
            'unit_price': 18.25,
            'cost_price': 12.50,
            'stock_quantity': 150,
            'reorder_level': 25,
            'expiry_date': '2025-06-30',
            'description': 'First-line treatment for type 2 diabetes',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'MED008',
            'name': 'Simvastatin',
            'category': 'Statin',
            'manufacturer': 'Merck & Co',
            'supplier': 'HealthMart',
            'unit_price': 32.75,
            'cost_price': 24.00,
            'stock_quantity': 180,
            'reorder_level': 35,
            'expiry_date': '2025-09-20',
            'description': 'Cholesterol-lowering medication',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'MED009',
            'name': 'Albuterol',
            'category': 'Bronchodilator',
            'manufacturer': 'GlaxoSmithKline',
            'supplier': 'Respiratory Meds Inc',
            'unit_price': 45.00,
            'cost_price': 35.25,
            'stock_quantity': 75,
            'reorder_level': 20,
            'expiry_date': '2025-04-10',
            'description': 'Rescue inhaler for asthma and COPD',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'MED010',
            'name': 'Prednisone',
            'category': 'Corticosteroid',
            'manufacturer': 'Pfizer',
            'supplier': 'MediSupply Ltd',
            'unit_price': 28.50,
            'cost_price': 20.00,
            'stock_quantity': 90,
            'reorder_level': 15,
            'expiry_date': '2025-07-25',
            'description': 'Anti-inflammatory steroid medication',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'MED011',
            'name': 'Warfarin',
            'category': 'Anticoagulant',
            'manufacturer': 'Bristol Myers',
            'supplier': 'CardioMed Supplies',
            'unit_price': 55.00,
            'cost_price': 42.50,
            'stock_quantity': 60,
            'reorder_level': 12,
            'expiry_date': '2025-05-30',
            'description': 'Blood thinner for clot prevention',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'MED012',
            'name': 'Furosemide',
            'category': 'Diuretic',
            'manufacturer': 'Sanofi',
            'supplier': 'HealthMart',
            'unit_price': 22.25,
            'cost_price': 16.75,
            'stock_quantity': 120,
            'reorder_level': 25,
            'expiry_date': '2025-10-15',
            'description': 'Loop diuretic for heart failure and edema',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'MED013',
            'name': 'Clopidogrel',
            'category': 'Antiplatelet',
            'manufacturer': 'Bristol Myers',
            'supplier': 'CardioMed Supplies',
            'unit_price': 48.75,
            'cost_price': 38.00,
            'stock_quantity': 85,
            'reorder_level': 18,
            'expiry_date': '2025-08-30',
            'description': 'Antiplatelet medication for cardiovascular protection',
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    db_manager = DatabaseManager()
    added_count = 0

    for medicine in additional_medicines:
        try:
            success = db_manager.add_medicine(medicine)
            if success:
                added_count += 1
                print(f"  ✅ Added: {medicine['name']}")
            else:
                print(f"  ⚠️ Skipped: {medicine['name']} (already exists)")
        except Exception as e:
            print(f"  ❌ Error adding {medicine['name']}: {e}")

    print(f"📦 Added {added_count} new medicines to database")
    return added_count

def add_sample_customers():
    """Add more sample customers to the database"""
    print("👥 Adding sample customers...")

    additional_customers = [
        {
            'customer_id': 'CUST004',
            'name': 'Emily Chen',
            'date_of_birth': '1982-05-12',
            'gender': 'Female',
            'blood_type': 'O-',
            'phone': '+1-555-1111',
            'email': 'emily.chen@email.com',
            'address': '321 Pine Street, City, State 12348',
            'allergies': 'Sulfa drugs',
            'medical_conditions': 'Asthma, High Blood Pressure',
            'emergency_contact_name': 'David Chen',
            'emergency_contact_phone': '+1-555-1112',
            'date_registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'customer_id': 'CUST005',
            'name': 'Michael Rodriguez',
            'date_of_birth': '1975-09-28',
            'gender': 'Male',
            'blood_type': 'A+',
            'phone': '+1-555-2222',
            'email': 'michael.rodriguez@email.com',
            'address': '654 Oak Avenue, City, State 12349',
            'allergies': 'Penicillin',
            'medical_conditions': 'Diabetes Type 2, High Cholesterol',
            'emergency_contact_name': 'Maria Rodriguez',
            'emergency_contact_phone': '+1-555-2223',
            'date_registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'customer_id': 'CUST006',
            'name': 'Jessica Taylor',
            'date_of_birth': '1992-12-03',
            'gender': 'Female',
            'blood_type': 'B+',
            'phone': '+1-555-3333',
            'email': 'jessica.taylor@email.com',
            'address': '987 Elm Street, City, State 12350',
            'allergies': '',
            'medical_conditions': 'Migraine Headaches',
            'emergency_contact_name': 'Robert Taylor',
            'emergency_contact_phone': '+1-555-3334',
            'date_registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'customer_id': 'CUST007',
            'name': 'Dr. Amanda Wilson',
            'date_of_birth': '1970-03-20',
            'gender': 'Female',
            'blood_type': 'AB+',
            'phone': '+1-555-4444',
            'email': 'amanda.wilson@email.com',
            'address': '147 Cedar Lane, City, State 12351',
            'allergies': 'Latex',
            'medical_conditions': 'Hypothyroidism',
            'emergency_contact_name': 'Thomas Wilson',
            'emergency_contact_phone': '+1-555-4445',
            'date_registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'customer_id': 'CUST008',
            'name': 'James Brown',
            'date_of_birth': '1965-07-15',
            'gender': 'Male',
            'blood_type': 'O+',
            'phone': '+1-555-5555',
            'email': 'james.brown@email.com',
            'address': '258 Maple Drive, City, State 12352',
            'allergies': 'Aspirin',
            'medical_conditions': 'Arthritis, Heart Disease',
            'emergency_contact_name': 'Susan Brown',
            'emergency_contact_phone': '+1-555-5556',
            'date_registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    db_manager = DatabaseManager()
    added_count = 0

    for customer in additional_customers:
        try:
            success = db_manager.add_customer(customer)
            if success:
                added_count += 1
                print(f"  ✅ Added: {customer['name']}")
            else:
                print(f"  ⚠️ Skipped: {customer['name']} (already exists)")
        except Exception as e:
            print(f"  ❌ Error adding {customer['name']}: {e}")

    print(f"👥 Added {added_count} new customers to database")
    return added_count

def add_sample_prescriptions():
    """Add more sample prescriptions to the database"""
    print("📋 Adding sample prescriptions...")

    # Get available medicines and customers for prescription creation
    db_manager = DatabaseManager()
    medicines = db_manager.load_medicines()
    customers = db_manager.load_customers()

    if medicines.empty or customers.empty:
        print("⚠️ Need medicines and customers in database to create prescriptions")
        return 0

    additional_prescriptions = [
        {
            'prescription_id': 'RX004',
            'customer_name': 'Emily Chen',
            'doctor_name': 'Dr. Sarah Kim',
            'medicine_name': 'Lisinopril',
            'quantity': 90,
            'dosage': '10mg once daily',
            'instructions': 'Take with food in the morning',
            'date_prescribed': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'status': 'Completed',
            'total_cost': 25.50 * 90,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'prescription_id': 'RX005',
            'customer_name': 'Michael Rodriguez',
            'doctor_name': 'Dr. Maria Garcia',
            'medicine_name': 'Metformin',
            'quantity': 180,
            'dosage': '500mg twice daily',
            'instructions': 'Take with meals to reduce stomach upset',
            'date_prescribed': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'status': 'Completed',
            'total_cost': 18.25 * 180,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'prescription_id': 'RX006',
            'customer_name': 'Jessica Taylor',
            'doctor_name': 'Dr. Robert Lee',
            'medicine_name': 'Albuterol',
            'quantity': 2,
            'dosage': '2 puffs as needed',
            'instructions': 'Use for asthma attacks, seek emergency care if no improvement',
            'date_prescribed': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'status': 'Completed',
            'total_cost': 45.00 * 2,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'prescription_id': 'RX007',
            'customer_name': 'Dr. Amanda Wilson',
            'doctor_name': 'Dr. Jennifer Adams',
            'medicine_name': 'Prednisone',
            'quantity': 21,
            'dosage': '20mg daily for 7 days, then taper',
            'instructions': 'Take with food, complete full course',
            'date_prescribed': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'status': 'Pending',
            'total_cost': 28.50 * 21,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'prescription_id': 'RX008',
            'customer_name': 'James Brown',
            'doctor_name': 'Dr. Michael Thompson',
            'medicine_name': 'Warfarin',
            'quantity': 30,
            'dosage': '5mg daily',
            'instructions': 'Regular INR monitoring required, avoid alcohol and certain foods',
            'date_prescribed': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'status': 'Completed',
            'total_cost': 55.00 * 30,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'prescription_id': 'RX009',
            'customer_name': 'Sarah Johnson',
            'doctor_name': 'Dr. Lisa Wong',
            'medicine_name': 'Furosemide',
            'quantity': 60,
            'dosage': '40mg once daily',
            'instructions': 'Take in morning to avoid nighttime urination',
            'date_prescribed': datetime.now().strftime('%Y-%m-%d'),
            'status': 'Pending',
            'total_cost': 22.25 * 60,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'prescription_id': 'RX010',
            'customer_name': 'Robert Davis',
            'doctor_name': 'Dr. David Miller',
            'medicine_name': 'Clopidogrel',
            'quantity': 30,
            'dosage': '75mg once daily',
            'instructions': 'Take at the same time each day, do not stop abruptly',
            'date_prescribed': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'status': 'Completed',
            'total_cost': 48.75 * 30,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    added_count = 0

    for prescription in additional_prescriptions:
        try:
            success = db_manager.add_prescription(prescription)
            if success:
                added_count += 1
                print(f"  ✅ Added prescription: {prescription['prescription_id']} - {prescription['customer_name']}")
            else:
                print(f"  ⚠️ Skipped prescription: {prescription['prescription_id']} (customer/medicine not found)")
        except Exception as e:
            print(f"  ❌ Error adding prescription {prescription['prescription_id']}: {e}")

    print(f"📋 Added {added_count} new prescriptions to database")
    return added_count

def add_sample_refill_reminders():
    """Add sample refill reminders to the database"""
    print("💊 Adding sample refill reminders...")

    # Get available customers and medicines for reminder creation
    db_manager = DatabaseManager()
    customers = db_manager.load_customers()
    medicines = db_manager.load_medicines()

    if customers.empty or medicines.empty:
        print("⚠️ Need customers and medicines in database to create refill reminders")
        return 0

    sample_reminders = [
    {
        'reminder_id': 'RR001',
        'customer_name': 'John Smith',
        'medicine_name': 'Amoxicillin',
        'last_prescription_date': (datetime.now() - timedelta(days=35)).strftime('%Y-%m-%d'),
        'refill_due_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
        'dosage': '500mg three times daily',
        'quantity_per_refill': 30,
        'reminder_sent': False,
        'status': 'Active',
        'notes': 'Patient should complete full course',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'reminder_id': 'RR002',
        'customer_name': 'Sarah Johnson',
        'medicine_name': 'Omeprazole',
        'last_prescription_date': (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d'),
        'refill_due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
        'dosage': '20mg once daily',
        'quantity_per_refill': 30,
        'reminder_sent': False,
        'status': 'Active',
        'notes': 'Take before breakfast for best results',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'reminder_id': 'RR003',
        'customer_name': 'Emily Chen',
        'medicine_name': 'Lisinopril',
        'last_prescription_date': (datetime.now() - timedelta(days=32)).strftime('%Y-%m-%d'),
        'refill_due_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),  # Overdue
        'dosage': '10mg once daily',
        'quantity_per_refill': 30,
        'reminder_sent': True,
        'status': 'Active',
        'notes': 'Monitor blood pressure regularly',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'reminder_id': 'RR004',
        'customer_name': 'Michael Rodriguez',
        'medicine_name': 'Metformin',
        'last_prescription_date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
        'refill_due_date': datetime.now().strftime('%Y-%m-%d'),  # Due today
        'dosage': '500mg twice daily',
        'quantity_per_refill': 60,
        'reminder_sent': False,
        'status': 'Active',
        'notes': 'Check blood sugar levels regularly',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'reminder_id': 'RR005',
        'customer_name': 'Jessica Taylor',
        'medicine_name': 'Albuterol',
        'last_prescription_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
        'refill_due_date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
        'dosage': '2 puffs as needed',
        'quantity_per_refill': 1,
        'reminder_sent': False,
        'status': 'Active',
        'notes': 'Rescue inhaler - monitor usage',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
]


    added_count = 0

    for reminder in sample_reminders:
        try:
            success = db_manager.add_refill_reminder(reminder)
            if success:
                added_count += 1
                print(f"  ✅ Added refill reminder: {reminder['reminder_id']} - {reminder['customer_name']}")
            else:
                print(f"  ⚠️ Skipped refill reminder: {reminder['reminder_id']} (already exists)")
        except Exception as e:
            print(f"  ❌ Error adding refill reminder {reminder['reminder_id']}: {e}")

    # <-- FIX: moved outside of loop
    print(f"💊 Added {added_count} refill reminders to database")
    return added_count

def show_database_stats():
    """Show current database statistics"""
    print("\n📊 Database Statistics:")
    db_manager = DatabaseManager()

    try:
        medicines = db_manager.load_medicines()
        customers = db_manager.load_customers()
        prescriptions = db_manager.load_prescriptions()

        print(f"  💊 Medicines: {len(medicines)}")
        print(f"  👥 Customers: {len(customers)}")
        print(f"  📋 Prescriptions: {len(prescriptions)}")

        if not medicines.empty:
            total_value = (medicines['stock_quantity'] * medicines['unit_price']).sum()
            print(f"  💰 Total Inventory Value: ${total_value:,.2f}")

        if not prescriptions.empty:
            completed_prescriptions = prescriptions[prescriptions['status'] == 'Completed']
            if not completed_prescriptions.empty:
                total_revenue = completed_prescriptions['total_cost'].sum()
                print(f"  💵 Total Revenue: ${total_revenue:,.2f}")

    except Exception as e:
        print(f"  ❌ Error getting statistics: {e}")

def main():
    """Main function to add sample data"""
    print("🏥 MediFlow - Adding Sample Data to Database")
    print("=" * 60)

    try:
        # Add medicines
        medicines_added = add_sample_medicines()

        # Add customers
        customers_added = add_sample_customers()

        # Add prescriptions
        prescriptions_added = add_sample_prescriptions()

        # Add refill reminders
        refill_reminders_added = add_sample_refill_reminders()

        # Show final statistics
        show_database_stats()

        print("\n✅ Sample data addition completed!")
        print(f"📦 Added {medicines_added} medicines")
        print(f"👥 Added {customers_added} customers")
        print(f"📋 Added {prescriptions_added} prescriptions")
        print(f"💊 Added {refill_reminders_added} refill reminders")

        print("\n🎉 Your MediFlow database is now populated with rich sample data!")
        print("You can now run the application to see the enhanced dataset in action.")

        return True

    except Exception as e:
        print(f"\n❌ Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    main()