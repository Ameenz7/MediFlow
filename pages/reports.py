import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.helpers import format_currency

st.markdown('<h1 class="main-header">📊 Reports & Analytics</h1>', unsafe_allow_html=True)

dm = st.session_state.data_manager

# Reports tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Inventory Reports", "💰 Sales Reports", "📈 Financial Reports", "👥 Customer Analytics", "📋 Prescription Analytics"])

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
    st.subheader("📈 Comprehensive Financial Reports")
    
    medicines = dm.load_medicines()
    prescriptions = dm.load_prescriptions()
    
    if not medicines.empty:
        # Calculate financial metrics
        medicines['profit_per_unit'] = medicines['unit_price'] - medicines['cost_price']
        medicines['profit_margin_percent'] = (medicines['profit_per_unit'] / medicines['unit_price'] * 100).round(1)
        medicines['inventory_cost'] = medicines['stock_quantity'] * medicines['cost_price']
        medicines['inventory_value'] = medicines['stock_quantity'] * medicines['unit_price']
        medicines['potential_profit'] = medicines['inventory_value'] - medicines['inventory_cost']
        
        # Financial summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_inventory_cost = medicines['inventory_cost'].sum()
            st.metric("Total Inventory Cost", format_currency(total_inventory_cost))
        
        with col2:
            total_inventory_value = medicines['inventory_value'].sum()
            st.metric("Total Inventory Value", format_currency(total_inventory_value))
        
        with col3:
            total_potential_profit = medicines['potential_profit'].sum()
            st.metric("Potential Profit", format_currency(total_potential_profit))
        
        with col4:
            overall_margin = (total_potential_profit / total_inventory_value * 100) if total_inventory_value > 0 else 0
            st.metric("Overall Margin", f"{overall_margin:.1f}%")
        
        st.markdown("---")
        
        # Profit Analysis Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Profit Margin by Medicine")
            top_margin_medicines = medicines.nlargest(10, 'profit_margin_percent')
            fig = px.bar(
                top_margin_medicines,
                x='profit_margin_percent',
                y='name',
                orientation='h',
                color='profit_margin_percent',
                color_continuous_scale='RdYlGn',
                title="Top 10 Medicines by Profit Margin %"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Inventory Value vs Cost by Category")
            category_financial = medicines.groupby('category').agg({
                'inventory_cost': 'sum',
                'inventory_value': 'sum',
                'potential_profit': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Cost',
                x=category_financial['category'],
                y=category_financial['inventory_cost'],
                marker_color='#DC2626'
            ))
            fig.add_trace(go.Bar(
                name='Value',
                x=category_financial['category'],
                y=category_financial['inventory_value'],
                marker_color='#059669'
            ))
            fig.update_layout(
                title="Inventory Cost vs Value by Category",
                barmode='group',
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Supplier Financial Analysis
        st.subheader("💼 Supplier Financial Performance")
        
        supplier_analysis = medicines.groupby('supplier').agg({
            'inventory_cost': 'sum',
            'inventory_value': 'sum',
            'potential_profit': 'sum',
            'name': 'count'
        }).reset_index()
        supplier_analysis.columns = ['Supplier', 'Total Cost', 'Total Value', 'Potential Profit', 'Medicine Count']
        supplier_analysis['Profit Margin %'] = (supplier_analysis['Potential Profit'] / supplier_analysis['Total Value'] * 100).round(1)
        supplier_analysis['Avg Cost per Medicine'] = (supplier_analysis['Total Cost'] / supplier_analysis['Medicine Count']).round(2)
        
        # Format currency columns
        for col in ['Total Cost', 'Total Value', 'Potential Profit']:
            supplier_analysis[col] = supplier_analysis[col].apply(format_currency)
        supplier_analysis['Avg Cost per Medicine'] = supplier_analysis['Avg Cost per Medicine'].apply(format_currency)
        
        st.dataframe(supplier_analysis, use_container_width=True)
        
        # Sales Profit Analysis (if prescriptions data available)
        if not prescriptions.empty:
            st.subheader("💰 Sales Profitability Analysis")
            
            completed_prescriptions = prescriptions[prescriptions['status'] == 'Completed'].copy()
            
            if not completed_prescriptions.empty:
                # Merge with medicines to get cost data
                sales_with_costs = completed_prescriptions.merge(
                    medicines[['name', 'cost_price', 'unit_price']], 
                    left_on='medicine_name', 
                    right_on='name', 
                    how='left'
                )
                
                # Calculate profit for each sale
                sales_with_costs['sale_cost'] = sales_with_costs['quantity'] * sales_with_costs['cost_price']
                sales_with_costs['sale_profit'] = sales_with_costs['total_cost'] - sales_with_costs['sale_cost']
                sales_with_costs['profit_margin'] = (sales_with_costs['sale_profit'] / sales_with_costs['total_cost'] * 100).round(1)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_sales_cost = sales_with_costs['sale_cost'].sum()
                    st.metric("Total Sales Cost", format_currency(total_sales_cost))
                
                with col2:
                    total_sales_revenue = sales_with_costs['total_cost'].sum()
                    st.metric("Total Sales Revenue", format_currency(total_sales_revenue))
                
                with col3:
                    total_sales_profit = sales_with_costs['sale_profit'].sum()
                    st.metric("Total Sales Profit", format_currency(total_sales_profit))
                
                with col4:
                    sales_margin = (total_sales_profit / total_sales_revenue * 100) if total_sales_revenue > 0 else 0
                    st.metric("Sales Margin", f"{sales_margin:.1f}%")
                
                # Profit by medicine chart
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Most Profitable Medicine Sales")
                    medicine_profits = sales_with_costs.groupby('medicine_name')['sale_profit'].sum().reset_index()
                    medicine_profits = medicine_profits.sort_values('sale_profit', ascending=False).head(10)
                    
                    fig = px.bar(
                        medicine_profits,
                        x='medicine_name',
                        y='sale_profit',
                        color='sale_profit',
                        color_continuous_scale='Greens',
                        title="Top 10 Medicines by Profit Generated"
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Daily Profit Trends")
                    sales_with_costs['date_prescribed'] = pd.to_datetime(sales_with_costs['date_prescribed'])
                    daily_profits = sales_with_costs.groupby(
                        sales_with_costs['date_prescribed'].dt.date
                    ).agg({
                        'sale_profit': 'sum',
                        'total_cost': 'sum'
                    }).reset_index()
                    daily_profits.columns = ['date', 'profit', 'revenue']
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_profits['date'],
                        y=daily_profits['revenue'],
                        mode='lines+markers',
                        name='Revenue',
                        line=dict(color='#2563EB')
                    ))
                    fig.add_trace(go.Scatter(
                        x=daily_profits['date'],
                        y=daily_profits['profit'],
                        mode='lines+markers',
                        name='Profit',
                        line=dict(color='#059669')
                    ))
                    fig.update_layout(
                        title="Daily Revenue vs Profit Trends",
                        height=400,
                        yaxis_title="Amount ($)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No completed sales available for profit analysis")
        
        # Profitability Recommendations
        st.subheader("💡 Financial Recommendations")
        
        # Low margin medicines
        low_margin_medicines = medicines[medicines['profit_margin_percent'] < 20]
        if not low_margin_medicines.empty:
            st.warning(f"⚠️ **Low Margin Alert**: {len(low_margin_medicines)} medicines have profit margins below 20%")
            with st.expander("View Low Margin Medicines"):
                display_df = low_margin_medicines[['name', 'category', 'supplier', 'cost_price', 'unit_price', 'profit_margin_percent']].copy()
                display_df['cost_price'] = display_df['cost_price'].apply(format_currency)
                display_df['unit_price'] = display_df['unit_price'].apply(format_currency)
                st.dataframe(display_df, use_container_width=True)
        
        # High value inventory
        high_value_medicines = medicines[medicines['inventory_value'] > 1000]
        if not high_value_medicines.empty:
            st.info(f"💰 **High Value Inventory**: {len(high_value_medicines)} medicines have inventory value > $1,000")
            with st.expander("View High Value Inventory"):
                display_df = high_value_medicines[['name', 'stock_quantity', 'unit_price', 'inventory_value', 'potential_profit']].copy()
                display_df['unit_price'] = display_df['unit_price'].apply(format_currency)
                display_df['inventory_value'] = display_df['inventory_value'].apply(format_currency)
                display_df['potential_profit'] = display_df['potential_profit'].apply(format_currency)
                st.dataframe(display_df, use_container_width=True)
        
        # Export financial data
        st.subheader("📊 Export Financial Reports")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Medicine Profitability"):
                export_df = medicines[['name', 'category', 'supplier', 'cost_price', 'unit_price', 'profit_per_unit', 'profit_margin_percent', 'stock_quantity', 'inventory_cost', 'inventory_value', 'potential_profit']].copy()
                csv_data = export_df.to_csv(index=False)
                st.download_button(
                    label="Download Medicine Profitability CSV",
                    data=csv_data,
                    file_name=f"medicine_profitability_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Export Supplier Analysis"):
                csv_data = supplier_analysis.to_csv(index=False)
                st.download_button(
                    label="Download Supplier Analysis CSV",
                    data=csv_data,
                    file_name=f"supplier_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    else:
        st.info("No financial data available for analysis.")

with tab4:
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

with tab5:
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
