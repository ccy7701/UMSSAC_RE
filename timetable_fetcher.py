import json
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Define the main URL and the target file path for saving the XML
url = 'https://jadual.ums.edu.my/KuliahKK/finder.html'
downloads_path = os.path.expanduser('~/Downloads/all_subjects_data.json')
response = requests.get(url)

# Check for successful fetch
if response.status_code == 200:
    print("(PASS) INIT: Fetch successful")

    # Parse the main page HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the iframe and extract its source URL
    iframe = soup.find('iframe')
    if iframe and iframe.get('src'):
        print("(PASS) IFRAME: iframe and source found")
        iframe_src = iframe['src']
        full_iframe_url = urljoin(url, iframe_src)

        # Fetch the iframe's HTML
        iframe_response = requests.get(full_iframe_url)

        if iframe_response.status_code == 200:
            print("(PASS) IFRAME: Fetch successful")

            # Parse the iframe's HTML
            iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')

            # Select all anchor elements with class 'ttlink'
            all_anchor_tags = iframe_soup.select('a.ttlink')

            # Prepare a list to store the links and their texts
            all_subjects_data = []

            # Regular expression to match the subject format
            subject_pattern = re.compile(r'^(?P<code>[A-Z]{2}\d{5})\s+(?P<name>.+)$')

            # Set to store unique subject codes and avoid duplicates
            unique_subjects = set()

            # Loop through each anchor tag and get the href and text
            for anchor in all_anchor_tags:
                href = urljoin(url, anchor['href'])
                text = anchor.get_text(strip=True)

                # Check if the text represents a module
                if "Module:" in text:
                    # Remove the "Module:" prefix and split the subjects
                    subject_part = text.split("Module:")[1].strip()

                    # Extract SubjectCode and SubjectName using regex
                    subjects = subject_part.split(',')

                    for subject in subjects:
                        match = subject_pattern.match(subject.strip())
                        if match:
                            subject_code = match.group('code')
                            subject_name = match.group('name')

                            # Check if this subject code is already in the set
                            if subject_code not in unique_subjects:
                                unique_subjects.add(subject_code)

                                # Append to the list
                                all_subjects_data.append({
                                    "subject_code": subject_code,
                                    "subject_name": subject_name,
                                    "href": href
                                })

            # Save the list to a JSON file
            with open(downloads_path, 'w', encoding='utf-8') as f:
                json.dump(all_subjects_data, f, ensure_ascii=False, indent=4)

            print(f"(PASS) JSON: File saved successfully at {downloads_path}")
        else:
            print(f"Failed to fetch iframe content. Status code: {iframe_response.status_code}")
    else:
        print("Iframe not found or missing 'src' attribute.")
else:
    print(f"Failed to fetch main page. Status code: {response.status_code}")
