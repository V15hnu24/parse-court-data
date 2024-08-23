# Court Case Processing Application

This application processes court-related HTML files to extract relevant case details and generate CSV files. It supports multithreading to improve the efficiency of processing large datasets.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Setting Up the Application](#setting-up-the-application)
4. [Handling SSL Certificates](#handling-ssl-certificates)
5. [Running the Application](#running-the-application)
6. [File Structure](#file-structure)
7. [Contributing](#contributing)
8. [License](#license)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.11 or later
- pip (Python package installer)
- A virtual environment tool (optional but recommended)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/court-case-processing.git
cd court-case-processing
```

### Step 2: Set Up a Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Step 3: Install Required Python Packages

```bash
pip install -r requirements.txt
```

This will install all necessary dependencies, including `requests`, `beautifulsoup4`, `concurrent.futures`, and other libraries required by the application.

## Setting Up the Application

### Step 1: Set Up Request Headers

If your application needs to make HTTP requests (for example, to fetch court case data), you should configure the necessary headers in your application code.

```python
import requests

headers = {
    'User-Agent': 'Your User Agent String',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = requests.get('https://example.com/api/court-cases', headers=headers)
```

### Step 2: Handle SSL Certificates

If you're dealing with SSL certificates (e.g., for HTTPS requests), and you encounter issues related to certificate verification, you may need to install or update your SSL certificates.

#### MacOS

Create a script named `install_certificates.command` to update your SSL certificates:

```bash
#!/bin/bash
/Applications/Python\ 3.x/Install\ Certificates.command
```

Make this script executable:

```bash
chmod +x install_certificates.command
```

Run the script to install the certificates:

```bash
./install_certificates.command
```

#### Windows

For Windows, ensure your `requests` library uses the correct certificates by pointing to the proper certificate bundle in your Python installation:

```python
import requests

response = requests.get('https://example.com', verify='path/to/your/cacert.pem')
```

## Running the Application

### Step 1: Process the Court Files

You can start processing the court-related HTML files by running the main script. Ensure all necessary input files (HTML files) are placed in the correct directory before executing the script.

```bash
python main.py
```

### Step 2: Multithreading

The application supports multithreading to speed up processing. This is handled automatically within the `main.py` script using `concurrent.futures`. You don't need to configure anything manually.

## File Structure

The repository is structured as follows:

```
court-case-processing/
├── csv_files/                   # Output directory for generated CSV files
├── html_files/                  # Input directory containing HTML files
├── main.py                      # Main script for processing the court files
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── install_certificates.command # SSL certificate installation script (MacOS)
```

- **csv_files/**: This directory will contain the generated CSV files after processing.
- **html_files/**: Place all the court-related HTML files in this directory before running the script.
- **main.py**: The main processing script that reads HTML files, processes them, and outputs CSV files.
- **requirements.txt**: Lists all Python dependencies required by the project.
- **install_certificates.command**: A helper script to install SSL certificates on MacOS.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have suggestions, bug fixes, or improvements.

### How to Contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.