import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create SQLAlchemy engine for pandas operations
        self.engine = create_engine(self.database_url)
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return None
    
    # Medicine management methods
    def load_medicines(self):
        """Load medicines from database"""
        try:
            query = """
            SELECT id, name, category, manufacturer, supplier, unit_price, 
                   stock_quantity, reorder_level, expiry_date, description, date_added
            FROM medicines
            ORDER BY name
            """
            return pd.read_sql_query(query, self.engine)
        except Exception as e:
            st.error(f"Error loading medicines: {e}")
            return pd.DataFrame()
    
    def add_medicine(self, medicine_data):
        """Add a new medicine to the inventory"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if medicine already exists
                    cursor.execute("SELECT id FROM medicines WHERE name = %s", (medicine_data['name'],))
                    if cursor.fetchone():
                        return False
                    
                    # Insert new medicine
                    insert_query = """
                    INSERT INTO medicines (id, name, category, manufacturer, supplier, unit_price, 
                                         stock_quantity, reorder_level, expiry_date, description, date_added)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        medicine_data['id'], medicine_data['name'], medicine_data['category'],
                        medicine_data['manufacturer'], medicine_data['supplier'], medicine_data['unit_price'],
                        medicine_data['stock_quantity'], medicine_data['reorder_level'], medicine_data['expiry_date'],
                        medicine_data['description'], medicine_data['date_added']
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error adding medicine: {e}")
            return False
    
    def update_medicine_stock(self, medicine_name, new_quantity):
        """Update stock quantity for a medicine"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE medicines SET stock_quantity = %s WHERE name = %s",
                        (new_quantity, medicine_name)
                    )
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error updating medicine stock: {e}")
            return False
    
    def delete_medicine(self, medicine_name):
        """Delete a medicine from inventory"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM medicines WHERE name = %s", (medicine_name,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error deleting medicine: {e}")
            return False
    
    # Prescription management methods
    def load_prescriptions(self):
        """Load prescriptions from database"""
        try:
            query = """
            SELECT prescription_id, customer_id, customer_name, doctor_name, 
                   medicine_id, medicine_name, quantity, dosage, instructions,
                   date_prescribed, status, total_cost, created_at
            FROM prescriptions
            ORDER BY created_at DESC
            """
            return pd.read_sql_query(query, self.engine)
        except Exception as e:
            st.error(f"Error loading prescriptions: {e}")
            return pd.DataFrame()
    
    def add_prescription(self, prescription_data):
        """Add a new prescription"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get customer_id and medicine_id
                    cursor.execute("SELECT customer_id FROM customers WHERE name = %s", (prescription_data['customer_name'],))
                    customer_result = cursor.fetchone()
                    if not customer_result:
                        st.error(f"Customer {prescription_data['customer_name']} not found")
                        return False
                    
                    cursor.execute("SELECT id FROM medicines WHERE name = %s", (prescription_data['medicine_name'],))
                    medicine_result = cursor.fetchone()
                    if not medicine_result:
                        st.error(f"Medicine {prescription_data['medicine_name']} not found")
                        return False
                    
                    # Insert prescription
                    insert_query = """
                    INSERT INTO prescriptions (prescription_id, customer_id, customer_name, doctor_name,
                                             medicine_id, medicine_name, quantity, dosage, instructions,
                                             date_prescribed, status, total_cost, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        prescription_data['prescription_id'], customer_result['customer_id'], prescription_data['customer_name'],
                        prescription_data['doctor_name'], medicine_result['id'], prescription_data['medicine_name'],
                        prescription_data['quantity'], prescription_data['dosage'], prescription_data['instructions'],
                        prescription_data['date_prescribed'], prescription_data['status'], prescription_data['total_cost'],
                        prescription_data['created_at']
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error adding prescription: {e}")
            return False
    
    def update_prescription_status(self, prescription_id, new_status):
        """Update prescription status"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE prescriptions SET status = %s WHERE prescription_id = %s",
                        (new_status, prescription_id)
                    )
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error updating prescription status: {e}")
            return False
    
    # Customer management methods
    def load_customers(self):
        """Load customers from database"""
        try:
            query = """
            SELECT customer_id, name, date_of_birth, gender, blood_type, phone, email,
                   address, allergies, medical_conditions, emergency_contact_name,
                   emergency_contact_phone, date_registered
            FROM customers
            ORDER BY name
            """
            return pd.read_sql_query(query, self.engine)
        except Exception as e:
            st.error(f"Error loading customers: {e}")
            return pd.DataFrame()
    
    def add_customer(self, customer_data):
        """Add a new customer"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if customer already exists
                    cursor.execute(
                        "SELECT customer_id FROM customers WHERE name = %s AND phone = %s",
                        (customer_data['name'], customer_data['phone'])
                    )
                    if cursor.fetchone():
                        return False
                    
                    # Insert new customer
                    insert_query = """
                    INSERT INTO customers (customer_id, name, date_of_birth, gender, blood_type,
                                         phone, email, address, allergies, medical_conditions,
                                         emergency_contact_name, emergency_contact_phone, date_registered)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        customer_data['customer_id'], customer_data['name'], customer_data['date_of_birth'],
                        customer_data['gender'], customer_data['blood_type'], customer_data['phone'],
                        customer_data['email'], customer_data['address'], customer_data['allergies'],
                        customer_data['medical_conditions'], customer_data['emergency_contact_name'],
                        customer_data['emergency_contact_phone'], customer_data['date_registered']
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error adding customer: {e}")
            return False
    
    def delete_customer(self, customer_id):
        """Delete a customer"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error deleting customer: {e}")
            return False
    
    def update_customer(self, customer_id, updated_data):
        """Update customer information"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Build dynamic update query
                    set_clauses = []
                    values = []
                    for key, value in updated_data.items():
                        set_clauses.append(f"{key} = %s")
                        values.append(value)
                    
                    if set_clauses:
                        query = f"UPDATE customers SET {', '.join(set_clauses)} WHERE customer_id = %s"
                        values.append(customer_id)
                        cursor.execute(query, values)
                        conn.commit()
                        return cursor.rowcount > 0
            return False
        except Exception as e:
            st.error(f"Error updating customer: {e}")
            return False
    
    # Utility methods
    def get_low_stock_medicines(self):
        """Get medicines with stock below reorder level"""
        try:
            query = "SELECT * FROM medicines WHERE stock_quantity <= reorder_level ORDER BY stock_quantity"
            return pd.read_sql_query(query, self.engine)
        except Exception as e:
            st.error(f"Error getting low stock medicines: {e}")
            return pd.DataFrame()
    
    def get_expiring_medicines(self, days=30):
        """Get medicines expiring within specified days"""
        try:
            query = """
            SELECT * FROM medicines 
            WHERE expiry_date <= CURRENT_DATE + %s::interval
            ORDER BY expiry_date
            """
            return pd.read_sql_query(query, self.engine, params=(f"{days} days",))
        except Exception as e:
            st.error(f"Error getting expiring medicines: {e}")
            return pd.DataFrame()
    
    def get_customer_prescription_history(self, customer_name):
        """Get prescription history for a specific customer"""
        try:
            query = """
            SELECT * FROM prescriptions 
            WHERE customer_name = %s 
            ORDER BY date_prescribed DESC
            """
            return pd.read_sql_query(query, self.engine, params=(customer_name,))
        except Exception as e:
            st.error(f"Error getting customer prescription history: {e}")
            return pd.DataFrame()
    
    def backup_data(self):
        """Create backup of all data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"backup_{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Export all tables to CSV
            tables = ['medicines', 'customers', 'prescriptions']
            
            with self.get_connection() as conn:
                for table in tables:
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    df.to_csv(f"{backup_dir}/{table}.csv", index=False)
            
            return True
        except Exception as e:
            st.error(f"Error creating backup: {e}")
            return False