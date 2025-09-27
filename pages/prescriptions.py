import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
from utils.helpers import format_currency
from utils.medicine_interactions import check_patient_safety
from utils.barcode_scanner import create_prescription_from_scan

st.markdown('<h1 class="main-header">📋 Prescription Management</h1>', unsafe_allow_html=True)

# Initialize data manager if not already done
if 'data_manager' not in st.session_state:
    from utils.data_manager import DataManager
    st.session_state.data_manager = DataManager()

dm = st.session_state.data_manager

# Prescription management tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Prescriptions", "➕ New Prescription", "📊 Prescription History", "📱 Quick Scan Entry"])

with tab1:
    st.subheader("Active Prescriptions")
    
    # Search and filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_customer = st.text_input("🔍 Search by customer", placeholder="Enter customer name...")
    
    with col2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Partially Filled", "Completed", "Cancelled"])
    
    with col3:
        date_filter = st.selectbox("Date Range", ["All", "Today", "This Week", "This Month"])
    
    # Load and filter prescriptions
    prescriptions = dm.load_prescriptions()
    
    if not prescriptions.empty:
        # Apply filters
        if search_customer:
            prescriptions = prescriptions[prescriptions['customer_name'].str.contains(search_customer, case=False, na=False)]
        
        if status_filter != "All":
            prescriptions = prescriptions[prescriptions['status'] == status_filter]
        
        if date_filter != "All":
            prescriptions['date_prescribed'] = pd.to_datetime(prescriptions['date_prescribed'])
            today = datetime.now()
            
            if date_filter == "Today":
                prescriptions = prescriptions[prescriptions['date_prescribed'].dt.date == today.date()]
            elif date_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                prescriptions = prescriptions[prescriptions['date_prescribed'] >= week_start]
            elif date_filter == "This Month":
                month_start = today.replace(day=1)
                prescriptions = prescriptions[prescriptions['date_prescribed'] >= month_start]
        
        if not prescriptions.empty:
            # Display prescriptions
            for _, prescription in prescriptions.iterrows():
                with st.expander(f"🏥 Prescription #{prescription['prescription_id'][:8]} - {prescription['customer_name']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Customer:** {prescription['customer_name']}")
                        st.write(f"**Doctor:** {prescription['doctor_name']}")
                        st.write(f"**Date Prescribed:** {prescription['date_prescribed']}")
                    
                    with col2:
                        st.write(f"**Medicine:** {prescription['medicine_name']}")
                        st.write(f"**Quantity:** {prescription['quantity']}")
                        st.write(f"**Dosage:** {prescription['dosage']}")
                    
                    with col3:
                        status_color = {
                            'Pending': '🟡',
                            'Partially Filled': '🟠', 
                            'Completed': '🟢',
                            'Cancelled': '🔴'
                        }
                        st.write(f"**Status:** {status_color.get(prescription['status'], '⚪')} {prescription['status']}")
                        st.write(f"**Total Cost:** {format_currency(prescription['total_cost'])}")
                    
                    if prescription['instructions']:
                        st.write(f"**Instructions:** {prescription['instructions']}")
                    
                    # Action buttons
                    if prescription['status'] in ['Pending', 'Partially Filled']:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"✅ Complete", key=f"complete_{prescription['prescription_id']}"):
                                dm.update_prescription_status(prescription['prescription_id'], 'Completed')
                                st.success("Prescription marked as completed!")
                                st.rerun()
                        
                        with col2:
                            if st.button(f"⏸️ Partial Fill", key=f"partial_{prescription['prescription_id']}"):
                                dm.update_prescription_status(prescription['prescription_id'], 'Partially Filled')
                                st.success("Prescription marked as partially filled!")
                                st.rerun()
                        
                        with col3:
                            if st.button(f"❌ Cancel", key=f"cancel_{prescription['prescription_id']}"):
                                dm.update_prescription_status(prescription['prescription_id'], 'Cancelled')
                                st.success("Prescription cancelled!")
                                st.rerun()
        else:
            st.info("No prescriptions found matching your criteria")
    else:
        st.info("No prescriptions found. Create a new prescription to get started!")

