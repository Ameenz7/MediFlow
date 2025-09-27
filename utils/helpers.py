import streamlit as st
from datetime import datetime, timedelta

def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def get_stock_status_color(stock_quantity, reorder_level):
    """Get color for stock status based on quantity and reorder level"""
    if stock_quantity == 0:
        return "#DC2626"  # Red for out of stock
    elif stock_quantity <= reorder_level:
        return "#F59E0B"  # Amber for low stock
    elif stock_quantity <= reorder_level * 2:
        return "#059669"  # Green for good stock
    else:
        return "#2563EB"  # Blue for high stock

def calculate_age(birth_date):
    """Calculate age from birth date"""
    try:
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return 0

def format_date(date_string):
    """Format date string for display"""
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_string

def get_days_until_expiry(expiry_date):
    """Calculate days until medicine expires"""
    try:
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
        today = datetime.now()
        delta = expiry - today
        return delta.days
    except:
        return 0

def validate_phone_number(phone):
    """Basic phone number validation"""
    # Remove any non-digit characters
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    # Check if it's a valid length (10 digits for US format)
    if len(clean_phone) == 10:
        return True
    elif len(clean_phone) == 11 and clean_phone.startswith('1'):
        return True
    else:
        return False

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_prescription_status_color(status):
    """Get color for prescription status"""
    colors = {
        'Pending': '#F59E0B',
        'Partially Filled': '#EA580C',
        'Completed': '#059669',
        'Cancelled': '#DC2626'
    }
    return colors.get(status, '#6B7280')

def generate_report_summary(data_type, data):
    """Generate summary text for reports"""
    if data.empty:
        return f"No {data_type} data available for reporting."
    
    summary = {
        'medicines': f"Total of {len(data)} medicines in inventory with combined value of ${(data['stock_quantity'] * data['unit_price']).sum():,.2f}",
        'prescriptions': f"Total of {len(data)} prescriptions with {len(data[data['status'] == 'Completed'])} completed",
        'customers': f"Total of {len(data)} registered customers"
    }
    
    return summary.get(data_type, f"{len(data)} records found")

def create_alert_message(alert_type, count, items=None):
    """Create formatted alert messages"""
    alerts = {
        'low_stock': {
            'icon': '⚠️',
            'color': '#F59E0B',
            'message': f"{count} medicines are running low on stock"
        },
        'out_of_stock': {
            'icon': '🚨',
            'color': '#DC2626', 
            'message': f"{count} medicines are out of stock"
        },
        'expiring': {
            'icon': '⏰',
            'color': '#F59E0B',
            'message': f"{count} medicines are expiring soon"
        },
        'pending_prescriptions': {
            'icon': '📋',
            'color': '#2563EB',
            'message': f"{count} prescriptions are pending"
        }
    }
    
    alert = alerts.get(alert_type, {'icon': 'ℹ️', 'color': '#6B7280', 'message': f"{count} items"})
    
    return alert

def format_dosage_instruction(dosage, quantity):
    """Format dosage instructions for prescriptions"""
    try:
        # Parse dosage string and create clear instructions
        if 'daily' in dosage.lower():
            return f"Take {dosage} for {quantity} days"
        elif 'twice' in dosage.lower():
            return f"Take {dosage} - {quantity} tablets total"
        else:
            return f"{dosage} - {quantity} tablets prescribed"
    except:
        return f"{dosage} - {quantity} tablets"

def get_reorder_suggestion(current_stock, reorder_level, avg_usage=None):
    """Suggest reorder quantity based on current stock and usage patterns"""
    if current_stock <= reorder_level:
        # Basic suggestion: order enough to reach 3x reorder level
        suggested_order = (reorder_level * 3) - current_stock
        
        if avg_usage:
            # If we have usage data, suggest based on that
            suggested_order = max(suggested_order, avg_usage * 30)  # 30 days supply
        
        return max(suggested_order, reorder_level)
    
    return 0

def calculate_prescription_metrics(prescriptions_df):
    """Calculate key metrics for prescriptions"""
    if prescriptions_df.empty:
        return {
            'total': 0,
            'completed': 0,
            'pending': 0,
            'completion_rate': 0,
            'revenue': 0,
            'avg_value': 0
        }
    
    completed = prescriptions_df[prescriptions_df['status'] == 'Completed']
    
    return {
        'total': len(prescriptions_df),
        'completed': len(completed),
        'pending': len(prescriptions_df[prescriptions_df['status'] == 'Pending']),
        'completion_rate': (len(completed) / len(prescriptions_df)) * 100 if len(prescriptions_df) > 0 else 0,
        'revenue': completed['total_cost'].sum() if not completed.empty else 0,
        'avg_value': completed['total_cost'].mean() if not completed.empty else 0
    }

def format_table_data(df, columns_to_format=None):
    """Format dataframe for better display in tables"""
    if df.empty:
        return df
    
    formatted_df = df.copy()
    
    # Format currency columns
    currency_columns = ['unit_price', 'total_cost', 'price', 'cost', 'value']
    for col in currency_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(format_currency)
    
    # Format date columns
    date_columns = ['date_prescribed', 'expiry_date', 'date_of_birth', 'created_at', 'date_added']
    for col in date_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(format_date)
    
    return formatted_df

def create_status_badge(status):
    """Create HTML badge for status display"""
    colors = {
        'Completed': '#059669',
        'Pending': '#F59E0B', 
        'Partially Filled': '#EA580C',
        'Cancelled': '#DC2626',
        'Low Stock': '#F59E0B',
        'Out of Stock': '#DC2626',
        'Good Stock': '#059669'
    }
    
    color = colors.get(status, '#6B7280')
    
    return f"""
    <span style="
        background-color: {color}20;
        color: {color};
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid {color}40;
    ">
        {status}
    </span>
    """
