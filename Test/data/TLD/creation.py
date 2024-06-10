# 29.04.24

import httpx
import json
from bs4 import BeautifulSoup


# URL of the webpage containing the table
url = 'https://icannwiki.org/New_gTLD_Generic_Applications'


# List to store scraped data
data = []


# List of preference notes and registries
preference_note = ['DELEGATED', 'WITHDRAWN', '']
preference_registry = ['Verisign', 'KSregistry', 'KNET']


# Function to scrape new gTLD applications
def scrape_new_gtld_applications(url):

    # Send a GET request to the URL
    response = httpx.get(url)

    # Check if the response is successful
    if response.status_code == 200:

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the gTLD applications
        table = soup.find('table', class_='wikitable')

        # Check if the table is found
        if table:

            # Iterate over each row in the table, skipping the header row
            for row in table.find_all('tr')[1:]:
                columns = row.find_all('td')

                # Extract data from each column of the row
                application_id = columns[0].get_text(strip=True)
                tld = columns[1].get_text(strip=True)
                category = columns[2].get_text(strip=True)
                applicant = columns[3].get_text(strip=True)
                application_status = columns[4].get_text(strip=True)
                notes = columns[5].get_text(strip=True).split(" ")[0]

                # Check if the note is in the preference list
                if notes in preference_note:

                    # Check if the applicant is not in the preference registry list
                    if applicant not in preference_registry:

                        # Add the extracted data to the list
                        data.append({
                            'application_id': application_id,
                            'tld': tld,
                            'category': category,
                            'applicant': applicant,
                            'application_status': application_status,
                            'notes': notes
                        })
        else:
            print("Table not found on the page.")
    else:
        print("Failed to fetch the page.")


def main():

    # Run main functio
    scrape_new_gtld_applications(url)

    # Print the number of records scraped
    print(len(data))

    # Write the scraped data to a JSON file
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file)


if __name__ == '__main__':
    main()