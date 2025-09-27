import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.backup_manager import BackupManager
from utils.helpers import format_currency
import tempfile
import os
import io

st.markdown('<h1 class="main-header">💾 Backup & Export</h1>', unsafe_allow_html=True)

dm = st.session_state.data_manager
backup_manager = BackupManager(dm)

# Backup and Export tabs
tab1, tab2, tab3, tab4 = st.tabs(["🗄️ Create Backup", "📋 Backup Management", "📤 Data Export", "📊 Compliance Reports"])

with tab1:
    st.subheader("Create System Backup")
    st.write("Create a complete backup of all pharmacy data including medicines, customers, and prescriptions.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        backup_name = st.text_input("Backup Name (Optional)", placeholder="Leave empty for auto-generated name")
        
        if st.button("🗄️ Create Full Backup", type="primary"):
            with st.spinner("Creating backup..."):
                backup_path, metadata = backup_manager.create_full_backup(backup_name)
                
                if backup_path and metadata:
                    st.success("✅ Backup created successfully!")
                    
                    # Display backup details
                    st.markdown("**Backup Details:**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Backup Name", metadata['backup_name'])
                    
                    with col2:
                        total_records = sum(metadata['record_counts'].values())
                        st.metric("Total Records", total_records)
                    
                    with col3:
                        file_size = os.path.getsize(backup_path) / (1024 * 1024)
                        st.metric("File Size", f"{file_size:.2f} MB")
                    
                    # Show record counts
                    st.markdown("**Records Backed Up:**")
                    for table, count in metadata['record_counts'].items():
                        st.write(f"• {table.capitalize()}: {count} records")
                    
                    # Download backup file
                    with open(backup_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Backup File",
                            data=f.read(),
                            file_name=f"{metadata['backup_name']}.zip",
                            mime="application/zip"
                        )
                else:
                    st.error("❌ Failed to create backup")
    
    with col2:
        st.info("**Backup includes:**\n• All medicines data\n• Customer information\n• Prescription records\n• System metadata\n• Backup report")

with tab2:
    st.subheader("Backup Management")
    
    # Get backup storage info
    storage_info = backup_manager.get_backup_storage_info()
    
    if storage_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Backups", storage_info['total_backups'])
        
        with col2:
            st.metric("Storage Used", f"{storage_info['total_size_mb']} MB")
        
        with col3:
            st.metric("Directory", storage_info['backup_directory'])
    
    st.markdown("---")
    
    # List existing backups
    backups = backup_manager.list_backups()
    
    if backups:
        st.subheader("Available Backups")
        
        for backup in backups:
            with st.expander(f"📦 {backup['name']} - {backup['created'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Created:** {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Size:** {backup['size'] / (1024*1024):.2f} MB")
                
                with col2:
                    # Get backup metadata
                    metadata = backup_manager.get_backup_info(backup['path'])
                    if metadata:
                        st.write("**Records:**")
                        for table, count in metadata['record_counts'].items():
                            st.write(f"• {table}: {count}")
                
                with col3:
                    # Download backup
                    with open(backup['path'], "rb") as f:
                        st.download_button(
                            label="📥 Download",
                            data=f.read(),
                            file_name=backup['filename'],
                            mime="application/zip",
                            key=f"download_{backup['name']}"
                        )
                    
                    # Delete backup
                    if st.button("🗑️ Delete", key=f"delete_{backup['name']}"):
                        if st.session_state.get(f'confirm_delete_{backup["name"]}'):
                            if backup_manager.delete_backup(backup['path']):
                                st.success("Backup deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete backup")
                        else:
                            st.session_state[f'confirm_delete_{backup["name"]}'] = True
                            st.warning("Click again to confirm deletion")
    else:
        st.info("No backups found. Create your first backup using the 'Create Backup' tab.")

with tab3:
    st.subheader("Data Export")
    st.write("Export specific data tables for analysis or external use.")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        export_table = st.selectbox("Select Data to Export", [
            "medicines", "customers", "prescriptions"
        ])
    
    with col2:
        export_format = st.selectbox("Export Format", ["CSV"])
    
    # Date range for prescriptions
    if export_table == "prescriptions":
        st.subheader("Date Range (Optional)")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("From Date", value=datetime.now().date() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("To Date", value=datetime.now().date())
        
        use_date_range = st.checkbox("Apply date filter")
        date_range = (start_date, end_date) if use_date_range else None
    else:
        date_range = None
    
    if st.button("📤 Export Data", type="primary"):
        with st.spinner(f"Exporting {export_table} data..."):
            csv_data, filename = backup_manager.export_data_csv(export_table, date_range)
            
            if csv_data and filename:
                st.success("✅ Export completed successfully!")
                
                # Download export (independent of preview)
                st.download_button(
                    label="📥 Download Export",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
                
                # Show preview of exported data
                try:
                    df = pd.read_csv(io.StringIO(csv_data))
                    st.subheader("Data Preview")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    if len(df) > 10:
                        st.info(f"Showing first 10 rows of {len(df)} total records")
                except Exception as e:
                    st.warning(f"Preview unavailable (data exported successfully): {str(e)}")
            else:
                st.error("❌ Failed to export data or no data found")

with tab4:
    st.subheader("Compliance Reports")
    st.write("Generate regulatory compliance reports for pharmacy operations.")
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        report_start = st.date_input("Report Start Date", value=datetime.now().date() - timedelta(days=30))
    
    with col2:
        report_end = st.date_input("Report End Date", value=datetime.now().date())
    
    if st.button("📊 Generate Compliance Report", type="primary"):
        with st.spinner("Generating compliance report..."):
            report_content, filename = backup_manager.create_compliance_report(report_start, report_end)
            
            if report_content and filename:
                st.success("✅ Compliance report generated successfully!")
                
                # Display report preview
                st.subheader("Report Preview")
                st.text_area("Report Content", report_content, height=400)
                
                # Download report
                st.download_button(
                    label="📥 Download Report",
                    data=report_content,
                    file_name=filename,
                    mime="text/plain"
                )
            else:
                st.error("❌ Failed to generate compliance report")
    
    # Compliance quick stats
    st.markdown("---")
    st.subheader("Current Compliance Status")
    
    try:
        # Load current data for compliance check
        medicines = dm.load_medicines()
        prescriptions = dm.load_prescriptions()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if not medicines.empty:
                expired_count = 0
                try:
                    medicines['expiry_date'] = pd.to_datetime(medicines['expiry_date'])
                    expired_count = len(medicines[medicines['expiry_date'] < datetime.now()])
                except:
                    pass
                
                if expired_count > 0:
                    st.metric("Expired Medicines", expired_count, delta="⚠️ Compliance Issue")
                else:
                    st.metric("Expired Medicines", expired_count, delta="✅ Compliant")
        
        with col2:
            if not medicines.empty:
                out_of_stock = len(medicines[medicines['stock_quantity'] == 0])
                if out_of_stock > 0:
                    st.metric("Out of Stock", out_of_stock, delta="⚠️ Monitor")
                else:
                    st.metric("Out of Stock", out_of_stock, delta="✅ Good")
        
        with col3:
            if not prescriptions.empty:
                pending_count = len(prescriptions[prescriptions['status'] == 'Pending'])
                st.metric("Pending Prescriptions", pending_count)
        
        with col4:
            if not prescriptions.empty:
                completion_rate = len(prescriptions[prescriptions['status'] == 'Completed']) / len(prescriptions) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    except Exception as e:
        st.error(f"Error loading compliance data: {e}")

# Footer information
st.markdown("---")
st.markdown("**💡 Backup & Export Guidelines:**")
st.markdown("""
- **Regular Backups**: Create daily backups for data protection
- **Compliance Reports**: Generate monthly reports for regulatory requirements
- **Data Export**: Export data for analysis or migration purposes
- **Storage Management**: Monitor backup storage usage and clean old backups
- **Security**: All exports contain sensitive medical data - handle with care
""")