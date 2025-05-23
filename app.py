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
@app.route('/<report_type>')
def index(report_type=None):
    """Home page that displays all available reports or a specific report type"""
    # Initialize data dictionaries
    prisma_data = {'has_files': False}
    cisco_data = {'has_files': False}
    azure_data = {'has_files': False}
    all_ips_data = []

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
                headers = next(csv_reader)  # Get header row
                prisma_data['csv_data'].append(headers)

                # Find indices for location and IP
                location_idx = headers.index("Location") if "Location" in headers else 0
                ip_idx = headers.index("egress IP") if "egress IP" in headers else 2

                for row in csv_reader:
                    prisma_data['csv_data'].append(row)

                    # Add to all_ips_data
                    if len(row) > max(location_idx, ip_idx):
                        name = row[location_idx]
                        ip = row[ip_idx]
                        all_ips_data.append({
                            'source': 'Prisma Access',
                            'name': name,
                            'ip': ip
                        })

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
                headers = next(csv_reader)  # Get header row
                cisco_data['csv_data'].append(headers)

                # Find indices for hostname and IP
                hostname_idx = headers.index("host-name") if "host-name" in headers else 1
                ip_idx = headers.index("interface-IP") if "interface-IP" in headers else 6

                for row in csv_reader:
                    cisco_data['csv_data'].append(row)

                    # Add to all_ips_data
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
                headers = next(csv_reader)  # Get header row
                azure_data['csv_data'].append(headers)

                # Find indices for name and IP
                name_idx = headers.index("name") if "name" in headers else 0
                ip_idx = headers.index("ipAddress") if "ipAddress" in headers else 1

                for row in csv_reader:
                    azure_data['csv_data'].append(row)

                    # Add to all_ips_data
                    if len(row) > max(name_idx, ip_idx):
                        name = row[name_idx]
                        ip = row[ip_idx]
                        all_ips_data.append({
                            'source': 'Azure',
                            'name': name,
                            'ip': ip
                        })
        except Exception as e:
            azure_data['error'] = str(e)

    # Map URL parameter to report ID used in the template
    active_report = 'all'  # Default to 'all' (All Reports)
    if report_type:
        if report_type.lower() in ['prismaaccess', 'prisma']:
            active_report = 'prisma'
        elif report_type.lower() in ['cisco', 'ciscoips']:
            active_report = 'cisco'
        elif report_type.lower() in ['azure', 'azureips']:
            active_report = 'azure'
        elif report_type.lower() in ['allips', 'all_ips']:
            active_report = 'allips'

    return render_template('index.html', 
                          prisma_data=prisma_data, 
                          cisco_data=cisco_data,
                          azure_data=azure_data,
                          all_ips_data=all_ips_data,
                          active_report=active_report)

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

# Route for Prisma Access Egress IPs has been removed as it is now integrated into the main dashboard

# Route for Cisco Public IPs has been removed as it is now integrated into the main dashboard

# Route for Azure Public IP Objects has been removed as it is now integrated into the main dashboard

# Route for All IPs has been removed as it is now integrated into the main dashboard

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
