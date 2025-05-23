from flask import Flask, render_template, request, redirect, url_for
import os
import csv
import datetime

app = Flask(__name__)

# Configuration
REPORTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
# Create reports directory if it doesn't exist
os.makedirs(REPORTS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Home page that lists all available reports"""
    # Get all text files from the reports directory
    reports = []
    if os.path.exists(REPORTS_FOLDER):
        for filename in os.listdir(REPORTS_FOLDER):
            if filename.endswith('.txt'):
                reports.append(filename)

    # Check if PrismaAccessEgressIPs files exist
    prisma_csv = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.csv')
    prisma_edl = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.edl')

    has_prisma_files = os.path.exists(prisma_csv) and os.path.exists(prisma_edl)

    # Check if CiscoPublicIPs files exist
    cisco_csv = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.csv')
    cisco_xlsx = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.xlsx')

    has_cisco_files = os.path.exists(cisco_csv) and os.path.exists(cisco_xlsx)

    # Check if AzurePIPs file exists
    azure_csv = os.path.join(REPORTS_FOLDER, 'AzurePIPs.csv')

    has_azure_files = os.path.exists(azure_csv)

    return render_template('index.html', reports=reports, has_prisma_files=has_prisma_files, has_cisco_files=has_cisco_files, has_azure_files=has_azure_files)

@app.route('/report/<filename>')
def view_report(filename):
    """Display the contents of a specific report"""
    file_path = os.path.join(REPORTS_FOLDER, filename)

    # Check if file exists and is a text file
    if not os.path.exists(file_path) or not filename.endswith('.txt'):
        return redirect(url_for('index'))

    # Read and organize the report content
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Split content into lines for better organization
        lines = content.split('\n')

        return render_template('report.html', filename=filename, lines=lines)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/prisma_access_egress_ips')
def prisma_access_egress_ips():
    """Display the Prisma Access Egress IPs in a similar fashion to oldReport.html"""
    csv_path = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.csv')
    edl_path = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.edl')

    # Check if files exist
    if not os.path.exists(csv_path) or not os.path.exists(edl_path):
        return redirect(url_for('index'))

    try:
        # Get file modification times
        csv_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(csv_path)).strftime('%b %d %Y %H:%M:%S')
        edl_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(edl_path)).strftime('%b %d %Y %H:%M:%S')

        # Read CSV file
        csv_data = []
        with open(csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        # Read EDL file
        edl_data = []
        with open(edl_path, 'r') as file:
            for line in file:
                edl_data.append(line.strip())

        return render_template('prisma_access_egress_ips.html', 
                              csv_data=csv_data, 
                              edl_data=edl_data,
                              csv_mod_time=csv_mod_time,
                              edl_mod_time=edl_mod_time)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/cisco_public_ips')
def cisco_public_ips():
    """Display the Cisco Public IPs data with download links for CSV and XLSX"""
    csv_path = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.csv')
    xlsx_path = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.xlsx')
    log_path = os.path.join(REPORTS_FOLDER, 'RetrieveCiscoPublicIP.log')

    # Check if files exist
    if not os.path.exists(csv_path) or not os.path.exists(xlsx_path):
        return redirect(url_for('index'))

    try:
        # Get file modification times
        csv_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(csv_path)).strftime('%b %d %Y %H:%M:%S')
        xlsx_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(xlsx_path)).strftime('%b %d %Y %H:%M:%S')
        log_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(log_path)).strftime('%b %d %Y %H:%M:%S') if os.path.exists(log_path) else "N/A"

        # Read CSV file
        csv_data = []
        with open(csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        return render_template('cisco_public_ips.html',
                              csv_data=csv_data,
                              csv_mod_time=csv_mod_time,
                              xlsx_mod_time=xlsx_mod_time,
                              log_mod_time=log_mod_time,
                              has_log_file=os.path.exists(log_path))
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/azure_public_ips')
def azure_public_ips():
    """Display the Azure Public IP Objects data with download link for CSV"""
    csv_path = os.path.join(REPORTS_FOLDER, 'AzurePIPs.csv')

    # Check if file exists
    if not os.path.exists(csv_path):
        return redirect(url_for('index'))

    try:
        # Get file modification time
        csv_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(csv_path)).strftime('%b %d %Y %H:%M:%S')

        # Read CSV file
        csv_data = []
        with open(csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                csv_data.append(row)

        return render_template('azure_public_ips.html',
                              csv_data=csv_data,
                              csv_mod_time=csv_mod_time)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/download/<file_type>')
def download_file(file_type):
    """Serve the file for download"""
    if file_type == 'prisma_csv':
        file_path = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.csv')
        return open(file_path, 'r').read(), 200, {'Content-Type': 'text/csv'}
    elif file_type == 'prisma_edl':
        file_path = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.edl')
        return open(file_path, 'r').read(), 200, {'Content-Type': 'text/plain'}
    elif file_type == 'cisco_csv':
        file_path = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.csv')
        return open(file_path, 'r').read(), 200, {'Content-Type': 'text/csv'}
    elif file_type == 'cisco_xlsx':
        file_path = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.xlsx')
        with open(file_path, 'rb') as f:
            data = f.read()
        return data, 200, {'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
    elif file_type == 'cisco_log':
        file_path = os.path.join(REPORTS_FOLDER, 'RetrieveCiscoPublicIP.log')
        return open(file_path, 'r').read(), 200, {'Content-Type': 'text/plain'}
    elif file_type == 'azure_csv':
        file_path = os.path.join(REPORTS_FOLDER, 'AzurePIPs.csv')
        return open(file_path, 'r').read(), 200, {'Content-Type': 'text/csv'}

if __name__ == '__main__':
    app.run(debug=True)
