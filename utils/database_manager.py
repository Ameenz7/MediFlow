import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine

class DatabaseManager:
    def __init__(self):
        # Use the provided database connection string (URL encoded password)
        self.database_url = "postgresql://postgres:Ameen%40db%40@localhost:5432/MediFlowDB"

        # Also check for environment variable as fallback
        env_url = os.getenv('DATABASE_URL')
        if env_url:
            self.database_url = env_url

        # Create SQLAlchemy engine for pandas operations
        self.engine = create_engine(self.database_url)

        # Create tables if they don't exist
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return None

    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Create medicines table
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS medicines (
                        id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(100),
                        manufacturer VARCHAR(255),
                        supplier VARCHAR(255),
                        unit_price DECIMAL(10,2),
                        cost_price DECIMAL(10,2),
                        stock_quantity INTEGER DEFAULT 0,
                        reorder_level INTEGER DEFAULT 10,
                        expiry_date DATE,
                        description TEXT,
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)

                    # Create customers table
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS customers (
                        customer_id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        date_of_birth DATE,
                        gender VARCHAR(50),
                        blood_type VARCHAR(10),
                        phone VARCHAR(50),
                        email VARCHAR(255),
                        address TEXT,
                        allergies TEXT,
                        medical_conditions TEXT,
                        emergency_contact_name VARCHAR(255),
                        emergency_contact_phone VARCHAR(50),
                        date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)

                    # Create prescriptions table
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prescriptions (
                        prescription_id VARCHAR(50) PRIMARY KEY,
                        customer_id VARCHAR(50),
                        customer_name VARCHAR(255) NOT NULL,
                        doctor_name VARCHAR(255) NOT NULL,
                        medicine_id VARCHAR(50),
                        medicine_name VARCHAR(255) NOT NULL,
                        quantity INTEGER NOT NULL,
                        dosage VARCHAR(255),
                        instructions TEXT,
                        date_prescribed DATE NOT NULL,
                        status VARCHAR(50) DEFAULT 'Pending',
                        total_cost DECIMAL(10,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
                    )
                    """)

                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error creating tables: {e}")
            return False
    
    # Medicine management methods
    def load_medicines(self):
        """Load medicines from database"""
        try:
            query = """
            SELECT id, name, category, manufacturer, supplier, unit_price, cost_price,
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
                    INSERT INTO medicines (id, name, category, manufacturer, supplier, unit_price, cost_price,
                                         stock_quantity, reorder_level, expiry_date, description, date_added)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        medicine_data['id'], medicine_data['name'], medicine_data['category'],
                        medicine_data['manufacturer'], medicine_data['supplier'], medicine_data['unit_price'],
                        medicine_data.get('cost_price', 0), medicine_data['stock_quantity'],
                        medicine_data['reorder_level'], medicine_data['expiry_date'],
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

    # Refill reminder management methods
    def load_refill_reminders(self):
        """Load refill reminders from database"""
        try:
            # Create refill_reminders table if it doesn't exist
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS refill_reminders (
                        reminder_id VARCHAR(50) PRIMARY KEY,
                        customer_name VARCHAR(255) NOT NULL,
                        medicine_name VARCHAR(255) NOT NULL,
                        last_prescription_date DATE,
                        refill_due_date DATE NOT NULL,
                        dosage VARCHAR(255),
                        quantity_per_refill INTEGER DEFAULT 30,
                        reminder_sent BOOLEAN DEFAULT FALSE,
                        status VARCHAR(50) DEFAULT 'Active',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
                    conn.commit()

            # Load refill reminders
            query = """
            SELECT reminder_id, customer_name, medicine_name, last_prescription_date,
                   refill_due_date, dosage, quantity_per_refill, reminder_sent, status, notes, created_at
            FROM refill_reminders
            ORDER BY refill_due_date
            """
            return pd.read_sql_query(query, self.engine)
        except Exception as e:
            st.error(f"Error loading refill reminders: {e}")
            return pd.DataFrame()

    def add_refill_reminder(self, reminder_data):
        """Add a new refill reminder"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if reminder already exists
                    cursor.execute("SELECT reminder_id FROM refill_reminders WHERE reminder_id = %s", (reminder_data['reminder_id'],))
                    if cursor.fetchone():
                        return False

                    # Insert new reminder
                    insert_query = """
                    INSERT INTO refill_reminders (reminder_id, customer_name, medicine_name, last_prescription_date,
                                                 refill_due_date, dosage, quantity_per_refill, reminder_sent, status, notes, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        reminder_data['reminder_id'], reminder_data['customer_name'], reminder_data['medicine_name'],
                        reminder_data['last_prescription_date'], reminder_data['refill_due_date'], reminder_data['dosage'],
                        reminder_data['quantity_per_refill'], reminder_data['reminder_sent'], reminder_data['status'],
                        reminder_data['notes'], reminder_data['created_at']
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error adding refill reminder: {e}")
            return False

    def get_due_refills(self, days_ahead=7):
        """Get refill reminders due within specified days"""
        try:
            query = """
            SELECT * FROM refill_reminders
            WHERE refill_due_date <= CURRENT_DATE + %s::interval
            AND status = 'Active'
            ORDER BY refill_due_date
            """
            return pd.read_sql_query(query, self.engine, params=(f"{days_ahead} days",))
        except Exception as e:
            st.error(f"Error getting due refills: {e}")
            return pd.DataFrame()

    def update_refill_reminder_status(self, reminder_id, new_status):
        """Update refill reminder status"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE refill_reminders SET status = %s WHERE reminder_id = %s",
                        (new_status, reminder_id)
                    )
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error updating refill reminder status: {e}")
            return False

    def mark_reminder_sent(self, reminder_id):
        """Mark a refill reminder as sent"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE refill_reminders SET reminder_sent = TRUE WHERE reminder_id = %s",
                        (reminder_id,)
                    )
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error marking reminder as sent: {e}")
            return False