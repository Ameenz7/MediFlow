import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
from utils.helpers import format_currency, get_stock_status_color

st.markdown('<h1 class="main-header">💊 Medicine Inventory</h1>', unsafe_allow_html=True)

dm = st.session_state.data_manager

# Inventory management tabs
tab1, tab2, tab3 = st.tabs(["📋 Current Inventory", "➕ Add Medicine", "📝 Update Stock"])

with tab1:
    st.subheader("Current Medicine Inventory")
    
    # Search and filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search medicines", placeholder="Enter medicine name...")
    
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(dm.load_medicines()['category'].unique()) if not dm.load_medicines().empty else ["All"])
    
    with col3:
        stock_filter = st.selectbox("Stock Status", ["All", "Low Stock", "Good Stock", "Out of Stock"])
    
    # Load and filter medicines
    medicines = dm.load_medicines()
    
    if not medicines.empty:
        # Apply filters
        if search_term:
            medicines = medicines[medicines['name'].str.contains(search_term, case=False, na=False)]
        
        if category_filter != "All":
            medicines = medicines[medicines['category'] == category_filter]
        
        # Add stock status
        medicines['stock_status'] = medicines.apply(
            lambda row: 'Out of Stock' if row['stock_quantity'] == 0
            else 'Low Stock' if row['stock_quantity'] <= row['reorder_level']
            else 'Good Stock', axis=1
        )
        
        if stock_filter != "All":
            medicines = medicines[medicines['stock_status'] == stock_filter]
        
        # Display medicines table
        if not medicines.empty:
            # Format the dataframe for display
            display_df = medicines.copy()
            display_df['unit_price'] = display_df['unit_price'].apply(format_currency)
            display_df['expiry_date'] = pd.to_datetime(display_df['expiry_date']).dt.strftime('%Y-%m-%d')
            
            # Add color coding for stock status
            def color_stock_status(val):
                if val == 'Out of Stock':
                    return 'background-color: #FEE2E2; color: #DC2626'
                elif val == 'Low Stock':
                    return 'background-color: #FEF3C7; color: #D97706'
                else:
                    return 'background-color: #D1FAE5; color: #059669'
            
            styled_df = display_df.style.applymap(color_stock_status, subset=['stock_status'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Quick actions
            st.subheader("Quick Actions")
            selected_medicine = st.selectbox("Select medicine for quick update:", medicines['name'].tolist())
            
            if selected_medicine:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Restock"):
                        st.session_state.restock_medicine = selected_medicine
                        st.rerun()
                
                with col2:
                    if st.button("📝 Edit Details"):
                        st.session_state.edit_medicine = selected_medicine
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Remove"):
                        if st.session_state.get('confirm_delete') == selected_medicine:
                            dm.delete_medicine(selected_medicine)
                            st.success(f"Removed {selected_medicine} from inventory")
                            st.session_state.pop('confirm_delete', None)
                            st.rerun()
                        else:
                            st.session_state.confirm_delete = selected_medicine
                            st.warning("Click again to confirm deletion")
        else:
            st.info("No medicines found matching your criteria")
    else:
        st.info("No medicines in inventory. Add some medicines to get started!")

with tab2:
    st.subheader("Add New Medicine")
    
    with st.form("add_medicine_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Medicine Name*", placeholder="Enter medicine name")
            category = st.selectbox("Category*", [
                "Prescription", "Over-the-Counter", "Antibiotics", "Pain Relief", 
                "Cold & Flu", "Vitamins", "First Aid", "Other"
            ])
            manufacturer = st.text_input("Manufacturer", placeholder="Enter manufacturer name")
            supplier = st.text_input("Supplier*", placeholder="Enter supplier name")
        
        with col2:
            unit_price = st.number_input("Unit Price ($)*", min_value=0.01, step=0.01, format="%.2f")
            stock_quantity = st.number_input("Initial Stock Quantity*", min_value=0, step=1)
            reorder_level = st.number_input("Reorder Level*", min_value=1, step=1, value=10)
            expiry_date = st.date_input("Expiry Date*", min_value=datetime.now().date())
        
        description = st.text_area("Description", placeholder="Enter medicine description (optional)")
        
        submitted = st.form_submit_button("➕ Add Medicine", type="primary")
        
        if submitted:
            if name and category and supplier and unit_price and stock_quantity >= 0:
                medicine_data = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'category': category,
                    'manufacturer': manufacturer,
                    'supplier': supplier,
                    'unit_price': unit_price,
                    'stock_quantity': stock_quantity,
                    'reorder_level': reorder_level,
                    'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                    'description': description,
                    'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if dm.add_medicine(medicine_data):
                    st.success(f"✅ {name} added to inventory successfully!")
                    st.rerun()
                else:
                    st.error("❌ Medicine with this name already exists!")
            else:
                st.error("❌ Please fill in all required fields marked with *")

with tab3:
    st.subheader("Update Stock Levels")
    
    medicines = dm.load_medicines()
    
    if not medicines.empty:
        selected_med = st.selectbox("Select Medicine to Update:", medicines['name'].tolist())
        
        if selected_med:
            current_med = medicines[medicines['name'] == selected_med].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Current Stock:** {current_med['stock_quantity']} units")
                st.info(f"**Reorder Level:** {current_med['reorder_level']} units")
                st.info(f"**Unit Price:** {format_currency(current_med['unit_price'])}")
            
            with col2:
                update_type = st.radio("Update Type:", ["Add Stock", "Remove Stock", "Set Exact Amount"])
                
                if update_type == "Add Stock":
                    quantity = st.number_input("Quantity to Add:", min_value=1, step=1)
                    if st.button("➕ Add Stock"):
                        new_quantity = current_med['stock_quantity'] + quantity
                        dm.update_medicine_stock(selected_med, new_quantity)
                        st.success(f"Added {quantity} units. New stock: {new_quantity}")
                        st.rerun()
                
                elif update_type == "Remove Stock":
                    max_remove = current_med['stock_quantity']
                    quantity = st.number_input(f"Quantity to Remove (max {max_remove}):", 
                                             min_value=1, max_value=max_remove, step=1)
                    if st.button("➖ Remove Stock"):
                        new_quantity = current_med['stock_quantity'] - quantity
                        dm.update_medicine_stock(selected_med, new_quantity)
                        st.success(f"Removed {quantity} units. New stock: {new_quantity}")
                        st.rerun()
                
                else:  # Set Exact Amount
                    quantity = st.number_input("Set Stock to:", min_value=0, step=1, 
                                             value=current_med['stock_quantity'])
                    if st.button("📝 Set Stock"):
                        dm.update_medicine_stock(selected_med, quantity)
                        st.success(f"Stock updated to {quantity} units")
                        st.rerun()
    else:
        st.info("No medicines available to update. Add some medicines first!")

# Handle restock dialog
if st.session_state.get('restock_medicine'):
    medicine_name = st.session_state.restock_medicine
    current_med = medicines[medicines['name'] == medicine_name].iloc[0]
    
    st.subheader(f"Restock: {medicine_name}")
    restock_quantity = st.number_input("Restock Quantity:", min_value=1, step=1, value=50)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm Restock"):
            new_quantity = current_med['stock_quantity'] + restock_quantity
            dm.update_medicine_stock(medicine_name, new_quantity)
            st.success(f"Restocked {restock_quantity} units of {medicine_name}")
            st.session_state.pop('restock_medicine', None)
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.pop('restock_medicine', None)
            st.rerun()
