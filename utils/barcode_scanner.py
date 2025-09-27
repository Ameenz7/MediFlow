"""
Barcode and QR Code Scanner for Quick Medicine Entry
Provides functionality to scan barcodes/QR codes for quick medicine lookup and entry
"""

import streamlit as st
import pandas as pd
import json
import os
from typing import Dict, List, Optional
import re

class BarcodeScanner:
    def __init__(self):
        self.scanned_medicines_file = "data/scanned_medicines.json"
        self._initialize_scanned_medicines()

    def _initialize_scanned_medicines(self):
        """Initialize scanned medicines tracking"""
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(self.scanned_medicines_file):
            with open(self.scanned_medicines_file, 'w') as f:
                json.dump([], f)

    def scan_barcode_input(self) -> Optional[str]:
        """
        Get barcode input from user
        Returns scanned barcode or None if cancelled
        """
        st.subheader("📱 Barcode Scanner")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Manual Entry:**")
            barcode_input = st.text_input(
                "Enter Barcode/QR Code",
                placeholder="Scan or type barcode here...",
                help="Enter the barcode number manually or use a barcode scanner"
            )

            if st.button("🔍 Lookup Medicine", type="primary"):
                if barcode_input.strip():
                    return barcode_input.strip()

        with col2:
            st.write("**Quick Scan:**")
            if st.button("📷 Start Camera Scan", help="This would integrate with device camera in a real app"):
                st.info("📷 Camera scanning would be implemented here with device integration")

            # Demo scan buttons for testing
            if st.button("🧪 Demo: Scan Paracetamol"):
                return "PARA001"
            if st.button("🧪 Demo: Scan Amoxicillin"):
                return "AMOX002"
            if st.button("🧪 Demo: Scan Ibuprofen"):
                return "IBUP003"

        return None

    def lookup_medicine_by_barcode(self, barcode: str, medicines_df: pd.DataFrame) -> Optional[Dict]:
        """
        Lookup medicine information by barcode
        Returns medicine data or None if not found
        """
        # Simple barcode matching - in real implementation this would be more sophisticated
        barcode_map = {
            "PARA001": "Paracetamol",
            "AMOX002": "Amoxicillin",
            "IBUP003": "Ibuprofen",
            "CETI004": "Cetirizine",
            "OMEP005": "Omeprazole"
        }

        medicine_name = barcode_map.get(barcode.upper())
        if medicine_name and not medicines_df.empty:
            medicine_data = medicines_df[medicines_df['name'] == medicine_name]
            if not medicine_data.empty:
                return medicine_data.iloc[0].to_dict()

        return None

    def add_medicine_to_prescription(self, medicine_data: Dict, quantity: int = 1) -> Dict:
        """
        Add scanned medicine to prescription with specified quantity
        Returns prescription item data
        """
        return {
            'medicine_name': medicine_data['name'],
            'medicine_id': medicine_data['id'],
            'quantity': quantity,
            'unit_price': medicine_data['unit_price'],
            'total_cost': medicine_data['unit_price'] * quantity,
            'dosage': 'As prescribed',  # Default dosage
            'scanned_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def show_scanner_interface(self, medicines_df: pd.DataFrame) -> Optional[List[Dict]]:
        """
        Display the barcode scanner interface
        Returns list of scanned prescription items or None
        """
        st.markdown("### Quick Entry with Barcode Scanner")

        if medicines_df.empty:
            st.warning("⚠️ No medicines available. Please add medicines to inventory first.")
            return None

        # Scan barcode section
        barcode = self.scan_barcode_input()

        prescription_items = []
        current_items = []

        if barcode:
            # Lookup medicine
            medicine_data = self.lookup_medicine_by_barcode(barcode, medicines_df)

            if medicine_data:
                st.success(f"✅ Found: **{medicine_data['name']}**")

                # Show medicine details
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Category:** {medicine_data['category']}")
                    st.write(f"**Available Stock:** {medicine_data['stock_quantity']}")
                    st.write(f"**Unit Price:** ${medicine_data['unit_price']}")

                with col2:
                    st.write(f"**Manufacturer:** {medicine_data['manufacturer']}")
                    st.write(f"**Supplier:** {medicine_data['supplier']}")
                    if medicine_data.get('expiry_date'):
                        st.write(f"**Expiry:** {medicine_data['expiry_date']}")

                # Quantity and dosage input
                st.markdown("---")
                col1, col2 = st.columns(2)

                with col1:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        max_value=int(medicine_data['stock_quantity']),
                        value=1,
                        key=f"qty_{barcode}"
                    )

                with col2:
                    dosage = st.text_input(
                        "Dosage Instructions",
                        value="As prescribed",
                        key=f"dosage_{barcode}"
                    )

                # Add to prescription button
                if st.button("➕ Add to Prescription", type="primary", key=f"add_{barcode}"):
                    prescription_item = self.add_medicine_to_prescription(medicine_data, quantity)
                    prescription_item['dosage'] = dosage
                    current_items.append(prescription_item)

                    # Save scanned medicine record
                    self._record_scanned_medicine(medicine_data, barcode, quantity)

                    st.success(f"✅ Added {quantity}x {medicine_data['name']} to prescription!")
                    st.rerun()

            else:
                st.error(f"❌ Medicine not found for barcode: {barcode}")
                st.info("💡 Make sure the medicine exists in your inventory with the correct barcode mapping.")

        # Show current prescription items
        if current_items:
            st.markdown("### Current Prescription Items")
            for i, item in enumerate(current_items):
                with st.expander(f"💊 {item['medicine_name']} - {item['quantity']} units"):
                    st.write(f"**Unit Price:** ${item['unit_price']}")
                    st.write(f"**Total Cost:** ${item['total_cost']}")
                    st.write(f"**Dosage:** {item['dosage']}")
                    st.write(f"**Scanned At:** {item['scanned_at']}")

                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        current_items.pop(i)
                        st.rerun()

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Scan Another Item"):
                st.rerun()

        with col2:
            if current_items and st.button("✅ Complete Prescription", type="primary"):
                return current_items

        with col3:
            if st.button("❌ Clear All"):
                current_items.clear()
                st.rerun()

        return current_items if current_items else None

    def _record_scanned_medicine(self, medicine_data: Dict, barcode: str, quantity: int):
        """Record scanned medicine for analytics"""
        try:
            with open(self.scanned_medicines_file, 'r') as f:
                scanned_records = json.load(f)
        except:
            scanned_records = []

        scan_record = {
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'barcode': barcode,
            'medicine_name': medicine_data['name'],
            'medicine_id': medicine_data['id'],
            'quantity': quantity,
            'unit_price': medicine_data['unit_price'],
            'total_value': medicine_data['unit_price'] * quantity
        }

        scanned_records.append(scan_record)

        with open(self.scanned_medicines_file, 'w') as f:
            json.dump(scanned_records, f, indent=2)

    def get_scan_analytics(self) -> Dict:
        """Get analytics for scanned medicines"""
        try:
            with open(self.scanned_medicines_file, 'r') as f:
                scanned_records = json.load(f)

            if not scanned_records:
                return {
                    'total_scans': 0,
                    'total_value': 0,
                    'unique_medicines': 0,
                    'recent_scans': []
                }

            df = pd.DataFrame(scanned_records)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            return {
                'total_scans': len(scanned_records),
                'total_value': df['total_value'].sum(),
                'unique_medicines': df['medicine_name'].nunique(),
                'recent_scans': df.sort_values('timestamp', ascending=False).head(5).to_dict('records')
            }

        except Exception as e:
            st.error(f"Error loading scan analytics: {e}")
            return {
                'total_scans': 0,
                'total_value': 0,
                'unique_medicines': 0,
                'recent_scans': []
            }

    def show_scan_analytics(self):
        """Display barcode scanning analytics"""
        st.subheader("📊 Barcode Scanning Analytics")

        analytics = self.get_scan_analytics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Scans", analytics['total_scans'])

        with col2:
            st.metric("Total Value", f"${analytics['total_value']:.2f}")

        with col3:
            st.metric("Unique Medicines", analytics['unique_medicines'])

        with col4:
            recent_count = len(analytics['recent_scans'])
            st.metric("Recent Scans", recent_count)

        if analytics['recent_scans']:
            st.subheader("Recent Scans")
            for scan in analytics['recent_scans']:
                st.write(f"• **{scan['medicine_name']}** - {scan['quantity']} units (${scan['total_value']:.2f}) at {scan['timestamp']}")

