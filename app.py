from flask import Flask, send_file, jsonify
from analysis import dodawork, showrevchart, showstatuschart, showregionpiechart, moneyrevtrend, showexcel, showexcelfull, editexcel, available_charts

# Initialize Flask application
app = Flask(__name__)

# --- Main Routes ---

@app.route("/")
def home():
    """Main dashboard entry point."""
    return dodawork()

@app.post("/")
def post_root():
    """Generic POST endpoint for root (placeholder)."""
    return "POST request received"

# --- API Endpoints: Analytics Charts ---

@app.route("/revenue-chart")
def revenue_chart():
    """Serves the Product Revenue bar chart as a PNG image."""
    img = showrevchart()
    return send_file(img, mimetype="image/png")

@app.route("/status-revenue-pie-chart")
def status_revenue_pie_chart_route():
    """Serves the Order Status distribution pie chart as a PNG image."""
    img = showstatuschart()
    return send_file(img, mimetype="image/png")

@app.route("/region-revenue-pie-chart")
def region_revenue_pie_chart_route():
    """Serves the Regional Revenue distribution pie chart as a PNG image."""
    img = showregionpiechart()
    return send_file(img, mimetype="image/png")

@app.route("/monthly-revenue-trend")
def monthly_revenue_trend_route():
    """Serves the Monthly Revenue Trend line chart as a PNG image."""
    img = moneyrevtrend()
    return send_file(img, mimetype="image/png")

# --- API Endpoints: Excel Data ---

@app.route("/show-excel")
def show_excel_route():
    """Returns HTML for the first 5 rows of the Excel data."""
    return showexcel()

@app.route("/show-excel-full")
def show_excel_full_route():
    """Returns HTML for the entire Excel dataset."""
    return showexcelfull()

@app.route("/edit-excel", methods=["POST"])
def edit_excel_route():
    """Receives batch cell edits and updates the Excel file."""
    return editexcel()

# --- Metadata Endpoints ---

@app.route("/charts")
def get_charts():
    """Returns a JSON list of all available reports/charts for the frontend UI."""
    return jsonify(available_charts())

# --- App Entry Point ---

if __name__ == "__main__":
    # Start the Flask development server
    app.run(debug=True)
