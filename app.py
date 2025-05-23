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
    """Home page that displays all available reports"""
    # Initialize data dictionaries
    prisma_data = {'has_files': False}
    cisco_data = {'has_files': False}
    azure_data = {'has_files': False}

    # Check and load Prisma Access Egress IPs data
    prisma_csv = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.csv')
    prisma_edl = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.edl')

    if os.path.exists(prisma_csv) and os.path.exists(prisma_edl):
        prisma_data['has_files'] = True
        try:
            # Get file modification times
            prisma_data['csv_mod_time'] = datetime.datetime.fromtimestamp(os.path.getmtime(prisma_csv)).strftime('%b %d %Y %H:%M:%S')
            prisma_data['edl_mod_time'] = datetime.datetime.fromtimestamp(os.path.getmtime(prisma_edl)).strftime('%b %d %Y %H:%M:%S')

            # Read CSV file
            prisma_data['csv_data'] = []
            with open(prisma_csv, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    prisma_data['csv_data'].append(row)

            # Read EDL file
            prisma_data['edl_data'] = []
            with open(prisma_edl, 'r') as file:
                for line in file:
                    prisma_data['edl_data'].append(line.strip())
        except Exception as e:
            prisma_data['error'] = str(e)

    # Check and load Cisco Public IPs data
    cisco_csv = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.csv')
    cisco_xlsx = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.xlsx')
    cisco_log = os.path.join(REPORTS_FOLDER, 'RetrieveCiscoPublicIP.log')

    if os.path.exists(cisco_csv) and os.path.exists(cisco_xlsx):
        cisco_data['has_files'] = True
        try:
            # Get file modification times
            cisco_data['csv_mod_time'] = datetime.datetime.fromtimestamp(os.path.getmtime(cisco_csv)).strftime('%b %d %Y %H:%M:%S')
            cisco_data['xlsx_mod_time'] = datetime.datetime.fromtimestamp(os.path.getmtime(cisco_xlsx)).strftime('%b %d %Y %H:%M:%S')
            cisco_data['has_log_file'] = os.path.exists(cisco_log)
            if cisco_data['has_log_file']:
                cisco_data['log_mod_time'] = datetime.datetime.fromtimestamp(os.path.getmtime(cisco_log)).strftime('%b %d %Y %H:%M:%S')

            # Read CSV file
            cisco_data['csv_data'] = []
            with open(cisco_csv, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    cisco_data['csv_data'].append(row)
        except Exception as e:
            cisco_data['error'] = str(e)

    # Check and load Azure Public IP Objects data
    azure_csv = os.path.join(REPORTS_FOLDER, 'AzurePIPs.csv')

    if os.path.exists(azure_csv):
        azure_data['has_files'] = True
        try:
            # Get file modification time
            azure_data['csv_mod_time'] = datetime.datetime.fromtimestamp(os.path.getmtime(azure_csv)).strftime('%b %d %Y %H:%M:%S')

            # Read CSV file
            azure_data['csv_data'] = []
            with open(azure_csv, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    azure_data['csv_data'].append(row)
        except Exception as e:
            azure_data['error'] = str(e)

    return render_template('index.html', 
                          prisma_data=prisma_data, 
                          cisco_data=cisco_data, 
                          azure_data=azure_data)

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

@app.route('/all_ips')
def all_ips():
    """Display all IPs from all sources in a single table"""
    all_ips_data = []

    # Check and load Prisma Access Egress IPs data
    prisma_csv = os.path.join(REPORTS_FOLDER, 'PrismaAccessEgressIPs.csv')
    if os.path.exists(prisma_csv):
        try:
            with open(prisma_csv, 'r') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)  # Skip header row
                location_idx = headers.index("Location") if "Location" in headers else 0
                ip_idx = headers.index("egress IP") if "egress IP" in headers else 2

                for row in csv_reader:
                    if len(row) > max(location_idx, ip_idx):
                        name = row[location_idx]
                        ip = row[ip_idx]
                        all_ips_data.append({
                            'source': 'Prisma Access',
                            'name': name,
                            'ip': ip
                        })
        except Exception as e:
            print(f"Error loading Prisma Access data: {str(e)}")

    # Check and load Cisco Public IPs data
    cisco_csv = os.path.join(REPORTS_FOLDER, 'CiscoPublicIPs.csv')
    if os.path.exists(cisco_csv):
        try:
            with open(cisco_csv, 'r') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)  # Skip header row
                hostname_idx = headers.index("host-name") if "host-name" in headers else 1
                ip_idx = headers.index("interface-IP") if "interface-IP" in headers else 6

                for row in csv_reader:
                    if len(row) > max(hostname_idx, ip_idx):
                        name = row[hostname_idx]
                        ip_with_subnet = row[ip_idx]

                        # Handle multiple IPs separated by semicolons
                        if ';' in ip_with_subnet:
                            ips = ip_with_subnet.split(';')
                            for ip_entry in ips:
                                # Extract IP without subnet
                                ip = ip_entry.strip().split('/')[0]
                                all_ips_data.append({
                                    'source': 'Cisco',
                                    'name': name,
                                    'ip': ip
                                })
                        else:
                            # Extract IP without subnet
                            ip = ip_with_subnet.split('/')[0]
                            all_ips_data.append({
                                'source': 'Cisco',
                                'name': name,
                                'ip': ip
                            })
        except Exception as e:
            print(f"Error loading Cisco data: {str(e)}")

    # Check and load Azure Public IP Objects data
    azure_csv = os.path.join(REPORTS_FOLDER, 'AzurePIPs.csv')
    if os.path.exists(azure_csv):
        try:
            with open(azure_csv, 'r') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)  # Skip header row
                name_idx = headers.index("name") if "name" in headers else 0
                ip_idx = headers.index("ipAddress") if "ipAddress" in headers else 1

                for row in csv_reader:
                    if len(row) > max(name_idx, ip_idx):
                        name = row[name_idx]
                        ip = row[ip_idx]
                        all_ips_data.append({
                            'source': 'Azure',
                            'name': name,
                            'ip': ip
                        })
        except Exception as e:
            print(f"Error loading Azure data: {str(e)}")

    return render_template('all_ips.html', all_ips_data=all_ips_data)

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
