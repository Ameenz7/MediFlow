import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.markdown('<h1 class="main-header">💊 Refill Reminders</h1>', unsafe_allow_html=True)

# Initialize data manager if not already done
if 'data_manager' not in st.session_state:
    try:
        # Try to use database manager first
        from utils.database_manager import DatabaseManager
        st.session_state.data_manager = DatabaseManager()
        st.session_state.using_database = True
    except Exception as e:
        # Fall back to CSV manager if database fails
        from utils.data_manager import DataManager
        st.session_state.data_manager = DataManager()
        st.session_state.using_database = False

dm = st.session_state.data_manager

# Create tabs for different refill reminder functions
tab1, tab2, tab3 = st.tabs(["📋 Active Reminders", "➕ Add Reminder", "📊 Reminder Analytics"])

with tab1:
    st.subheader("📋 Active Refill Reminders")

    # Get due reminders for next 7 days
    try:
        due_reminders = dm.get_due_refills(7)
    except AttributeError:
        st.error("❌ DataManager method not found. Please check the data_manager.py file.")
        st.info("This might be a temporary loading issue. Try refreshing the page.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading refill reminders: {e}")
        st.info("This might be a temporary issue. Try refreshing the page.")
        st.stop()

    if not due_reminders.empty:
        # Convert date columns to datetime format
        due_reminders['refill_due_date'] = pd.to_datetime(due_reminders['refill_due_date'])

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            total_due = len(due_reminders)
            st.metric("Due This Week", total_due)

        with col2:
            today_due = len(due_reminders[due_reminders['refill_due_date'].dt.date == datetime.now().date()])
            st.metric("Due Today", today_due)

        with col3:
            urgent_due = len(due_reminders[due_reminders['refill_due_date'].dt.date < datetime.now().date()])
            st.metric("Overdue", urgent_due)

        st.markdown("---")

        # Display reminders
        for _, reminder in due_reminders.iterrows():
            days_until_due = (reminder['refill_due_date'] - pd.Timestamp.now()).days

            if days_until_due < 0:
                alert_type = "overdue"
                alert_color = "#DC2626"
                alert_icon = "🔴"
            elif days_until_due == 0:
                alert_type = "today"
                alert_color = "#F59E0B"
                alert_icon = "🟡"
            else:
                alert_type = "upcoming"
                alert_color = "#059669"
                alert_icon = "🟢"

            st.markdown(f"""
            <div class="warning-card" style="border-left: 4px solid {alert_color};">
                <h4>{alert_icon} {reminder['customer_name']} - {reminder['medicine_name']}</h4>
                <p><strong>Due Date:</strong> {reminder['refill_due_date'].strftime('%Y-%m-%d')}</p>
                <p><strong>Dosage:</strong> {reminder['dosage']} | <strong>Quantity:</strong> {reminder['quantity_per_refill']}</p>
                <p><strong>Status:</strong> {alert_type.title()} | <strong>Last Prescription:</strong> {reminder['last_prescription_date']}</p>
                {f'<p><strong>Notes:</strong> {reminder["notes"]}</p>' if reminder['notes'] else ''}
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Mark as Sent", key=f"sent_{reminder['reminder_id']}"):
                    if dm.mark_reminder_sent(reminder['reminder_id']):
                        st.success("Reminder marked as sent!")
                        st.rerun()

            with col2:
                if st.button("Complete Refill", key=f"complete_{reminder['reminder_id']}"):
                    if dm.update_refill_reminder_status(reminder['reminder_id'], 'Completed'):
                        st.success("Refill marked as completed!")
                        st.rerun()

            with col3:
                if st.button("Cancel Reminder", key=f"cancel_{reminder['reminder_id']}"):
                    if dm.update_refill_reminder_status(reminder['reminder_id'], 'Cancelled'):
                        st.success("Reminder cancelled!")
                        st.rerun()

            st.markdown("---")
    else:
        st.success("✅ No refill reminders due this week!")

    # Show all active reminders (not just due ones)
    st.subheader("All Active Reminders")
    try:
        all_reminders = dm.load_refill_reminders()
        active_reminders = all_reminders[all_reminders['status'] == 'Active']
    except Exception as e:
        st.error(f"❌ Error loading active reminders: {e}")
        st.info("This might be a temporary issue. Try refreshing the page.")
        st.stop()

    if not active_reminders.empty:
        active_reminders['refill_due_date'] = pd.to_datetime(active_reminders['refill_due_date'])
        active_reminders['days_until_due'] = (active_reminders['refill_due_date'] - pd.Timestamp.now()).dt.days

        st.dataframe(active_reminders[['customer_name', 'medicine_name', 'refill_due_date', 'days_until_due', 'dosage', 'quantity_per_refill']], width='stretch')
    else:
        st.info("No active refill reminders.")

with tab2:
    st.subheader("➕ Add New Refill Reminder")

    with st.form("add_refill_reminder"):
        col1, col2 = st.columns(2)

        with col1:
            customer_name = st.text_input("Customer Name*")
            medicine_name = st.text_input("Medicine Name*")
            dosage = st.text_input("Dosage (e.g., 500mg)*")
            last_prescription_date = st.date_input("Last Prescription Date*", value=datetime.now())

        with col2:
            refill_interval_days = st.number_input("Refill Interval (days)*", min_value=1, value=30)
            quantity_per_refill = st.number_input("Quantity per Refill*", min_value=1, value=30)
            notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Refill Reminder")

        if submitted:
            if customer_name and medicine_name and dosage:
                due_date = datetime.now() + timedelta(days=refill_interval_days)

                reminder_data = {
                    'reminder_id': f"RR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'customer_name': customer_name,
                    'medicine_name': medicine_name,
                    'last_prescription_date': last_prescription_date.strftime('%Y-%m-%d'),
                    'refill_due_date': due_date.strftime('%Y-%m-%d'),
                    'dosage': dosage,
                    'quantity_per_refill': quantity_per_refill,
                    'reminder_sent': False,
                    'status': 'Active',
                    'notes': notes,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                if dm.add_refill_reminder(reminder_data):
                    st.success(f"✅ Refill reminder added for {customer_name}!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add refill reminder.")
            else:
                st.error("❌ Please fill in all required fields.")

with tab3:
    st.subheader("📊 Refill Reminder Analytics")

    try:
        reminders = dm.load_refill_reminders()
    except Exception as e:
        st.error(f"❌ Error loading reminders for analytics: {e}")
        st.info("This might be a temporary issue. Try refreshing the page.")
        st.stop()

    if not reminders.empty:
        # Convert date columns
        reminders['refill_due_date'] = pd.to_datetime(reminders['refill_due_date'])
        reminders['created_at'] = pd.to_datetime(reminders['created_at'])

        # Analytics metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_reminders = len(reminders)
            st.metric("Total Reminders", total_reminders)

        with col2:
            active_reminders = len(reminders[reminders['status'] == 'Active'])
            st.metric("Active Reminders", active_reminders)

        with col3:
            completed_reminders = len(reminders[reminders['status'] == 'Completed'])
            st.metric("Completed Refills", completed_reminders)

        with col4:
            completion_rate = (completed_reminders / total_reminders * 100) if total_reminders > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Reminder Status Distribution")
            status_counts = reminders['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color_discrete_map={
                    'Active': '#059669',
                    'Completed': '#2563EB',
                    'Cancelled': '#DC2626'
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

        with col2:
            st.subheader("Monthly Reminder Trends")
            monthly_reminders = reminders.groupby([reminders['created_at'].dt.to_period('M'), 'status']).size().unstack(fill_value=0)

            fig = go.Figure()
            for status in monthly_reminders.columns:
                fig.add_trace(go.Scatter(
                    x=monthly_reminders.index.astype(str),
                    y=monthly_reminders[status],
                    mode='lines+markers',
                    name=status
                ))

            fig.update_layout(
                title="Monthly Refill Reminder Trends",
                height=300,
                xaxis_title="Month",
                yaxis_title="Number of Reminders"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Top medicines with refill reminders
        st.subheader("Medicines with Most Refill Reminders")
        medicine_counts = reminders['medicine_name'].value_counts().head(10)

        fig = px.bar(
            x=medicine_counts.values,
            y=medicine_counts.index,
            orientation='h',
            title="Top 10 Medicines by Refill Reminders"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')

    else:
        st.info("No refill reminder data available for analytics.")