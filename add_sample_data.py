import pandas as pd
import os
from datetime import datetime, timedelta

# Sample data for medicines
medicines_data = [
    {
        'id': 'MED001',
        'name': 'Paracetamol',
        'category': 'Analgesic',
        'manufacturer': 'PharmaCorp',
        'supplier': 'MediSupply Ltd',
        'unit_price': 5.99,
        'cost_price': 3.50,
        'stock_quantity': 150,
        'reorder_level': 20,
        'expiry_date': '2024-12-31',
        'description': 'Pain relief medication',
        'date_added': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'id': 'MED002',
        'name': 'Amoxicillin',
        'category': 'Antibiotic',
        'manufacturer': 'BioHealth',
        'supplier': 'MediSupply Ltd',
        'unit_price': 12.50,
        'cost_price': 8.75,
        'stock_quantity': 45,
        'reorder_level': 15,
        'expiry_date': '2024-10-15',
        'description': 'Antibiotic for bacterial infections',
        'date_added': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'id': 'MED003',
        'name': 'Ibuprofen',
        'category': 'Anti-inflammatory',
        'manufacturer': 'PharmaCorp',
        'supplier': 'HealthMart',
        'unit_price': 8.75,
        'cost_price': 5.25,
        'stock_quantity': 8,
        'reorder_level': 25,
        'expiry_date': '2024-11-30',
        'description': 'Non-steroidal anti-inflammatory drug',
        'date_added': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'id': 'MED004',
        'name': 'Cetirizine',
        'category': 'Antihistamine',
        'manufacturer': 'AllergyMed',
        'supplier': 'HealthMart',
        'unit_price': 6.25,
        'cost_price': 3.75,
        'stock_quantity': 75,
        'reorder_level': 20,
        'expiry_date': '2025-03-20',
        'description': 'Allergy relief medication',
        'date_added': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'id': 'MED005',
        'name': 'Omeprazole',
        'category': 'Proton Pump Inhibitor',
        'manufacturer': 'DigestHealth',
        'supplier': 'MediSupply Ltd',
        'unit_price': 15.00,
        'cost_price': 10.50,
        'stock_quantity': 30,
        'reorder_level': 10,
        'expiry_date': '2024-09-30',
        'description': 'Acid reflux treatment',
        'date_added': datetime.now().strftime('%Y-%m-%d')
    }
]

# Sample data for customers
customers_data = [
    {
        'customer_id': 'CUST001',
        'name': 'John Smith',
        'date_of_birth': '1985-03-15',
        'gender': 'Male',
        'blood_type': 'O+',
        'phone': '+1-555-0123',
        'email': 'john.smith@email.com',
        'address': '123 Main St, City, State 12345',
        'allergies': 'Penicillin',
        'medical_conditions': 'Hypertension',
        'emergency_contact_name': 'Jane Smith',
        'emergency_contact_phone': '+1-555-0124',
        'date_registered': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'customer_id': 'CUST002',
        'name': 'Sarah Johnson',
        'date_of_birth': '1990-07-22',
        'gender': 'Female',
        'blood_type': 'A+',
        'phone': '+1-555-0456',
        'email': 'sarah.j@email.com',
        'address': '456 Oak Ave, City, State 12346',
        'allergies': 'None',
        'medical_conditions': 'Diabetes',
        'emergency_contact_name': 'Mike Johnson',
        'emergency_contact_phone': '+1-555-0457',
        'date_registered': datetime.now().strftime('%Y-%m-%d')
    },
    {
        'customer_id': 'CUST003',
        'name': 'Robert Davis',
        'date_of_birth': '1978-11-08',
        'gender': 'Male',
        'blood_type': 'B-',
        'phone': '+1-555-0789',
        'email': 'robert.davis@email.com',
        'address': '789 Pine St, City, State 12347',
        'allergies': 'Aspirin',
        'medical_conditions': 'High Cholesterol',
        'emergency_contact_name': 'Lisa Davis',
        'emergency_contact_phone': '+1-555-0790',
        'date_registered': datetime.now().strftime('%Y-%m-%d')
    }
]

# Sample data for prescriptions
prescriptions_data = [
    {
        'prescription_id': 'RX001',
        'customer_name': 'John Smith',
        'doctor_name': 'Dr. Wilson',
        'medicine_name': 'Amoxicillin',
        'quantity': 30,
        'dosage': '500mg',
        'instructions': 'Take 1 tablet 3 times daily with food',
        'date_prescribed': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        'status': 'Filled',
        'total_cost': 375.00,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'prescription_id': 'RX002',
        'customer_name': 'Sarah Johnson',
        'doctor_name': 'Dr. Chen',
        'medicine_name': 'Omeprazole',
        'quantity': 60,
        'dosage': '20mg',
        'instructions': 'Take 1 capsule daily before breakfast',
        'date_prescribed': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        'status': 'Ready for pickup',
        'total_cost': 900.00,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'prescription_id': 'RX003',
        'customer_name': 'Robert Davis',
        'doctor_name': 'Dr. Wilson',
        'medicine_name': 'Cetirizine',
        'quantity': 90,
        'dosage': '10mg',
        'instructions': 'Take 1 tablet daily for allergies',
        'date_prescribed': datetime.now().strftime('%Y-%m-%d'),
        'status': 'Processing',
        'total_cost': 562.50,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
]

# Create DataFrames and save to CSV files
medicines_df = pd.DataFrame(medicines_data)
customers_df = pd.DataFrame(customers_data)
prescriptions_df = pd.DataFrame(prescriptions_data)

# Save to CSV files
medicines_df.to_csv('data/medicines.csv', index=False)
customers_df.to_csv('data/customers.csv', index=False)
prescriptions_df.to_csv('data/prescriptions.csv', index=False)

print("Sample data added successfully!")
print(f"Medicines: {len(medicines_data)} records")
print(f"Customers: {len(customers_data)} records")
print(f"Prescriptions: {len(prescriptions_data)} records")