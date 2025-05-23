# Report Viewer Flask Application

A Flask application to read text files and display their organized contents on the web.

## Features

- Lists all available text reports from the reports directory
- Displays report contents with preserved formatting
- Simple and responsive user interface
- Error handling for file operations

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

1. Place your text report files in the `reports` directory (must have .txt extension)
2. Run the application:
   ```
   python app.py
   ```
3. Open your browser and navigate to `http://127.0.0.1:5000/`
4. Click on a report name to view its contents

## Adding New Reports

Simply add new .txt files to the `reports` directory. The application will automatically detect and list them on the home page.

## Customization

- Modify the templates in the `templates` directory to change the appearance
- Edit the CSS in the `layout.html` file to customize the styling

## License

This project is open source and available under the MIT License.