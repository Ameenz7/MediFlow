import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from utils.helpers import format_currency

st.markdown('<h1 class="main-header">👥 Customer Management</h1>', unsafe_allow_html=True)

dm = st.session_state.data_manager

# Customer management tabs
tab1, tab2, tab3 = st.tabs(["👥 Customer Directory", "➕ Add Customer", "📊 Customer History"])

with tab1:
    st.subheader("Customer Directory")
    
    # Search and filter controls
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("🔍 Search customers", placeholder="Enter name, phone, or email...")
    
    with col2:
        sort_by = st.selectbox("Sort by", ["Name (A-Z)", "Name (Z-A)", "Recent Activity", "Most Prescriptions"])
    
    # Load and filter customers
    customers = dm.load_customers()
    prescriptions = dm.load_prescriptions()
    
    if not customers.empty:
        # Apply search filter
        if search_term:
            customers = customers[
                customers['name'].str.contains(search_term, case=False, na=False) |
                customers['phone'].str.contains(search_term, case=False, na=False) |
                customers['email'].str.contains(search_term, case=False, na=False)
            ]
        
        if not customers.empty:
            # Add prescription counts and last visit
            for idx, customer in customers.iterrows():
                customer_prescriptions = prescriptions[prescriptions['customer_name'] == customer['name']]
                customers.at[idx, 'prescription_count'] = len(customer_prescriptions)
                if not customer_prescriptions.empty:
                    customers.at[idx, 'last_visit'] = customer_prescriptions['date_prescribed'].max()
                else:
                    customers.at[idx, 'last_visit'] = 'Never'
            
            # Apply sorting
            if sort_by == "Name (A-Z)":
                customers = customers.sort_values('name')
            elif sort_by == "Name (Z-A)":
                customers = customers.sort_values('name', ascending=False)
            elif sort_by == "Recent Activity":
                customers = customers.sort_values('last_visit', ascending=False)
            elif sort_by == "Most Prescriptions":
                customers = customers.sort_values('prescription_count', ascending=False)
            
            # Display customer cards
            for _, customer in customers.iterrows():
                with st.expander(f"👤 {customer['name']} - {customer['prescription_count']} prescriptions"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Name:** {customer['name']}")
                        st.write(f"**Phone:** {customer['phone']}")
                        st.write(f"**Email:** {customer['email']}")
                    
                    with col2:
                        st.write(f"**Date of Birth:** {customer['date_of_birth']}")
                        st.write(f"**Gender:** {customer['gender']}")
                        st.write(f"**Blood Type:** {customer.get('blood_type', 'Not specified')}")
                    
                    with col3:
                        st.write(f"**Address:** {customer['address']}")
                        st.write(f"**Total Prescriptions:** {customer['prescription_count']}")
                        st.write(f"**Last Visit:** {customer['last_visit']}")
                    
                    if customer.get('allergies'):
                        st.warning(f"⚠️ **Allergies:** {customer['allergies']}")
                    
                    if customer.get('medical_conditions'):
                        st.info(f"🏥 **Medical Conditions:** {customer['medical_conditions']}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"📋 View Prescriptions", key=f"view_prescriptions_{customer['customer_id']}"):
                            st.session_state.view_customer_prescriptions = customer['name']
                            st.rerun()
                    
                    with col2:
                        if st.button(f"✏️ Edit Customer", key=f"edit_customer_{customer['customer_id']}"):
                            st.session_state.edit_customer = customer['customer_id']
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"delete_customer_{customer['customer_id']}"):
                            if st.session_state.get('confirm_delete_customer') == customer['customer_id']:
                                dm.delete_customer(customer['customer_id'])
                                st.success(f"Deleted customer: {customer['name']}")
                                st.session_state.pop('confirm_delete_customer', None)
                                st.rerun()
                            else:
                                st.session_state.confirm_delete_customer = customer['customer_id']
                                st.warning("Click again to confirm deletion")
        else:
            st.info("No customers found matching your search criteria")
    else:
        st.info("No customers registered. Add some customers to get started!")

with tab2:
    st.subheader("Add New Customer")
    
    with st.form("add_customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            name = st.text_input("Full Name*", placeholder="Enter customer's full name")
            date_of_birth = st.date_input("Date of Birth*")
            gender = st.selectbox("Gender*", ["Male", "Female", "Other", "Prefer not to say"])
            blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
        
        with col2:
            st.subheader("Contact Information")
            phone = st.text_input("Phone Number*", placeholder="Enter phone number")
            email = st.text_input("Email Address", placeholder="Enter email address")
            address = st.text_area("Address*", placeholder="Enter full address")
        
        st.subheader("Medical Information")
        col1, col2 = st.columns(2)
        
        with col1:
            allergies = st.text_area("Known Allergies", placeholder="List any known allergies (optional)")
        
        with col2:
            medical_conditions = st.text_area("Medical Conditions", placeholder="List any ongoing medical conditions (optional)")
        
        emergency_contact_name = st.text_input("Emergency Contact Name", placeholder="Emergency contact person")
        emergency_contact_phone = st.text_input("Emergency Contact Phone", placeholder="Emergency contact phone")
        
        submitted = st.form_submit_button("➕ Add Customer", type="primary")
        
        if submitted:
            if name and date_of_birth and gender and phone and address:
                customer_data = {
                    'customer_id': str(uuid.uuid4()),
                    'name': name,
                    'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                    'gender': gender,
                    'blood_type': blood_type,
                    'phone': phone,
                    'email': email,
                    'address': address,
                    'allergies': allergies,
                    'medical_conditions': medical_conditions,
                    'emergency_contact_name': emergency_contact_name,
                    'emergency_contact_phone': emergency_contact_phone,
                    'date_registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if dm.add_customer(customer_data):
                    st.success(f"✅ Customer {name} added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error adding customer. Please check if customer already exists.")
            else:
                st.error("❌ Please fill in all required fields marked with *")

with tab3:
    st.subheader("Customer Prescription History")
    
    customers = dm.load_customers()
    
    if not customers.empty:
        selected_customer = st.selectbox("Select Customer:", customers['name'].tolist())
        
        if selected_customer:
            customer_info = customers[customers['name'] == selected_customer].iloc[0]
            prescriptions = dm.load_prescriptions()
            customer_prescriptions = prescriptions[prescriptions['customer_name'] == selected_customer]
            
            # Customer summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Prescriptions", len(customer_prescriptions))
            
            with col2:
                completed_count = len(customer_prescriptions[customer_prescriptions['status'] == 'Completed'])
                st.metric("Completed", completed_count)
            
            with col3:
                pending_count = len(customer_prescriptions[customer_prescriptions['status'] == 'Pending'])
                st.metric("Pending", pending_count)
            
            with col4:
                total_spent = customer_prescriptions[customer_prescriptions['status'] == 'Completed']['total_cost'].sum()
                st.metric("Total Spent", format_currency(total_spent))
            
            # Display customer information
            with st.expander("📋 Customer Details"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Phone:** {customer_info['phone']}")
                    st.write(f"**Email:** {customer_info['email']}")
                    st.write(f"**Date of Birth:** {customer_info['date_of_birth']}")
                    st.write(f"**Gender:** {customer_info['gender']}")
                
                with col2:
                    st.write(f"**Blood Type:** {customer_info.get('blood_type', 'Not specified')}")
                    st.write(f"**Address:** {customer_info['address']}")
                    if customer_info.get('allergies'):
                        st.warning(f"**Allergies:** {customer_info['allergies']}")
                    if customer_info.get('medical_conditions'):
                        st.info(f"**Medical Conditions:** {customer_info['medical_conditions']}")
            
            # Prescription history
            if not customer_prescriptions.empty:
                st.subheader(f"Prescription History for {selected_customer}")
                
                # Sort by date (newest first)
                customer_prescriptions = customer_prescriptions.sort_values('date_prescribed', ascending=False)
                
                for _, prescription in customer_prescriptions.iterrows():
                    with st.expander(f"📄 {prescription['date_prescribed']} - {prescription['medicine_name']} ({prescription['status']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Medicine:** {prescription['medicine_name']}")
                            st.write(f"**Quantity:** {prescription['quantity']}")
                            st.write(f"**Dosage:** {prescription['dosage']}")
                            st.write(f"**Doctor:** {prescription['doctor_name']}")
                        
                        with col2:
                            st.write(f"**Date Prescribed:** {prescription['date_prescribed']}")
                            st.write(f"**Status:** {prescription['status']}")
                            st.write(f"**Total Cost:** {format_currency(prescription['total_cost'])}")
                            
                            if prescription['instructions']:
                                st.write(f"**Instructions:** {prescription['instructions']}")
            else:
                st.info(f"No prescription history found for {selected_customer}")
    else:
        st.info("No customers available.")

# Handle viewing customer prescriptions
if st.session_state.get('view_customer_prescriptions'):
    customer_name = st.session_state.view_customer_prescriptions
    st.subheader(f"Prescriptions for {customer_name}")
    
    prescriptions = dm.load_prescriptions()
    customer_prescriptions = prescriptions[prescriptions['customer_name'] == customer_name]
    
    if not customer_prescriptions.empty:
        for _, prescription in customer_prescriptions.iterrows():
            st.write(f"**{prescription['date_prescribed']}** - {prescription['medicine_name']} - {prescription['status']}")
    else:
        st.info("No prescriptions found for this customer")
    
    if st.button("← Back to Customer Directory"):
        st.session_state.pop('view_customer_prescriptions', None)
        st.rerun()