with tab2:
    st.subheader("Create New Prescription")
    
    # Load customers and medicines for selection
    customers = dm.load_customers()
    medicines = dm.load_medicines()
    
    if customers.empty:
        st.warning("⚠️ No customers found. Please add customers first before creating prescriptions.")
    elif medicines.empty:
        st.warning("⚠️ No medicines found. Please add medicines to inventory first.")
    else:
        with st.form("new_prescription_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Patient Information")
                customer_name = st.selectbox("Select Customer*", customers['name'].tolist())
                doctor_name = st.text_input("Doctor Name*", placeholder="Enter prescribing doctor's name")
                date_prescribed = st.date_input("Date Prescribed*", value=datetime.now().date())
            
            with col2:
                st.subheader("Prescription Details")
                medicine_name = st.selectbox("Select Medicine*", medicines['name'].tolist())

                # Show available stock
                if medicine_name:
                    selected_medicine = medicines[medicines['name'] == medicine_name].iloc[0]
                    st.info(f"Available Stock: {selected_medicine['stock_quantity']} units")
                    max_quantity = selected_medicine['stock_quantity']
                else:
                    max_quantity = 1

                quantity = st.number_input("Quantity*", min_value=1, max_value=max_quantity, step=1)
                dosage = st.text_input("Dosage Instructions*", placeholder="e.g., 1 tablet twice daily")

                # Medicine Safety Warnings
                if medicine_name and customer_name:
                    # Get customer data for comprehensive safety check
                    customer_data = customers[customers['name'] == customer_name].iloc[0] if not customers.empty else None

                    if customer_data is not None:
                        # Check for medicine conflicts and patient safety
                        safety_check = check_patient_safety([medicine_name], customer_data.to_dict())

                        if safety_check['warnings']:
                            st.markdown("### ⚠️ Medicine Safety Warnings")

                            for warning in safety_check['warnings']:
                                severity = warning['severity']
                                icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"

                                st.markdown(f"""
                                <div class="warning-card" style="border-left: 4px solid {'#DC2626' if severity == 'high' else '#F59E0B' if severity == 'medium' else '#059669'};">
                                    <h4>{icon} {warning['type'].replace('_', ' ').title()}</h4>
                                    <p><strong>Description:</strong> {warning['description']}</p>
                                    <p><strong>Recommendation:</strong> {warning['recommendation']}</p>
                                </div>
                                """, unsafe_allow_html=True)

                            if safety_check['high_risk_count'] > 0:
                                st.error("🚨 **High Risk Warning**: This prescription may pose significant health risks. Please consult with a healthcare professional before proceeding.")
                            elif safety_check['total_warnings'] > 0:
                                st.warning("⚠️ **Caution**: Please review the warnings above before proceeding with this prescription.")
            
            instructions = st.text_area("Additional Instructions", placeholder="Special instructions for the patient")
            
            submitted = st.form_submit_button("➕ Create Prescription", type="primary")
            
            if submitted:
                if customer_name and doctor_name and medicine_name and quantity and dosage:
                    # Calculate total cost
                    unit_price = medicines[medicines['name'] == medicine_name]['unit_price'].iloc[0]
                    total_cost = unit_price * quantity
                    
                    prescription_data = {
                        'prescription_id': str(uuid.uuid4()),
                        'customer_name': customer_name,
                        'doctor_name': doctor_name,
                        'medicine_name': medicine_name,
                        'quantity': quantity,
                        'dosage': dosage,
                        'instructions': instructions,
                        'date_prescribed': date_prescribed.strftime('%Y-%m-%d'),
                        'status': 'Pending',
                        'total_cost': total_cost,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    if dm.add_prescription(prescription_data):
                        st.success(f"✅ Prescription created successfully!")
                        st.info(f"Total Cost: {format_currency(total_cost)}")
                        
                        # Update medicine stock
                        selected_medicine = medicines[medicines['name'] == medicine_name].iloc[0]
                        new_stock = selected_medicine['stock_quantity'] - quantity
                        dm.update_medicine_stock(medicine_name, new_stock)
                        
                        st.rerun()
                    else:
                        st.error("❌ Error creating prescription. Please try again.")
                else:
                    st.error("❌ Please fill in all required fields marked with *")

with tab3:
    st.subheader("Prescription History")
    
    prescriptions = dm.load_prescriptions()
    
    if not prescriptions.empty:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_prescriptions = len(prescriptions)
            st.metric("Total Prescriptions", total_prescriptions)
        
        with col2:
            completed_prescriptions = len(prescriptions[prescriptions['status'] == 'Completed'])
            st.metric("Completed", completed_prescriptions)
        
        with col3:
            pending_prescriptions = len(prescriptions[prescriptions['status'] == 'Pending'])
            st.metric("Pending", pending_prescriptions)
        
        with col4:
            total_revenue = prescriptions[prescriptions['status'] == 'Completed']['total_cost'].sum()
            st.metric("Total Revenue", format_currency(total_revenue))
        
        # Detailed history table
        st.subheader("Detailed History")
        
        # Format prescription data for display
        display_df = prescriptions.copy()
        display_df['total_cost'] = display_df['total_cost'].apply(format_currency)
        display_df = display_df.sort_values('date_prescribed', ascending=False)
        
        # Add status color coding
        def color_status(val):
            colors = {
                'Completed': 'background-color: #D1FAE5; color: #059669',
                'Pending': 'background-color: #FEF3C7; color: #D97706',
                'Partially Filled': 'background-color: #FED7AA; color: #EA580C',
                'Cancelled': 'background-color: #FEE2E2; color: #DC2626'
            }
            return colors.get(val, '')
        
        styled_df = display_df.style.map(color_status, subset=['status'])
        st.dataframe(styled_df, width='stretch')
        
        # Export functionality
        if st.button("📥 Export Prescription History"):
            csv_data = prescriptions.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"prescription_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No prescription history available.")

