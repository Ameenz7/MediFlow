import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from utils.database_manager import DatabaseManager
from utils.helpers import format_currency, get_stock_status_color

# Page configuration
st.set_page_config(
    page_title="Pharmacy Management System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database manager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DatabaseManager()

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
    "📊 Reports": "reports"
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
                today_prescriptions = len(prescriptions_copy[prescriptions_copy['date_prescribed'].dt.date == datetime.now().date()])
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
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No medicine data available")
    
    with col2:
        st.subheader("📅 Prescription Trends")
        if not prescriptions.empty:
            # Daily prescriptions for last 30 days
            prescriptions_copy = prescriptions.copy()
            prescriptions_copy['date_prescribed'] = pd.to_datetime(prescriptions_copy['date_prescribed'])
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
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No prescription data in the last 30 days")
        else:
            st.info("No prescription data available")
    
    # Alerts section
    st.subheader("🚨 Alerts & Notifications")
    
    # Low stock alerts
    if not medicines.empty:
        low_stock_medicines = medicines[medicines['stock_quantity'] <= medicines['reorder_level']]
        if not low_stock_medicines.empty:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⚠️ {len(low_stock_medicines)} medicines are running low on stock!")
            for _, med in low_stock_medicines.head(3).iterrows():
                st.write(f"• {med['name']} - Only {med['stock_quantity']} units left")
            if len(low_stock_medicines) > 3:
                st.write(f"...and {len(low_stock_medicines) - 3} more")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Expiring medicines
    if not medicines.empty:
        medicines['expiry_date'] = pd.to_datetime(medicines['expiry_date'])
        expiring_soon = medicines[medicines['expiry_date'] <= datetime.now() + timedelta(days=30)]
        if not expiring_soon.empty:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⏰ {len(expiring_soon)} medicines expire within 30 days!")
            for _, med in expiring_soon.head(3).iterrows():
                days_left = (med['expiry_date'] - datetime.now()).days
                st.write(f"• {med['name']} - Expires in {days_left} days")
            if len(expiring_soon) > 3:
                st.write(f"...and {len(expiring_soon) - 3} more")
            st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "💊 Inventory":
    exec(open('pages/inventory.py').read())
elif selected_page == "📋 Prescriptions":
    exec(open('pages/prescriptions.py').read())
elif selected_page == "👥 Customers":
    exec(open('pages/customers.py').read())
elif selected_page == "📊 Reports":
    exec(open('pages/reports.py').read())

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Pharmacy Management System v1.0**")
st.sidebar.markdown("Built with ❤️ using Streamlit")