def create_prescription_from_scan(medicines_df: pd.DataFrame, customers_df: pd.DataFrame) -> Optional[Dict]:
    """
    Create a complete prescription using barcode scanning
    Returns prescription data or None if cancelled
    """
    scanner = BarcodeScanner()

    st.markdown('<h2 class="main-header">🏥 Quick Prescription Entry</h2>', unsafe_allow_html=True)

    # Customer selection
    if not customers_df.empty:
        customer_name = st.selectbox("Select Patient", customers_df['name'].tolist())
        customer_data = customers_df[customers_df['name'] == customer_name].iloc[0]
    else:
        st.warning("⚠️ No customers available. Please add customers first.")
        return None

    # Doctor input
    doctor_name = st.text_input("Prescribing Doctor", placeholder="Enter doctor's name")

    if not doctor_name:
        st.warning("⚠️ Please enter the prescribing doctor's name.")
        return None

    # Barcode scanning interface
    scanned_items = scanner.show_scanner_interface(medicines_df)

    if scanned_items:
        # Calculate total cost
        total_cost = sum(item['total_cost'] for item in scanned_items)

        # Create prescription data
        prescription_data = {
            'prescription_id': f"RX_SCAN_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}",
            'customer_name': customer_name,
            'doctor_name': doctor_name,
            'scanned_items': scanned_items,
            'total_cost': total_cost,
            'date_prescribed': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'status': 'Pending',
            'created_via': 'barcode_scan',
            'created_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return prescription_data

    return None