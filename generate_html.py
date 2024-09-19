import requests
import base64
import json
from datetime import date, datetime


def _get_court_codes(court_data):
    court_codes = [court["court_code"] for court in court_data]
    return court_codes


def _get_updated_date():
    session = requests.Session()
    get_date_url = "https://services.tshc.gov.in/Hcdbs/getdates.jsp?listtype=D"
    response = session.get(get_date_url)
    content = response.content.decode("utf-8")
    dates = content.split("@")
    cleaned_dates = [dt_str.strip() for dt_str in dates]
    today = date.today()
    valid_dates = [
        datetime.strptime(dt_str, "%Y-%m-%d").date()
        for dt_str in cleaned_dates
        if dt_str
        and dt_str.strip()
        and datetime.strptime(dt_str, "%Y-%m-%d").date() >= today
    ]
    return str(valid_dates[0])


def generate_html_files(date):
    # 1. Start the session
    session = requests.Session()
    start_url = "https://services.tshc.gov.in/Hcdbs/search.do"
    session.get(start_url)

    # 2. Fetch the list of courts for a particular date
    court_list_url = "https://services.tshc.gov.in/Hcdbs/searchdates.do"
    court_list_payload = {"causelisttype": "D"}
    session.post(court_list_url, data=court_list_payload)

    # 3. Get court numbers for a specific date
    court_numbers_url = "https://services.tshc.gov.in/Hcdbs/searchtypeinput.do"
    court_numbers_payload = {"listdate": date, "caset": "courtsearch"}
    session.post(court_numbers_url, data=court_numbers_payload)

    # 4. Get the court list (base64 encoded)
    court_list_api_url = "https://services.tshc.gov.in/Hcdbs/courtlist.jsp"
    court_list_params = {"listtype1": "D", "listdate1": "2024-09-04"}
    court_list_response = session.get(
        court_list_api_url, params=court_list_params
    )

    # Decode the base64 response to JSON
    court_list_json = base64.b64decode(court_list_response.text)
    courts = court_list_json.decode("utf-8")

    # Assuming we're interested in the first court, extract the court_code
    court_data = json.loads(courts)
    court_codes = _get_court_codes(court_data)

    for court_code in court_codes:

        # 5. Select the court number and fetch the cause list
        cause_list_url = "https://services.tshc.gov.in/Hcdbs/searchtype.do"
        cause_list_payload = {"court": court_code, "listtype": "courtsearch"}
        session.post(cause_list_url, data=cause_list_payload)

        # 6. Retrieve the cause list HTML for the selected court and date
        final_cause_list_url = (
            "https://services.tshc.gov.in/Hcdbs/cause_list.jsp"
        )
        cause_list_html_response = session.get(final_cause_list_url)

        # 7. Save the final HTML content to a file
        with open(
            f"html/cause_list_{court_code}.html", "w", encoding="utf-8"
        ) as file:
            file.write(cause_list_html_response.text)

        print(f"Cause list saved as 'cause_list_{court_code}.html'")


if __name__ == "__main__":
    tom_date = _get_updated_date()
    print("Generating htmls for the date: ", tom_date)
    generate_html_files(tom_date)

