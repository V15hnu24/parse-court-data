import re
import urllib.request
import json
import csv
import os
import ssl
import pandas as pd
from bs4 import BeautifulSoup
import certifi
import concurrent.futures
import logging

logging.basicConfig(
    filename="app.log",  # Log file path
    filemode="a",  # Append mode; 'w' would overwrite the file
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,  # Set the logging level
)

def html_table_to_csv(html_file, csv_file):
    logging.debug(f"Processing HTML file: {html_file}")
    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        tables = soup.find_all("table")
        if not tables:
            logging.warning(f"No tables found in the HTML file: {html_file}")
            return

        table = tables[0]
        headers = [header.get_text(strip=True) for header in table.find_all("th")]
        if not headers:
            headers = [
                f"Column {i+1}"
                for i in range(len(table.find_all("tr")[0].find_all("td")))
            ]

        rows = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:
                rows.append(row_data)

        max_columns = max(len(row) for row in rows)
        if len(headers) != max_columns:
            headers = [f"Column {i+1}" for i in range(max_columns)]

        df = pd.DataFrame(rows, columns=headers)
        df["Column 2"] = df["Column 2"].str.split().str[0]

        df.to_csv(csv_file, index=False)
        logging.info(f"Data has been written to {csv_file}")
    except Exception as e:
        logging.error(f"Error processing HTML to CSV for {html_file}: {e}")

def html_csv_handler(html_file):
    csv_file = f"convert/{html_file}.csv"
    html_file = f"html/{html_file}.html"
    html_table_to_csv(html_file, csv_file)


def update_item_numbers(output_file, converted_csv_files):
    logging.debug(f"Updating item numbers in {output_file}")
    try:
        output_df = pd.read_csv(output_file)

        for csv_file in converted_csv_files:
            logging.debug(f"Processing converted CSV file: {csv_file}")
            converted_df = pd.read_csv(csv_file)

            for index, row in output_df.iterrows():
                case_no = re.escape(row["Case No"])
                match_rows = converted_df[
                    converted_df["Column 2"].str.contains(case_no, na=False)
                ]
                if not match_rows.empty:
                    output_df.at[index, "Item No"] = match_rows["Column 1"].tolist()[0]

        output_df.to_csv(output_file, index=False)
        logging.info(f"Updated item numbers in {output_file}")
    except Exception as e:
        logging.error(f"Error updating item numbers: {e}")


def identify_main_numbers(html_content):
    pattern = r"WP(?:\(PIL\))?\/\d+\/\d{4}"
    matches = re.findall(pattern, html_content)
    unique_matches = list(set(matches))
    return unique_matches


def fetch_case_details(case_number):
    logging.debug(f"Fetching case details for case number: {case_number}")
    base_url = "https://services.tshc.gov.in/Hcdbs/caseDetails.jsp?casedet="
    url = base_url + case_number.replace("/", "%2F")
    context = ssl.create_default_context(cafile=certifi.where())

    try:
        with urllib.request.urlopen(url, context=context, timeout=10) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        logging.error(f"Error fetching case details for {case_number}: {e}")
        return None


