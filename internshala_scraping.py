import requests
from bs4 import BeautifulSoup
import json

def safe_get_text(element, strip=True):
    return element.get_text(strip=strip) if element else 'N/A'

def save_data_to_file(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving data: {e}")


def fetch_job_listings(page=1):
    url = f"https://internshala.com/internships_ajax/work-from-home-artificial-intelligence-ai,data-science,machine-learning-internships-in-mumbai,navi-mumbai,pune/page-{page}/"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["internship_list_html"]
        soup = BeautifulSoup(data, 'html.parser')
        
        job_cards = soup.find_all('div', class_='internship_meta')
        
        job_listings = []
        job_listings_json = {}
        
        for job in job_cards:
            try:
                job_title = safe_get_text(job.find('h3', class_='job-internship-name'))
                company_name = safe_get_text(job.find('p', class_='company-name'))
                company_logo_url = job.find('img')['src'] if job.find('img') else 'N/A'
                location_element = job.find('div', class_='locations').find('a') if job.find('div', class_='locations') else None
                location = safe_get_text(location_element)
                duration_element = job.find('div', class_='row-1-item', text='6 Months').find_next_sibling('span') if job.find('div', class_='row-1-item', text='6 Months') else None
                duration = safe_get_text(duration_element)
                stipend = safe_get_text(job.find('span', class_='stipend'))
                status_info = safe_get_text(job.find('div', class_='status-info').find('span') if job.find('div', class_='status-info') else None)
                job_type = safe_get_text(job.find('div', class_='status-li').find('span') if job.find('div', class_='status-li') else None)

                job_listings.append({
                    'job_title': job_title,
                    'company_name': company_name,
                    'company_logo_url': company_logo_url,
                    'location': location,
                    'duration': duration,
                    'stipend': stipend,
                    'status_info': status_info,
                    'job_type':job_type
                })
                # print(job_listings)
            except:
                pass
        job_listings_json[page] = job_listings
        save_data_to_file(job_listings_json, f"{page}.json")
    else:
        print(f"Failed to retrieve data: {response.status_code}")

fetch_job_listings(page=1)

for i in range(1, 11):
    fetch_job_listings(i)