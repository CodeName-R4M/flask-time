import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from flask import render_template, request, jsonify

# --- Configuration ---
# Set matplotlib backend to Agg for non-GUI environments (required for Flask)
matplotlib.use("Agg")

# Path to the data source
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "finished.xlsx")

# --- Data Initialization ---
# Load the dataset into a global DataFrame
df = pd.read_excel(EXCEL_PATH)

# Pre-calculate common metrics
product_revenue = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
product_revenue_dict = product_revenue.to_dict()
total_revenue = round(df['Revenue'].sum(), 2)

# --- Core View Functions ---

def dodawork():
    """Renders the main dashboard template with initial data."""
    return render_template(
        "index.html",
        message="Revenue Charts",
        product_revenue=product_revenue_dict,
        total_revenue=total_revenue
    )

# --- Chart Generation Functions ---

def showrevchart():
    """Generates a bar chart showing Total Revenue by Product."""
    product_revenue = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(product_revenue.index, product_revenue.values, color='#3b82f6', edgecolor='#1d4ed8', alpha=0.8)
    
    ax.set_title('Total Revenue by Product', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Product', fontsize=12, labelpad=10)
    ax.set_ylabel('Revenue ($)', fontsize=12, labelpad=10)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save to buffer
    img = BytesIO()
    fig.savefig(img, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    img.seek(0)
    return img

def showregionchart():
    """Generates a bar chart showing Revenue by Region."""
    # Clean region names (e.g., replace placeholder 0s)
    df['Region'] = df['Region'].astype(str).str.replace("0", "UNKNOWN")
    region_revenue = df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
    region_revenue_dict = region_revenue.to_dict()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=list(region_revenue_dict.keys()),
        y=list(region_revenue_dict.values()),
        ax=ax,
        palette='Blues_d'
    )

    ax.set_title('Region Revenue', pad=20, fontsize=16, fontweight='bold')
    ax.set_xlabel('Region', fontsize=12, labelpad=10)
    ax.set_ylabel('Revenue', fontsize=12, labelpad=10)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save to buffer
    img = BytesIO()
    fig.savefig(img, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    img.seek(0)
    return img

def showregionpiechart():
    """Generates a pie chart showing Revenue distribution by Region."""
    region_revenue = df.groupby('Region')['Revenue'].sum()
    colors = sns.color_palette('pastel')[0:len(region_revenue)]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(
        region_revenue, 
        labels=region_revenue.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=colors, 
        wedgeprops={'edgecolor': 'white'}
    )
    ax.axis('equal')
    plt.title('Revenue Distribution by Region', pad=20, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save to buffer
    img = BytesIO()
    fig.savefig(img, format="png", dpi=150)
    plt.close(fig)
    img.seek(0)
    return img

def showstatuschart():
    """Generates a pie chart showing Revenue distribution by Order Status."""
    status_revenue = df.groupby('Status')['Revenue'].sum()
    colors = sns.color_palette('muted')[0:len(status_revenue)]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(
        status_revenue, 
        labels=status_revenue.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=colors, 
        wedgeprops={'edgecolor': 'white'}
    )
    ax.axis('equal')
    plt.title('Revenue Distribution by Status', pad=20, fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save to buffer
    img = BytesIO()
    fig.savefig(img, format="png", dpi=150)
    plt.close(fig)
    img.seek(0)
    return img

def moneyrevtrend():
    """Generates a line chart showing the Monthly Revenue Trend."""
    # Work on a copy to avoid polluting the global dataframe
    temp_df = df.copy()
    temp_df['Date'] = pd.to_datetime(temp_df['Date'], errors='coerce')
    temp_df['Month'] = temp_df['Date'].dt.to_period('M')
    monthly_rev = temp_df.groupby('Month')['Revenue'].sum().reset_index()
    monthly_rev['Month'] = monthly_rev['Month'].astype(str)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        monthly_rev['Month'], 
        monthly_rev['Revenue'], 
        marker='o', 
        linewidth=3, 
        color='#2563eb', 
        markersize=8, 
        markerfacecolor='white', 
        markeredgewidth=2
    )
    ax.fill_between(monthly_rev['Month'], monthly_rev['Revenue'], color='#2563eb', alpha=0.1)
    
    ax.set_title('Monthly Revenue Trend', fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel('Month', fontsize=12, labelpad=10)
    ax.set_ylabel('Revenue ($)', fontsize=12, labelpad=10)
    plt.xticks(rotation=45)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Remove chart borders for a cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    # Save to buffer
    img = BytesIO()
    fig.savefig(img, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    img.seek(0)
    return img

# --- Excel Data Functions ---

def showexcel():
    """Returns an HTML table of the first 5 rows of data."""
    display_df = df.drop(columns=['Month'], errors='ignore')
    return display_df.head().to_html(classes='editable-table', index=True)

def showexcelfull():
    """Returns an HTML table of the full dataset."""
    display_df = df.drop(columns=['Month'], errors='ignore')
    return display_df.to_html(classes='editable-table', index=True)

def editexcel():
    """
    Handles batch updates to the Excel file.
    Expects JSON: { "changes": { "row_index": { "column": "new_value" } }, "fetch_full": bool }
    """
    global total_revenue
    try:
        data = request.get_json(force=True)
        changes = data.get("changes", {})
        
        if not changes:
            return jsonify({"success": False, "error": "No changes provided"})

        # Apply each change to the in-memory DataFrame
        for row_idx_str, row_changes in changes.items():
            row_idx = int(row_idx_str)
            for col_name, new_val in row_changes.items():
                # Strict validation: Convert Revenue to float
                if col_name == 'Revenue':
                    try:
                        new_val = float(new_val)
                    except (ValueError, TypeError):
                        continue # Skip invalid numeric data
                # Strict validation: Ensure valid Date
                elif col_name == 'Date':
                    try:
                        pd.to_datetime(new_val)
                    except:
                        continue # Skip invalid date data
                
                df.at[row_idx, col_name] = new_val

        # Recalculate global total revenue metric
        total_revenue = round(df['Revenue'].sum(), 2)

        # Persist changes to the physical Excel file
        df.to_excel(EXCEL_PATH, index=False)

        # Prepare the updated HTML table for the frontend
        show_full = data.get("fetch_full", False)
        display_df = df.drop(columns=['Month'], errors='ignore')
        html_table = display_df.to_html(classes='editable-table', index=True) if show_full else display_df.head().to_html(classes='editable-table', index=True)

        return jsonify({
            "success": True, 
            "html": html_table,
            "total_revenue": total_revenue
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# --- Metadata ---

def available_charts():
    """Returns a list of available reports/charts for the frontend to render."""
    return [
        {"id": "revenue-chart", "name": "Revenue Chart"},
        {"id": "region-revenue-pie-chart", "name": "Region Revenue Pie Chart"},
        {"id": "status-revenue-pie-chart", "name": "Status Revenue Pie Chart"},
        {"id": "monthly-revenue-trend", "name": "Monthly Revenue Trend"},
        {"id": "show-excel", "name": "Show first 5 rows of Excel"},
        {"id": "show-excel-full", "name": "Show full Excel"}
    ]
