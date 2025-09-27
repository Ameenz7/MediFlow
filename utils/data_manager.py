import pandas as pd
import os
from datetime import datetime
import streamlit as st

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.medicines_file = os.path.join(self.data_dir, "medicines.csv")
        self.prescriptions_file = os.path.join(self.data_dir, "prescriptions.csv")
        self.customers_file = os.path.join(self.data_dir, "customers.csv")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize empty CSV files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize CSV files with headers if they don't exist"""
        
        # Medicines CSV structure
        if not os.path.exists(self.medicines_file):
            medicines_columns = [
                'id', 'name', 'category', 'manufacturer', 'supplier', 
                'unit_price', 'stock_quantity', 'reorder_level', 'expiry_date', 
                'description', 'date_added'
            ]
            medicines_df = pd.DataFrame(columns=medicines_columns)
            medicines_df.to_csv(self.medicines_file, index=False)
        
        # Prescriptions CSV structure
        if not os.path.exists(self.prescriptions_file):
            prescriptions_columns = [
                'prescription_id', 'customer_name', 'doctor_name', 'medicine_name',
                'quantity', 'dosage', 'instructions', 'date_prescribed', 'status',
                'total_cost', 'created_at'
            ]
            prescriptions_df = pd.DataFrame(columns=prescriptions_columns)
            prescriptions_df.to_csv(self.prescriptions_file, index=False)
        
        # Customers CSV structure
        if not os.path.exists(self.customers_file):
            customers_columns = [
                'customer_id', 'name', 'date_of_birth', 'gender', 'blood_type',
                'phone', 'email', 'address', 'allergies', 'medical_conditions',
                'emergency_contact_name', 'emergency_contact_phone', 'date_registered'
            ]
            customers_df = pd.DataFrame(columns=customers_columns)
            customers_df.to_csv(self.customers_file, index=False)

        # Refill reminders CSV structure
        self.refill_reminders_file = os.path.join(self.data_dir, "refill_reminders.csv")
        if not os.path.exists(self.refill_reminders_file):
            refill_columns = [
                'reminder_id', 'customer_name', 'medicine_name', 'last_prescription_date',
                'refill_due_date', 'dosage', 'quantity_per_refill', 'reminder_sent',
                'status', 'notes', 'created_at'
            ]
            refill_df = pd.DataFrame(columns=refill_columns)
            refill_df.to_csv(self.refill_reminders_file, index=False)
    
    # Medicine management methods
    def load_medicines(self):
        """Load medicines from CSV file"""
        try:
            return pd.read_csv(self.medicines_file)
        except Exception as e:
            st.error(f"Error loading medicines: {e}")
            return pd.DataFrame()
    
    def add_medicine(self, medicine_data):
        """Add a new medicine to the inventory"""
        try:
            medicines_df = self.load_medicines()
            
            # Check if medicine already exists
            if not medicines_df.empty and medicine_data['name'] in medicines_df['name'].values:
                return False
            
            # Add new medicine
            new_medicine = pd.DataFrame([medicine_data])
            medicines_df = pd.concat([medicines_df, new_medicine], ignore_index=True)
            medicines_df.to_csv(self.medicines_file, index=False)
            return True
        except Exception as e:
            st.error(f"Error adding medicine: {e}")
            return False
    
    def update_medicine_stock(self, medicine_name, new_quantity):
        """Update stock quantity for a medicine"""
        try:
            medicines_df = self.load_medicines()
            if not medicines_df.empty:
                medicines_df.loc[medicines_df['name'] == medicine_name, 'stock_quantity'] = new_quantity
                medicines_df.to_csv(self.medicines_file, index=False)
                return True
            return False
        except Exception as e:
            st.error(f"Error updating medicine stock: {e}")
            return False
    
    def delete_medicine(self, medicine_name):
        """Delete a medicine from inventory"""
        try:
            medicines_df = self.load_medicines()
            if not medicines_df.empty:
                medicines_df = medicines_df[medicines_df['name'] != medicine_name]
                medicines_df.to_csv(self.medicines_file, index=False)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting medicine: {e}")
            return False
    
    # Prescription management methods
    def load_prescriptions(self):
        """Load prescriptions from CSV file"""
        try:
            return pd.read_csv(self.prescriptions_file)
        except Exception as e:
            st.error(f"Error loading prescriptions: {e}")
            return pd.DataFrame()
    
    def add_prescription(self, prescription_data):
        """Add a new prescription"""
        try:
            prescriptions_df = self.load_prescriptions()
            new_prescription = pd.DataFrame([prescription_data])
            prescriptions_df = pd.concat([prescriptions_df, new_prescription], ignore_index=True)
            prescriptions_df.to_csv(self.prescriptions_file, index=False)
            return True
        except Exception as e:
            st.error(f"Error adding prescription: {e}")
            return False
    
    def update_prescription_status(self, prescription_id, new_status):
        """Update prescription status"""
        try:
            prescriptions_df = self.load_prescriptions()
            if not prescriptions_df.empty:
                prescriptions_df.loc[prescriptions_df['prescription_id'] == prescription_id, 'status'] = new_status
                prescriptions_df.to_csv(self.prescriptions_file, index=False)
                return True
            return False
        except Exception as e:
            st.error(f"Error updating prescription status: {e}")
            return False
    
    # Customer management methods
    def load_customers(self):
        """Load customers from CSV file"""
        try:
            return pd.read_csv(self.customers_file)
        except Exception as e:
            st.error(f"Error loading customers: {e}")
            return pd.DataFrame()
    
    def add_customer(self, customer_data):
        """Add a new customer"""
        try:
            customers_df = self.load_customers()
            
            # Check if customer already exists (by name and phone)
            if not customers_df.empty:
                existing = customers_df[
                    (customers_df['name'] == customer_data['name']) &
                    (customers_df['phone'] == customer_data['phone'])
                ]
                if not existing.empty:
                    return False
            
            # Add new customer
            new_customer = pd.DataFrame([customer_data])
            customers_df = pd.concat([customers_df, new_customer], ignore_index=True)
            customers_df.to_csv(self.customers_file, index=False)
            return True
        except Exception as e:
            st.error(f"Error adding customer: {e}")
            return False
    
    def delete_customer(self, customer_id):
        """Delete a customer"""
        try:
            customers_df = self.load_customers()
            if not customers_df.empty:
                customers_df = customers_df[customers_df['customer_id'] != customer_id]
                customers_df.to_csv(self.customers_file, index=False)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting customer: {e}")
            return False
    
    def update_customer(self, customer_id, updated_data):
        """Update customer information"""
        try:
            customers_df = self.load_customers()
            if not customers_df.empty:
                for key, value in updated_data.items():
                    customers_df.loc[customers_df['customer_id'] == customer_id, key] = value
                customers_df.to_csv(self.customers_file, index=False)
                return True
            return False
        except Exception as e:
            st.error(f"Error updating customer: {e}")
            return False
    
    # Utility methods
    def get_low_stock_medicines(self):
        """Get medicines with stock below reorder level"""
        medicines_df = self.load_medicines()
        if not medicines_df.empty:
            return medicines_df[medicines_df['stock_quantity'] <= medicines_df['reorder_level']]
        return pd.DataFrame()
    
    def get_expiring_medicines(self, days=30):
        """Get medicines expiring within specified days"""
        medicines_df = self.load_medicines()
        if not medicines_df.empty:
            medicines_df['expiry_date'] = pd.to_datetime(medicines_df['expiry_date'])
            cutoff_date = pd.Timestamp.now() + pd.Timedelta(days=days)
            return medicines_df[medicines_df['expiry_date'] <= cutoff_date]
        return pd.DataFrame()
    
    def get_customer_prescription_history(self, customer_name):
        """Get prescription history for a specific customer"""
        prescriptions_df = self.load_prescriptions()
        if not prescriptions_df.empty:
            return prescriptions_df[prescriptions_df['customer_name'] == customer_name]
        return pd.DataFrame()
    
    def backup_data(self):
        """Create backup of all data files"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.data_dir, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy all CSV files to backup directory
            for filename in [self.medicines_file, self.prescriptions_file, self.customers_file]:
                if os.path.exists(filename):
                    backup_path = os.path.join(backup_dir, os.path.basename(filename))
                    pd.read_csv(filename).to_csv(backup_path, index=False)
            
            return True
        except Exception as e:
            st.error(f"Error creating backup: {e}")
            return False

    # Refill reminder management methods
    def load_refill_reminders(self):
        """Load refill reminders from CSV file"""
        try:
            return pd.read_csv(self.refill_reminders_file)
        except Exception as e:
            st.error(f"Error loading refill reminders: {e}")
            return pd.DataFrame()

    def add_refill_reminder(self, reminder_data):
        """Add a new refill reminder"""
        try:
            reminders_df = self.load_refill_reminders()
            new_reminder = pd.DataFrame([reminder_data])
            reminders_df = pd.concat([reminders_df, new_reminder], ignore_index=True)
            reminders_df.to_csv(self.refill_reminders_file, index=False)
            return True
        except Exception as e:
            st.error(f"Error adding refill reminder: {e}")
            return False

    def get_due_refills(self, days_ahead=7):
        """Get refill reminders due within specified days"""
        reminders_df = self.load_refill_reminders()
        if not reminders_df.empty:
            reminders_df['refill_due_date'] = pd.to_datetime(reminders_df['refill_due_date'])
            cutoff_date = pd.Timestamp.now() + pd.Timedelta(days=days_ahead)
            due_reminders = reminders_df[reminders_df['refill_due_date'] <= cutoff_date]
            return due_reminders[due_reminders['status'] == 'Active']
        return pd.DataFrame()

    def update_refill_reminder_status(self, reminder_id, new_status):
        """Update refill reminder status"""
        try:
            reminders_df = self.load_refill_reminders()
            if not reminders_df.empty:
                reminders_df.loc[reminders_df['reminder_id'] == reminder_id, 'status'] = new_status
                reminders_df.to_csv(self.refill_reminders_file, index=False)
                return True
            return False
        except Exception as e:
            st.error(f"Error updating refill reminder status: {e}")
            return False

    def mark_reminder_sent(self, reminder_id):
        """Mark a refill reminder as sent"""
        try:
            reminders_df = self.load_refill_reminders()
            if not reminders_df.empty:
                reminders_df.loc[reminders_df['reminder_id'] == reminder_id, 'reminder_sent'] = True
                reminders_df.to_csv(self.refill_reminders_file, index=False)
                return True
            return False
        except Exception as e:
            st.error(f"Error marking reminder as sent: {e}")
            return False