def process_case_details(case_number, court_number, case_details):
    if not isinstance(case_details, list):
        logging.warning("Unexpected data format.")
        return None

    officers_result = []
    petitioners = " "
    subject = " "
    respondentAdv = " "
    hJudge = " "

    with open(f'csv_files/{court_number}.csv', mode="w", newline="") as output_csv:
        csv_writer = csv.writer(output_csv)
        csv_writer.writerow(
            ["Sl.No", "Court No", "Item No", "Case No", "Respondant Name"]
        )
        all_officers = []
        case = case_details[0]
        
        subject = case.get("prayer")
        if len(case.get("orderdetails")) > 0:
            hJudge = case.get("orderdetails")[0].get("judgename")
        respondentAdv = case.get("respondentadv")
        
        pet_details = case.get("petdetails")
        pnames = []

        for pet in pet_details:
            pnames.append(pet.get("pname"))
        petitioners = ", ".join(set(pnames))

        district = case.get("district", "").lower()
        if district != "hyderabad":
            return None

        res_details = case.get("resdetails")
        officers = []

        for res in res_details:
            rname = res.get("rname", "").lower()
            address = res.get("address", "").lower()

            all_officers.append(rname + address)
            if "collector" in rname:
                officers.append("District Collector Hyderabad")

            if any(mro in rname for mro in ["tahsildar", "tahshildhar"]) and any(
                area in address
                for area in [
                    "saidabad",
                    "khairatabad",
                    "amberpet",
                    "ameerpet",
                    "shaikpet",
                    "himayatnagar",
                    "maredpally",
                    "ramgopalpet",
                    "bahadurpura",
                    "bandlaguda",
                    "golconda",
                    "asif nagar",
                    "secunderabad",
                    "musheerabad",
                    "tirumalagiri",
                    "charminar",
                    "nampally"
                ]
            ):
                officers.append(f"Tahsildar {address.split(',')[0].capitalize()}")

            if any(
                officer in rname
                for officer in [
                    "mandal revenue officer",
                    "greater hyderabad municipal corporation",
                    "rdo",
                    "revenue divisional officer",
                    "the mandal revenue officer",
                    "the rdo",
                    "the revenue divisional officer",
                    "the greater hyderabad municipal corporation",
                ]
            ):
                officers.append(rname.capitalize() + " " + address)

        ghmc_count = sum(
            1
            for officer in officers
            if any(
                ghmc in officer.lower()
                for ghmc in ["greater hyderabad municipal corporation"]
            )
        )
        collector_count = sum(
            1 for officer in officers if "District Collector" in officer
        )        

        if len(officers) > 0:
            if len(officers) == ghmc_count:
                return None
            if len(officers) == ghmc_count + collector_count:
                return None
            officers_result.append(", ".join(set(officers)))

        csv_writer.writerow([1, court_number, 1, case_number, ", ".join(all_officers) ])
    print(hJudge, petitioners, officers_result[0] if officers_result else None, subject, respondentAdv)
    return hJudge, petitioners, officers_result[0] if officers_result else None, subject, respondentAdv

def generate_csv_for_court(court_number, html_content, writer):
    logging.debug(f"Generating CSV for court number {court_number}")
    sl_no_counter = 0
    case_numbers = identify_main_numbers(html_content)

    for i, case_number in enumerate(case_numbers, start=1):
        # case_details = case_details_map.get(case_number)
        case_details = fetch_case_details(case_number)
        if case_details:
            result = process_case_details(case_number, court_number, case_details)

            if result is not None:
                h_judge, petitioner_name, respondent_name, subject, respondent_adv = result
                print(respondent_name)
                if respondent_name is not None:
                    sl_no_counter += 1
                    writer.writerow(
    #["Sl.No", "Court No", "Item No", "Hon'ble Justice", "Case No", "Petitioner Name", "Respondant Name", "Subject", "Respondent Advocate", ]
                        [sl_no_counter, court_number, i, h_judge, case_number, petitioner_name, respondent_name, subject, respondent_adv]
                    )
    logging.debug(f"Finished generating CSV for court number {court_number}")


def process_court(court_number):
    logging.debug(f"Processing court {court_number}")
    html_csv_handler(f"court{court_number}")

    html_file = f"html/court{court_number}.html"
    output_file = f"output/court{court_number}.csv"

    if os.path.exists(html_file):
        with open(html_file, "r") as file:
            html_content = file.read()

        with open(output_file, mode="w", newline="") as output_csv:
            writer = csv.writer(output_csv)
            writer.writerow(
                ["Sl.No", "Court No", "Item No", "Hon'ble Justice", "Case No", "Petitioner Name", "Respondant Name", "Subject", "Respondent Advocate"]
            )
            generate_csv_for_court(court_number, html_content, writer)

    logging.debug(f"Finished processing court {court_number}")
    return output_file

def read_court_numbers(file_path):
    with open(file_path, 'r') as file:
        court_numbers = [int(line.strip()) for line in file if line.strip().isdigit()]
    return court_numbers

def main():
    # Read court numbers from file
    court_numbers = read_court_numbers('court_numbers.txt')
    output_file = "case_details.csv"

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(process_court, court_number)
            for court_number in court_numbers
        ]
        output_files = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]

    # Filter out any None or empty files
    output_files = [
        file
        for file in output_files
        if os.path.exists(file) and os.path.getsize(file) > 0
    ]

    if output_files:
        # After processing all courts, combine the results into a single CSV file
        combined_df = pd.concat([pd.read_csv(file) for file in output_files])
        combined_df.to_csv(output_file, index=False)
        logging.info(f"Combined CSV saved to {output_file}")
    else:
        logging.warning("No valid CSV files to combine.")

    converted_csv_files = [
        f"convert/court{court_number}.csv" for court_number in court_numbers
    ]
    update_item_numbers(output_file, converted_csv_files)


def dev():
    print(process_case_details(1, 1, fetch_case_details("WP/16785/2024")))


if __name__ == "__main__":
    main()
    # dev()
