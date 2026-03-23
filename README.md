# flask-time

A Flask web application for generating revenue analytics charts from Excel data.

## Overview
This project provides a web interface to visualize revenue data stored in an Excel file. It serves various analytical charts like bar charts and pie charts to represent revenue metrics.

## Features
- Display total revenue and revenue distribution by product
- Generate charts for order status distribution and regional revenue breakdown
- Show a monthly revenue trend line chart

## Tech Stack / Built With
- Python
- Flask
- Pandas
- Matplotlib
- Seaborn

## Installation & Setup
```bash
git clone https://github.com/CodeName-R4M/flask-time.git
cd flask-time
pip install -r requirements.txt
python app.py
```

## Usage
```python
# Run the Flask application
python app.py
```

## Project Structure
```
├── .gitattributes
├── __pycache__
├── analysis.py
├── app.py
├── finished.xlsx
├── flask-time
├── py-learn
├── py-mid
├── static
└── templates
```

## Contributing
Contributions are welcome. Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License.