with tab4:
    st.subheader("📱 Quick Prescription Entry with Barcode Scanner")

    # Load data
    medicines = dm.load_medicines()
    customers = dm.load_customers()

    if customers.empty:
        st.warning("⚠️ No customers found. Please add customers first before using quick scan entry.")
    elif medicines.empty:
        st.warning("⚠️ No medicines found. Please add medicines to inventory first.")
    else:
        # Create prescription using barcode scanner
        prescription_data = create_prescription_from_scan(medicines, customers)

        if prescription_data:
            st.success("✅ Prescription created successfully via barcode scanning!")

            # Show prescription summary
            st.markdown("### Prescription Summary")
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Patient:** {prescription_data['customer_name']}")
                st.write(f"**Doctor:** {prescription_data['doctor_name']}")
                st.write(f"**Date:** {prescription_data['date_prescribed']}")

            with col2:
                st.write(f"**Items:** {len(prescription_data['scanned_items'])}")
                st.write(f"**Total Cost:** ${prescription_data['total_cost']:.2f}")
                st.write(f"**Status:** {prescription_data['status']}")

            # Show scanned items
            st.markdown("### Scanned Items")
            for item in prescription_data['scanned_items']:
                st.write(f"• **{item['medicine_name']}** - {item['quantity']} units × ${item['unit_price']:.2f} = ${item['total_cost']:.2f}")

            # Confirm and save prescription
            if st.button("💾 Save Prescription to System", type="primary"):
                # Convert scanned prescription to regular prescription format
                for item in prescription_data['scanned_items']:
                    prescription_item = {
                        'prescription_id': prescription_data['prescription_id'],
                        'customer_name': prescription_data['customer_name'],
                        'doctor_name': prescription_data['doctor_name'],
                        'medicine_name': item['medicine_name'],
                        'quantity': item['quantity'],
                        'dosage': item['dosage'],
                        'instructions': f"Scanned via barcode - {item['dosage']}",
                        'date_prescribed': prescription_data['date_prescribed'],
                        'status': prescription_data['status'],
                        'total_cost': item['total_cost'],
                        'created_at': prescription_data['created_at']
                    }

                    # Add to system
                    if dm.add_prescription(prescription_item):
                        # Update stock
                        dm.update_medicine_stock(item['medicine_name'], item['quantity'])

                st.success("✅ Prescription saved successfully!")
                st.info("You can now view it in the 'Active Prescriptions' tab.")
                st.rerun()
