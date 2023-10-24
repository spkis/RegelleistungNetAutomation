# RegelleistungNetAutomation

## Overview
This script automates the process of downloading and converting XLSX files from the Regelleistung website. It's written in Python and uses libraries like `pandas` and `requests`.

## Requirements
- Python 3.x
- pandas
- requests

## How to Use
1. Clone this repository.
2. Install the required Python packages.
3. Run `regelleistung_convert.py`.

### Steps Explained
- The script first checks if a folder named `results_xlsx` exists; if not, it creates one.
- It then downloads an XLSX file from the Regelleistung website and saves it in the `results_xlsx` folder.
- Finally, the script converts the XLSX file to a CSV format and saves it as `output.csv`.

## Troubleshooting
If you encounter any issues, the script will print out error messages to help you understand what went wrong.

## Telegraf Import
After the files have been placed into the telegraf_import folder, a telegraf process is supposed to pick up the files and read them into an influxDB. 
