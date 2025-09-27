import os
import json
import zipfile
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from utils.database_manager import DatabaseManager
import tempfile
import shutil

class BackupManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_full_backup(self, backup_name=None):
        """Create a complete backup of all pharmacy data"""
        try:
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"pharmacy_backup_{timestamp}"
            
            backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            # Create temporary directory for backup files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Export all data to CSV files
                tables = {
                    'medicines': self.db_manager.load_medicines(),
                    'customers': self.db_manager.load_customers(),
                    'prescriptions': self.db_manager.load_prescriptions()
                }
                
                backup_metadata = {
                    'backup_name': backup_name,
                    'created_at': datetime.now().isoformat(),
                    'tables': list(tables.keys()),
                    'record_counts': {}
                }
                
                # Export data to CSV files
                for table_name, data in tables.items():
                    if not data.empty:
                        csv_path = os.path.join(temp_dir, f"{table_name}.csv")
                        data.to_csv(csv_path, index=False)
                        backup_metadata['record_counts'][table_name] = len(data)
                    else:
                        backup_metadata['record_counts'][table_name] = 0
                
                # Create metadata file
                metadata_path = os.path.join(temp_dir, "backup_metadata.json")
                with open(metadata_path, 'w') as f:
                    json.dump(backup_metadata, f, indent=2)
                
                # Create backup report
                report_path = os.path.join(temp_dir, "backup_report.txt")
                self._create_backup_report(backup_metadata, tables, report_path)
                
                # Create ZIP archive
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file)
            
            return backup_path, backup_metadata
            
        except Exception as e:
            st.error(f"Error creating backup: {e}")
            return None, None
    
    def _create_backup_report(self, metadata, tables, report_path):
        """Create a human-readable backup report"""
        try:
            with open(report_path, 'w') as f:
                f.write("PHARMACY MANAGEMENT SYSTEM - BACKUP REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Backup Name: {metadata['backup_name']}\n")
                f.write(f"Created: {metadata['created_at']}\n")
                f.write(f"Tables Included: {len(metadata['tables'])}\n\n")
                
                f.write("DATA SUMMARY:\n")
                f.write("-" * 20 + "\n")
                for table_name, count in metadata['record_counts'].items():
                    f.write(f"{table_name.capitalize()}: {count} records\n")
                
                f.write("\nSYSTEM STATUS AT BACKUP:\n")
                f.write("-" * 30 + "\n")
                
                # Add low stock medicines
                medicines = tables.get('medicines', pd.DataFrame())
                if not medicines.empty:
                    low_stock = medicines[medicines['stock_quantity'] <= medicines['reorder_level']]
                    f.write(f"Low Stock Medicines: {len(low_stock)}\n")
                    if not low_stock.empty:
                        f.write("Low Stock Items:\n")
                        for _, med in low_stock.iterrows():
                            f.write(f"  - {med['name']}: {med['stock_quantity']} units\n")
                
                # Add expiring medicines
                medicines['expiry_date'] = pd.to_datetime(medicines['expiry_date'], errors='coerce')
                expiring = medicines[medicines['expiry_date'] <= datetime.now() + timedelta(days=30)]
                f.write(f"\nMedicines Expiring Soon: {len(expiring)}\n")
                if not expiring.empty:
                    f.write("Expiring Items:\n")
                    for _, med in expiring.iterrows():
                        f.write(f"  - {med['name']}: Expires {med['expiry_date'].strftime('%Y-%m-%d')}\n")
                
                # Add prescription statistics
                prescriptions = tables.get('prescriptions', pd.DataFrame())
                if not prescriptions.empty:
                    status_counts = prescriptions['status'].value_counts()
                    f.write(f"\nPrescription Status:\n")
                    for status, count in status_counts.items():
                        f.write(f"  - {status}: {count}\n")
                
                f.write(f"\nBackup completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
        except Exception as e:
            st.error(f"Error creating backup report: {e}")
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            if os.path.exists(self.backup_dir):
                for filename in os.listdir(self.backup_dir):
                    if filename.endswith('.zip'):
                        filepath = os.path.join(self.backup_dir, filename)
                        stat = os.stat(filepath)
                        backups.append({
                            'name': filename[:-4],  # Remove .zip extension
                            'filename': filename,
                            'path': filepath,
                            'size': stat.st_size,
                            'created': datetime.fromtimestamp(stat.st_mtime)
                        })
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            st.error(f"Error listing backups: {e}")
            return []
    
    def get_backup_info(self, backup_path):
        """Get detailed information about a backup"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if 'backup_metadata.json' in zipf.namelist():
                    with zipf.open('backup_metadata.json') as f:
                        metadata = json.load(f)
                    return metadata
            return None
        except Exception as e:
            st.error(f"Error reading backup info: {e}")
            return None
    
    def export_data_csv(self, table_name=None, date_range=None):
        """Export specific data to CSV format"""
        try:
            if table_name == 'medicines':
                data = self.db_manager.load_medicines()
            elif table_name == 'customers':
                data = self.db_manager.load_customers()
            elif table_name == 'prescriptions':
                data = self.db_manager.load_prescriptions()
                if date_range:
                    data['date_prescribed'] = pd.to_datetime(data['date_prescribed'], errors='coerce')
                    start_date, end_date = date_range
                    data = data[(data['date_prescribed'].dt.date >= start_date) & 
                               (data['date_prescribed'].dt.date <= end_date)]
            else:
                return None
            
            if data.empty:
                return None
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{table_name}_export_{timestamp}.csv"
            
            return data.to_csv(index=False), filename
            
        except Exception as e:
            st.error(f"Error exporting data: {e}")
            return None, None
    
    def create_compliance_report(self, start_date, end_date):
        """Create a compliance report for regulatory purposes"""
        try:
            # Load data for the specified period
            prescriptions = self.db_manager.load_prescriptions()
            medicines = self.db_manager.load_medicines()
            customers = self.db_manager.load_customers()
            
            if not prescriptions.empty:
                prescriptions['date_prescribed'] = pd.to_datetime(prescriptions['date_prescribed'], errors='coerce')
                period_prescriptions = prescriptions[
                    (prescriptions['date_prescribed'].dt.date >= start_date) & 
                    (prescriptions['date_prescribed'].dt.date <= end_date)
                ]
            else:
                period_prescriptions = pd.DataFrame()
            
            # Create compliance report content
            report_content = []
            report_content.append("PHARMACY COMPLIANCE REPORT")
            report_content.append("=" * 50)
            report_content.append(f"Report Period: {start_date} to {end_date}")
            report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append("")
            
            # Prescription Summary
            report_content.append("PRESCRIPTION ACTIVITY SUMMARY")
            report_content.append("-" * 30)
            if not period_prescriptions.empty:
                total_prescriptions = len(period_prescriptions)
                completed_prescriptions = len(period_prescriptions[period_prescriptions['status'] == 'Completed'])
                pending_prescriptions = len(period_prescriptions[period_prescriptions['status'] == 'Pending'])
                cancelled_prescriptions = len(period_prescriptions[period_prescriptions['status'] == 'Cancelled'])
                
                report_content.append(f"Total Prescriptions: {total_prescriptions}")
                report_content.append(f"Completed: {completed_prescriptions}")
                report_content.append(f"Pending: {pending_prescriptions}")
                report_content.append(f"Cancelled: {cancelled_prescriptions}")
                
                # Calculate completion rate
                completion_rate = (completed_prescriptions / total_prescriptions * 100) if total_prescriptions > 0 else 0
                report_content.append(f"Completion Rate: {completion_rate:.1f}%")
            else:
                report_content.append("No prescriptions found for this period")
            
            report_content.append("")
            
            # Inventory Compliance
            report_content.append("INVENTORY COMPLIANCE")
            report_content.append("-" * 20)
            if not medicines.empty:
                total_medicines = len(medicines)
                low_stock = len(medicines[medicines['stock_quantity'] <= medicines['reorder_level']])
                out_of_stock = len(medicines[medicines['stock_quantity'] == 0])
                
                medicines['expiry_date'] = pd.to_datetime(medicines['expiry_date'], errors='coerce')
                expired = len(medicines[medicines['expiry_date'] < datetime.now()])
                expiring_30_days = len(medicines[medicines['expiry_date'] <= datetime.now() + timedelta(days=30)])
                
                report_content.append(f"Total Medicines in Inventory: {total_medicines}")
                report_content.append(f"Low Stock Items: {low_stock}")
                report_content.append(f"Out of Stock Items: {out_of_stock}")
                report_content.append(f"Expired Medicines: {expired}")
                report_content.append(f"Expiring within 30 days: {expiring_30_days}")
                
                # Compliance flags
                if expired > 0:
                    report_content.append("⚠️  COMPLIANCE ALERT: Expired medicines detected")
                if out_of_stock > 0:
                    report_content.append("⚠️  COMPLIANCE ALERT: Out of stock medicines detected")
            
            report_content.append("")
            
            # Customer Activity
            report_content.append("CUSTOMER ACTIVITY")
            report_content.append("-" * 16)
            if not customers.empty:
                total_customers = len(customers)
                if not period_prescriptions.empty:
                    active_customers = len(period_prescriptions['customer_name'].unique())
                else:
                    active_customers = 0
                
                report_content.append(f"Total Registered Customers: {total_customers}")
                report_content.append(f"Active Customers (Period): {active_customers}")
            
            report_content.append("")
            report_content.append("END OF REPORT")
            
            # Create filename and return content
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"compliance_report_{start_date}_{end_date}_{timestamp}.txt"
            
            return "\n".join(report_content), filename
            
        except Exception as e:
            st.error(f"Error creating compliance report: {e}")
            return None, None
    
    def delete_backup(self, backup_path):
        """Delete a backup file"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting backup: {e}")
            return False
    
    def get_backup_storage_info(self):
        """Get information about backup storage usage"""
        try:
            total_size = 0
            backup_count = 0
            
            if os.path.exists(self.backup_dir):
                for filename in os.listdir(self.backup_dir):
                    if filename.endswith('.zip'):
                        filepath = os.path.join(self.backup_dir, filename)
                        total_size += os.path.getsize(filepath)
                        backup_count += 1
            
            return {
                'total_backups': backup_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'backup_directory': self.backup_dir
            }
            
        except Exception as e:
            st.error(f"Error getting storage info: {e}")
            return None