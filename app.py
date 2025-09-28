import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from utils.data_manager import DataManager
from utils.helpers import format_currency, get_stock_status_color
from utils.medicine_interactions import check_patient_safety

# Page configuration
st.set_page_config(
    page_title="Pharmacy Management System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data manager
if 'data_manager' not in st.session_state:
    try:
        # Try to use database manager first
        from utils.database_manager import DatabaseManager
        st.session_state.data_manager = DatabaseManager()
        st.session_state.using_database = True
    except Exception as e:
        # Fall back to CSV manager if database fails
        st.session_state.data_manager = DataManager()
        st.session_state.using_database = False

dm = st.session_state.data_manager

# Custom CSS for professional healthcare styling
st.markdown("""
<style>
    .main-header {
        color: #2563EB;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #059669;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2563EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .warning-card {
        background: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-card {
        background: #D1FAE5;
        border-left: 4px solid #059669;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏥 Pharmacy Management")
st.sidebar.markdown("---")

# Navigation
pages = {
    "🏠 Dashboard": "dashboard",
    "💊 Inventory": "inventory",
    "📋 Prescriptions": "prescriptions",
    "👥 Customers": "customers",
    "💊 Refill Reminders": "refill_reminders",
    "📱 Quick Scan": "quick_scan",
    "� Reports": "reports",
    "💾 Backup & Export": "backup_export"
}

selected_page = st.sidebar.selectbox("Navigate to:", list(pages.keys()))

# Main content area
if selected_page == "🏠 Dashboard":
    st.markdown('<h1 class="main-header">Pharmacy Management Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data for dashboard
    medicines = dm.load_medicines()
    prescriptions = dm.load_prescriptions()
    customers = dm.load_customers()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_medicines = len(medicines)
        st.metric("Total Medicines", total_medicines, delta=None)
    
    with col2:
        low_stock_count = len(medicines[medicines['stock_quantity'] <= medicines['reorder_level']])
        st.metric("Low Stock Items", low_stock_count, delta=None)
    
    with col3:
        total_customers = len(customers)
        st.metric("Total Customers", total_customers, delta=None)
    
    with col4:
        if not prescriptions.empty and 'date_prescribed' in prescriptions.columns:
            prescriptions_copy = prescriptions.copy()
            try:
                prescriptions_copy['date_prescribed'] = pd.to_datetime(prescriptions_copy['date_prescribed'], errors='coerce')
                today_prescriptions = len(prescriptions_copy[prescriptions_copy['date_prescribed'].dt.date == pd.Timestamp.now().date()])
            except Exception as e:
                st.error(f"Date parsing error: {e}")
                today_prescriptions = 0
        else:
            today_prescriptions = 0
        st.metric("Today's Prescriptions", today_prescriptions, delta=None)
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Stock Levels Overview")
        if not medicines.empty:
            # Stock status chart
            medicines['stock_status'] = medicines.apply(
                lambda row: 'Low Stock' if row['stock_quantity'] <= row['reorder_level'] 
                else 'Good Stock' if row['stock_quantity'] <= row['reorder_level'] * 2
                else 'High Stock', axis=1
            )
            
            stock_counts = medicines['stock_status'].value_counts()
            fig = px.pie(
                values=stock_counts.values, 
                names=stock_counts.index,
                color_discrete_map={
                    'Low Stock': '#F59E0B',
                    'Good Stock': '#059669', 
                    'High Stock': '#2563EB'
                }
            )
            fig.update_layout(height=300)
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,
                    "responsive": True
                }
            )
        else:
            st.info("No medicine data available")
    
    with col2:
        st.subheader("📅 Prescription Trends")
        if not prescriptions.empty and 'date_prescribed' in prescriptions.columns:
            # Daily prescriptions for last 30 days
            prescriptions_copy = prescriptions.copy()
            try:
                prescriptions_copy['date_prescribed'] = pd.to_datetime(prescriptions_copy['date_prescribed'], errors='coerce')
                last_30_days = datetime.now() - timedelta(days=30)
                recent_prescriptions = prescriptions_copy[prescriptions_copy['date_prescribed'] >= last_30_days]
            
                if not recent_prescriptions.empty:
                    daily_counts = recent_prescriptions.groupby(recent_prescriptions['date_prescribed'].dt.date).size().reset_index()
                    daily_counts.columns = ['date', 'count']
                    
                    fig = px.line(
                        daily_counts, 
                        x='date', 
                        y='count',
                        title="Daily Prescriptions (Last 30 Days)"
                    )
                    fig.update_traces(line_color='#2563EB')
                    fig.update_layout(height=300)
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                            "responsive": True
                        }
                    )
                else:
                    st.info("No prescription data in the last 30 days")
            except Exception as e:
                st.error(f"Error loading prescription trends: {e}")
                st.info("Unable to load prescription trends")
        else:
            st.info("No prescription data available")
    
    # Alerts section
    st.subheader("🚨 Alerts & Notifications")

    # Create tabs for different alert types
    alert_tabs = st.tabs(["💊 Safety Alerts", "📦 Stock Alerts", "⏰ Expiry Alerts", "📊 Summary"])

    with alert_tabs[0]:  # Safety Alerts
        # Medicine Conflict Warnings - Enhanced
        if not prescriptions.empty and not customers.empty:
            with st.container():
                conflict_warnings = []
                high_risk_count = 0
                medium_risk_count = 0

                # Check each completed prescription for potential conflicts
                completed_prescriptions = prescriptions[prescriptions['status'] == 'Completed']

                for customer_name in completed_prescriptions['customer_name'].unique():
                    customer_prescriptions = completed_prescriptions[completed_prescriptions['customer_name'] == customer_name]
                    if len(customer_prescriptions) > 1:
                        # Get customer data
                        customer_data = customers[customers['name'] == customer_name]
                        if not customer_data.empty:
                            customer_info = customer_data.iloc[0]
                            medicines_list = customer_prescriptions['medicine_name'].tolist()

                            # Check for conflicts
                            try:
                                safety_check = check_patient_safety(medicines_list, customer_info.to_dict())
                                if safety_check['warnings']:
                                    warning_item = {
                                        'customer': customer_name,
                                        'medicines': medicines_list,
                                        'warnings': safety_check['warnings'],
                                        'high_risk': safety_check['high_risk_count'] > 0,
                                        'warning_count': len(safety_check['warnings'])
                                    }
                                    conflict_warnings.append(warning_item)

                                    if warning_item['high_risk']:
                                        high_risk_count += 1
                                    else:
                                        medium_risk_count += 1
                            except Exception as e:
                                st.warning(f"Error checking safety for {customer_name}: {e}")

                if conflict_warnings:
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("High Risk", high_risk_count, delta=None)
                    with col2:
                        st.metric("Medium Risk", medium_risk_count, delta=None)
                    with col3:
                        st.metric("Total Alerts", len(conflict_warnings), delta=None)

                    st.markdown("---")

                    # Sort by risk level (high risk first)
                    conflict_warnings.sort(key=lambda x: (not x['high_risk'], x['warning_count']), reverse=True)

                    for warning in conflict_warnings[:5]:  # Show top 5
                        severity_icon = "🔴" if warning['high_risk'] else "🟡"
                        severity_color = "#DC2626" if warning['high_risk'] else "#F59E0B"

                        with st.expander(f"{severity_icon} {warning['customer']} - {warning['warning_count']} conflict(s)"):
                            st.markdown(f"**Medicines:** {', '.join(warning['medicines'])}")
                            st.markdown(f"**Risk Level:** {'High' if warning['high_risk'] else 'Medium'}")

                            for w in warning['warnings'][:3]:  # Show first 3 warnings
                                st.warning(f"⚠️ {w}")

                            if len(warning['warnings']) > 3:
                                st.info(f"...and {len(warning['warnings']) - 3} more warnings")

                    if len(conflict_warnings) > 5:
                        st.info(f"💡 **{len(conflict_warnings) - 5} more patients** have potential conflicts. Check detailed reports for complete list.")
                else:
                    st.success("✅ No medicine conflicts detected!")

    with alert_tabs[1]:  # Stock Alerts
        if not medicines.empty:
            with st.container():
                # Enhanced stock analysis
                low_stock_medicines = medicines[medicines['stock_quantity'] <= medicines['reorder_level']]
                critical_stock = medicines[medicines['stock_quantity'] == 0]
                very_low_stock = medicines[(medicines['stock_quantity'] > 0) & (medicines['stock_quantity'] <= medicines['reorder_level'] * 0.5)]

                if not low_stock_medicines.empty:
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Out of Stock", len(critical_stock), delta=None)
                    with col2:
                        st.metric("Critical Stock", len(very_low_stock), delta=None)
                    with col3:
                        st.metric("Low Stock", len(low_stock_medicines), delta=None)

                    st.markdown("---")

                    # Critical stock (out of stock)
                    if not critical_stock.empty:
                        st.error(f"🚨 **CRITICAL:** {len(critical_stock)} medicines are completely out of stock!")
                        for _, med in critical_stock.iterrows():
                            st.write(f"• **{med['name']}** - OUT OF STOCK (Reorder Level: {med['reorder_level']})")

                    # Very low stock
                    if not very_low_stock.empty:
                        st.warning(f"⚠️ **LOW STOCK:** {len(very_low_stock)} medicines are critically low!")
                        for _, med in very_low_stock.iterrows():
                            urgency = "🔴" if med['stock_quantity'] <= med['reorder_level'] * 0.25 else "🟡"
                            st.write(f"{urgency} **{med['name']}** - Only {med['stock_quantity']} units left (Reorder: {med['reorder_level']})")

                    # Regular low stock
                    regular_low = low_stock_medicines[~low_stock_medicines.index.isin(critical_stock.index) & ~low_stock_medicines.index.isin(very_low_stock.index)]
                    if not regular_low.empty:
                        with st.expander(f"📦 {len(regular_low)} medicines need reordering"):
                            for _, med in regular_low.iterrows():
                                st.write(f"• {med['name']} - {med['stock_quantity']} units (Reorder at {med['reorder_level']})")
                else:
                    st.success("✅ All medicines are adequately stocked!")

    with alert_tabs[2]:  # Expiry Alerts
        if not medicines.empty:
            with st.container():
                # Enhanced expiry analysis with multiple time windows
                medicines['expiry_date'] = pd.to_datetime(medicines['expiry_date'], errors='coerce')

                # Remove medicines without valid expiry dates
                valid_expiry = medicines.dropna(subset=['expiry_date'])

                if not valid_expiry.empty:
                    today = datetime.now()

                    # Different time windows
                    expiring_7_days = valid_expiry[valid_expiry['expiry_date'] <= today + timedelta(days=7)]
                    expiring_30_days = valid_expiry[valid_expiry['expiry_date'] <= today + timedelta(days=30)]
                    expiring_90_days = valid_expiry[valid_expiry['expiry_date'] <= today + timedelta(days=90)]

                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Next 7 Days", len(expiring_7_days), delta=None)
                    with col2:
                        st.metric("Next 30 Days", len(expiring_30_days), delta=None)
                    with col3:
                        st.metric("Next 90 Days", len(expiring_90_days), delta=None)

                    st.markdown("---")

                    # Critical (next 7 days)
                    if not expiring_7_days.empty:
                        st.error(f"🚨 **URGENT:** {len(expiring_7_days)} medicines expire within 7 days!")
                        for _, med in expiring_7_days.iterrows():
                            days_left = (med['expiry_date'] - today).days
                            st.write(f"• **{med['name']}** - Expires in {days_left} days!")

                    # Warning (next 30 days)
                    expiring_30_only = expiring_30_days[~expiring_30_days.index.isin(expiring_7_days.index)]
                    if not expiring_30_only.empty:
                        st.warning(f"⚠️ **ACTION NEEDED:** {len(expiring_30_only)} medicines expire within 30 days!")
                        with st.expander("View medicines expiring in 8-30 days"):
                            for _, med in expiring_30_only.iterrows():
                                days_left = (med['expiry_date'] - today).days
                                st.write(f"• {med['name']} - {days_left} days left")

                    # Info (next 90 days)
                    expiring_90_only = expiring_90_days[~expiring_90_days.index.isin(expiring_30_days.index)]
                    if not expiring_90_only.empty:
                        with st.expander(f"📅 {len(expiring_90_only)} medicines expire within 90 days"):
                            for _, med in expiring_90_only.iterrows():
                                days_left = (med['expiry_date'] - today).days
                                st.write(f"• {med['name']} - {days_left} days left")
                else:
                    st.info("No medicines with valid expiry dates found.")

    with alert_tabs[3]:  # Summary
        with st.container():
            st.subheader("📊 Alert Summary")

            total_alerts = 0
            critical_alerts = 0

            # Count conflicts
            if not prescriptions.empty and not customers.empty:
                completed_prescriptions = prescriptions[prescriptions['status'] == 'Completed']
                for customer_name in completed_prescriptions['customer_name'].unique():
                    customer_prescriptions = completed_prescriptions[completed_prescriptions['customer_name'] == customer_name]
                    if len(customer_prescriptions) > 1:
                        customer_data = customers[customers['name'] == customer_name]
                        if not customer_data.empty:
                            customer_info = customer_data.iloc[0]
                            medicines_list = customer_prescriptions['medicine_name'].tolist()
                            try:
                                safety_check = check_patient_safety(medicines_list, customer_info.to_dict())
                                if safety_check['warnings']:
                                    total_alerts += 1
                                    if safety_check['high_risk_count'] > 0:
                                        critical_alerts += 1
                            except:
                                pass

            # Count stock alerts
            if not medicines.empty:
                critical_stock = len(medicines[medicines['stock_quantity'] == 0])
                very_low_stock = len(medicines[(medicines['stock_quantity'] > 0) & (medicines['stock_quantity'] <= medicines['reorder_level'] * 0.5)])
                total_alerts += critical_stock + very_low_stock

                # Count expiry alerts
                medicines['expiry_date'] = pd.to_datetime(medicines['expiry_date'], errors='coerce')
                expiring_7_days = medicines[medicines['expiry_date'] <= datetime.now() + timedelta(days=7)]
                total_alerts += len(expiring_7_days)
                critical_alerts += len(expiring_7_days)

            # Display summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Alerts", total_alerts, delta=None)
            with col2:
                st.metric("Critical Alerts", critical_alerts, delta=None)
            with col3:
                healthy_score = max(0, 100 - (total_alerts * 5))
                st.metric("System Health", f"{healthy_score}%", delta=None)

            # Health status
            if healthy_score >= 90:
                st.success("✅ System is in excellent health!")
            elif healthy_score >= 70:
                st.warning("⚠️ System needs attention in some areas.")
            else:
                st.error("🚨 System requires immediate attention!")


elif selected_page == "💊 Inventory":
    exec(open('pages/inventory.py', encoding="utf-8").read())
elif selected_page == "📋 Prescriptions":
    exec(open('pages/prescriptions.py', encoding="utf-8").read())
elif selected_page == "👥 Customers":
    exec(open('pages/customers.py', encoding="utf-8").read())
elif selected_page == "💊 Refill Reminders":
    exec(open('pages/refill_reminders.py', encoding="utf-8").read())
elif selected_page == "📱 Quick Scan":
    # Quick scan interface (standalone version)
    import streamlit as st
    from utils.barcode_scanner import BarcodeScanner
    from utils.data_manager import DataManager

    st.markdown('<h1 class="main-header">📱 Quick Scan Entry</h1>', unsafe_allow_html=True)

    # Initialize data manager if not already done
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()

    dm = st.session_state.data_manager
    scanner = BarcodeScanner()

    medicines = dm.load_medicines()
    customers = dm.load_customers()

    if not customers.empty and not medicines.empty:
        from utils.barcode_scanner import create_prescription_from_scan
        prescription_data = create_prescription_from_scan(medicines, customers)

        if prescription_data and st.button("💾 Save to Prescriptions"):
            # Save the scanned prescription
            for item in prescription_data['scanned_items']:
                prescription_item = {
                    'prescription_id': prescription_data['prescription_id'],
                    'customer_name': prescription_data['customer_name'],
                    'doctor_name': prescription_data['doctor_name'],
                    'medicine_name': item['medicine_name'],
                    'quantity': item['quantity'],
                    'dosage': item['dosage'],
                    'instructions': f"Quick scan - {item['dosage']}",
                    'date_prescribed': prescription_data['date_prescribed'],
                    'status': 'Pending',
                    'total_cost': item['total_cost'],
                    'created_at': prescription_data['created_at']
                }
                dm.add_prescription(prescription_item)
                dm.update_medicine_stock(item['medicine_name'], -item['quantity'])

            st.success("✅ Prescription saved successfully!")
            st.rerun()
    else:
        st.warning("⚠️ Please ensure you have both customers and medicines in your system.")

elif selected_page == "� Reports":
    exec(open('pages/reports.py', encoding="utf-8").read())
elif selected_page == "💾 Backup & Export":
    exec(open('pages/backup_export.py', encoding="utf-8").read())

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Pharmacy Management System v1.0**")
st.sidebar.markdown("Built with ❤️ using Streamlit")
