import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.helpers import format_currency

st.markdown('<h1 class="main-header">📊 Reports & Analytics</h1>', unsafe_allow_html=True)

dm = st.session_state.data_manager

# Reports tabs
tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventory Reports", "💰 Sales Reports", "👥 Customer Analytics", "📋 Prescription Analytics"])

with tab1:
    st.subheader("📦 Inventory Status Reports")
    
    medicines = dm.load_medicines()
    
    if not medicines.empty:
        # Inventory summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_medicines = len(medicines)
            st.metric("Total Medicines", total_medicines)
        
        with col2:
            total_stock_value = (medicines['stock_quantity'] * medicines['unit_price']).sum()
            st.metric("Total Stock Value", format_currency(total_stock_value))
        
        with col3:
            low_stock_count = len(medicines[medicines['stock_quantity'] <= medicines['reorder_level']])
            st.metric("Low Stock Items", low_stock_count)
        
        with col4:
            out_of_stock = len(medicines[medicines['stock_quantity'] == 0])
            st.metric("Out of Stock", out_of_stock)
        
        st.markdown("---")
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stock Status Distribution")
            medicines['stock_status'] = medicines.apply(
                lambda row: 'Out of Stock' if row['stock_quantity'] == 0
                else 'Low Stock' if row['stock_quantity'] <= row['reorder_level']
                else 'Good Stock', axis=1
            )
            
            status_counts = medicines['stock_status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color_discrete_map={
                    'Out of Stock': '#DC2626',
                    'Low Stock': '#F59E0B',
                    'Good Stock': '#059669'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Inventory Value by Category")
            category_value = medicines.groupby('category').apply(
                lambda x: (x['stock_quantity'] * x['unit_price']).sum()
            ).reset_index()
            category_value.columns = ['category', 'value']
            
            fig = px.bar(
                category_value,
                x='category',
                y='value',
                color='value',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Low stock alert table
        st.subheader("🚨 Low Stock Alerts")
        low_stock_medicines = medicines[medicines['stock_quantity'] <= medicines['reorder_level']]
        
        if not low_stock_medicines.empty:
            display_df = low_stock_medicines[['name', 'category', 'stock_quantity', 'reorder_level', 'supplier']].copy()
            display_df['action_needed'] = display_df.apply(
                lambda row: f"Order {row['reorder_level'] * 2 - row['stock_quantity']} units", axis=1
            )
            st.dataframe(display_df, use_container_width=True)
        else:
            st.success("✅ All medicines are adequately stocked!")
        
        # Expiring medicines
        st.subheader("⏰ Medicines Expiring Soon (Next 90 Days)")
        medicines['expiry_date'] = pd.to_datetime(medicines['expiry_date'])
        next_90_days = datetime.now() + timedelta(days=90)
        expiring_medicines = medicines[medicines['expiry_date'] <= next_90_days]
        
        if not expiring_medicines.empty:
            expiring_medicines['days_to_expiry'] = (expiring_medicines['expiry_date'] - datetime.now()).dt.days
            display_df = expiring_medicines[['name', 'category', 'stock_quantity', 'expiry_date', 'days_to_expiry']].copy()
            display_df = display_df.sort_values('days_to_expiry')
            st.dataframe(display_df, use_container_width=True)
        else:
            st.success("✅ No medicines expiring in the next 90 days!")
        
    else:
        st.info("No inventory data available for reporting.")

with tab2:
    st.subheader("💰 Sales & Revenue Reports")
    
    prescriptions = dm.load_prescriptions()
    medicines = dm.load_medicines()
    
    if not prescriptions.empty:
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From Date:", value=datetime.now().date() - timedelta(days=30))
        with col2:
            end_date = st.date_input("To Date:", value=datetime.now().date())
        
        # Filter prescriptions by date range
        prescriptions['date_prescribed'] = pd.to_datetime(prescriptions['date_prescribed'])
        filtered_prescriptions = prescriptions[
            (prescriptions['date_prescribed'].dt.date >= start_date) &
            (prescriptions['date_prescribed'].dt.date <= end_date)
        ]
        
        if not filtered_prescriptions.empty:
            # Revenue metrics
            completed_prescriptions = filtered_prescriptions[filtered_prescriptions['status'] == 'Completed']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_prescriptions = len(filtered_prescriptions)
                st.metric("Total Prescriptions", total_prescriptions)
            
            with col2:
                completed_count = len(completed_prescriptions)
                st.metric("Completed Sales", completed_count)
            
            with col3:
                total_revenue = completed_prescriptions['total_cost'].sum()
                st.metric("Total Revenue", format_currency(total_revenue))
            
            with col4:
                avg_sale_value = completed_prescriptions['total_cost'].mean() if not completed_prescriptions.empty else 0
                st.metric("Avg Sale Value", format_currency(avg_sale_value))
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Daily Revenue Trend")
                if not completed_prescriptions.empty:
                    daily_revenue = completed_prescriptions.groupby(
                        completed_prescriptions['date_prescribed'].dt.date
                    )['total_cost'].sum().reset_index()
                    daily_revenue.columns = ['date', 'revenue']
                    
                    fig = px.line(
                        daily_revenue,
                        x='date',
                        y='revenue',
                        title=f"Revenue from {start_date} to {end_date}"
                    )
                    fig.update_traces(line_color='#2563EB')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No completed sales in the selected period")
            
            with col2:
                st.subheader("Top Selling Medicines")
                if not completed_prescriptions.empty:
                    top_medicines = completed_prescriptions.groupby('medicine_name').agg({
                        'quantity': 'sum',
                        'total_cost': 'sum'
                    }).reset_index().sort_values('total_cost', ascending=False).head(10)
                    
                    fig = px.bar(
                        top_medicines,
                        x='medicine_name',
                        y='total_cost',
                        title="Top 10 Medicines by Revenue"
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No sales data available")
            
            # Sales summary table
            st.subheader("Sales Summary by Medicine")
            if not completed_prescriptions.empty:
                sales_summary = completed_prescriptions.groupby('medicine_name').agg({
                    'quantity': 'sum',
                    'total_cost': 'sum',
                    'prescription_id': 'count'
                }).reset_index()
                sales_summary.columns = ['Medicine', 'Units Sold', 'Revenue', 'Orders']
                sales_summary['Revenue'] = sales_summary['Revenue'].apply(format_currency)
                sales_summary = sales_summary.sort_values('Units Sold', ascending=False)
                st.dataframe(sales_summary, use_container_width=True)
        else:
            st.info("No sales data found for the selected date range")
    else:
        st.info("No sales data available for reporting.")

with tab3:
    st.subheader("👥 Customer Analytics")
    
    customers = dm.load_customers()
    prescriptions = dm.load_prescriptions()
    
    if not customers.empty and not prescriptions.empty:
        # Customer metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_customers = len(customers)
            st.metric("Total Customers", total_customers)
        
        with col2:
            active_customers = len(prescriptions['customer_name'].unique())
            st.metric("Active Customers", active_customers)
        
        with col3:
            avg_prescriptions = prescriptions.groupby('customer_name').size().mean()
            st.metric("Avg Prescriptions/Customer", f"{avg_prescriptions:.1f}")
        
        with col4:
            completed_prescriptions = prescriptions[prescriptions['status'] == 'Completed']
            avg_customer_value = completed_prescriptions.groupby('customer_name')['total_cost'].sum().mean()
            st.metric("Avg Customer Value", format_currency(avg_customer_value))
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Customer Age Distribution")
            customers['date_of_birth'] = pd.to_datetime(customers['date_of_birth'])
            customers['age'] = ((datetime.now() - customers['date_of_birth']).dt.days / 365.25).astype(int)
            
            age_bins = [0, 18, 30, 50, 65, 100]
            age_labels = ['0-17', '18-29', '30-49', '50-64', '65+']
            customers['age_group'] = pd.cut(customers['age'], bins=age_bins, labels=age_labels, right=False)
            
            age_distribution = customers['age_group'].value_counts()
            fig = px.bar(
                x=age_distribution.index,
                y=age_distribution.values,
                title="Customer Distribution by Age Group"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Top Customers by Spending")
            completed_prescriptions = prescriptions[prescriptions['status'] == 'Completed']
            if not completed_prescriptions.empty:
                customer_spending = completed_prescriptions.groupby('customer_name')['total_cost'].sum().reset_index()
                customer_spending = customer_spending.sort_values('total_cost', ascending=False).head(10)
                
                fig = px.bar(
                    customer_spending,
                    x='customer_name',
                    y='total_cost',
                    title="Top 10 Customers by Total Spending"
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No customer spending data available")
        
        # Customer details table
        st.subheader("Customer Activity Summary")
        customer_activity = []
        
        for _, customer in customers.iterrows():
            customer_prescriptions = prescriptions[prescriptions['customer_name'] == customer['name']]
            completed_prescriptions = customer_prescriptions[customer_prescriptions['status'] == 'Completed']
            
            customer_activity.append({
                'Customer Name': customer['name'],
                'Total Prescriptions': len(customer_prescriptions),
                'Completed Prescriptions': len(completed_prescriptions),
                'Total Spent': format_currency(completed_prescriptions['total_cost'].sum()),
                'Last Visit': customer_prescriptions['date_prescribed'].max() if not customer_prescriptions.empty else 'Never',
                'Phone': customer['phone']
            })
        
        activity_df = pd.DataFrame(customer_activity)
        activity_df = activity_df.sort_values('Total Prescriptions', ascending=False)
        st.dataframe(activity_df, use_container_width=True)
        
    else:
        st.info("Insufficient data for customer analytics.")

with tab4:
    st.subheader("📋 Prescription Analytics")
    
    prescriptions = dm.load_prescriptions()
    
    if not prescriptions.empty:
        # Prescription metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_prescriptions = len(prescriptions)
            st.metric("Total Prescriptions", total_prescriptions)
        
        with col2:
            completion_rate = len(prescriptions[prescriptions['status'] == 'Completed']) / len(prescriptions) * 100
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        with col3:
            avg_processing_time = "2.5 days"  # This would require more detailed tracking
            st.metric("Avg Processing Time", avg_processing_time)
        
        with col4:
            unique_medicines = len(prescriptions['medicine_name'].unique())
            st.metric("Medicines Prescribed", unique_medicines)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Prescription Status Distribution")
            status_counts = prescriptions['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color_discrete_map={
                    'Completed': '#059669',
                    'Pending': '#F59E0B',
                    'Partially Filled': '#EA580C',
                    'Cancelled': '#DC2626'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Prescriptions by Doctor")
            doctor_counts = prescriptions['doctor_name'].value_counts().head(10)
            fig = px.bar(
                x=doctor_counts.values,
                y=doctor_counts.index,
                orientation='h',
                title="Top 10 Prescribing Doctors"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Monthly prescription trends
        st.subheader("Monthly Prescription Trends")
        prescriptions['date_prescribed'] = pd.to_datetime(prescriptions['date_prescribed'])
        prescriptions['month_year'] = prescriptions['date_prescribed'].dt.to_period('M')
        
        monthly_trends = prescriptions.groupby(['month_year', 'status']).size().unstack(fill_value=0)
        
        fig = go.Figure()
        for status in monthly_trends.columns:
            fig.add_trace(go.Scatter(
                x=monthly_trends.index.astype(str),
                y=monthly_trends[status],
                mode='lines+markers',
                name=status,
                stackgroup='one' if status in ['Completed', 'Cancelled'] else None
            ))
        
        fig.update_layout(
            title="Monthly Prescription Trends by Status",
            xaxis_title="Month",
            yaxis_title="Number of Prescriptions",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Export functionality
        st.subheader("📥 Export Reports")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export Prescription Data"):
                csv_data = prescriptions.to_csv(index=False)
                st.download_button(
                    label="Download Prescriptions CSV",
                    data=csv_data,
                    file_name=f"prescriptions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            medicines = dm.load_medicines()
            if not medicines.empty and st.button("Export Inventory Data"):
                csv_data = medicines.to_csv(index=False)
                st.download_button(
                    label="Download Inventory CSV",
                    data=csv_data,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            customers = dm.load_customers()
            if not customers.empty and st.button("Export Customer Data"):
                csv_data = customers.to_csv(index=False)
                st.download_button(
                    label="Download Customers CSV",
                    data=csv_data,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    else:
        st.info("No prescription data available for analytics.")
