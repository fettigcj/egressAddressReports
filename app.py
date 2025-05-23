from flask import Flask, render_template, request, redirect, url_for
import os

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
    
    return render_template('index.html', reports=reports)

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

if __name__ == '__main__':
    app.run(debug=True)