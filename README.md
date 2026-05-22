# IP Reports Dashboard

A Flask web application that displays and manages various IP address reports including Prisma Access Egress IPs and Cloud Public IP Objects. The application provides interactive tables with advanced filtering, sorting, and pagination capabilities.

## Features

- **Unified Dashboard**: View all reports in a single interface with tab navigation
- **Multiple Report Types**:
  - Prisma Access Egress IPs (CSV and EDL formats)
  - Cloud Public IP Objects (CSV format)
  - Combined view of all IPs from both sources
- **Interactive Tables**:
  - Sorting: Click on column headers to sort data
  - Filtering: Click on funnel icons to filter columns
  - Pagination: Configurable page sizes with synchronized pagination across tables
- **Export Options**: Export table data to CSV, Excel, PDF, or print directly
- **Direct URL Access**: Bookmark specific report views with direct URL links
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. Clone this repository
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your report files in the `reports` directory:
- `PrismaAccessEgressIPs.csv` and `PrismaAccessEgressIPs.edl` for Prisma Access reports
- `CloudEgressIPs.csv` for Cloud reports

2. Run the application locally (development):
   ```
   python app.py
   # or
   python wsgi.py
   ```

3. Open your browser and navigate to `http://127.0.0.1:5000/`

## Deployment (Apache mod_wsgi)

In production, do not call `app.run()` directly. Instead, have Apache import the WSGI callable named `application` from `wsgi.py`.

Example Apache config:
```
ServerName egressreport.example.com
DocumentRoot /path/to/egressReport

WSGIDaemonProcess egressreport python-home=/path/to/egressReport/.venv
WSGIProcessGroup egressreport
WSGIScriptAlias / /path/to/egressReport/wsgi.py

<Directory "/path/to/egressReport">
    Require all granted
</Directory>
```

Notes:
- Ensure the virtualenv path in `python-home` is correct for your server.
- `wsgi.py` already ensures the project root is on `sys.path` and exposes `application`.
- After deploying or updating code, reload Apache.
- Health check endpoint: `GET /health` returns `200 OK` when the app is loaded.

## URL Routes

The application supports direct access to specific reports via URL:

- `/` - All Reports view (default)
- `/prismaaccess` - Prisma Access Egress IPs report
- `/cloud` - Cloud Public IP Objects report
- `/allips` - Combined view of all IPs

## Table Features

### Filtering

1. Click the funnel icon (⏷) in any column header to reveal the filter input
2. Type to filter the table by that column
3. Select from the dropdown list to auto-complete filtering
4. The filter will remain visible as long as a filter is applied

### Sorting

Click on any column header to sort by that column. Click again to toggle between ascending and descending order.

### Pagination

- Use the pagination controls at the bottom of each table to navigate between pages
- Change the number of entries displayed per page using the dropdown menu
- Page size is synchronized across all tables for consistent viewing

### Exporting

Use the buttons at the top of each table to export data:
- Copy: Copy table data to clipboard
- CSV: Export as CSV file
- Excel: Export as Excel file
- PDF: Export as PDF document
- Print: Print the table

## File Formats

The application supports the following file formats:

- **CSV**: Comma-separated values for all report types
- **EDL**: External Dynamic List format for Prisma Access Egress IPs

## Customization

- Modify the templates in the `templates` directory to change the appearance
- Edit the CSS in the `layout.html` file to customize the styling
- Adjust table configurations in the JavaScript section of `index.html`

## License

This project is open source and available under the MIT License.
