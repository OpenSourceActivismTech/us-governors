import scraperwiki
from bs4 import BeautifulSoup
import re
import csv, json

# Scrape data from National Governors Association
html = scraperwiki.scrape("https://www.nga.org/cms/governors/addresses")
soup = BeautifulSoup(html, "html5lib")

governors = []
for gov_div in soup.select('.article-body .col-sm-6.col-md-4'):

    lines = gov_div.find('p').text.split('\n')
    gov_data = {'state_name': gov_div.find('h3').text}

    if lines[0].startswith('Office of Governor'):
        gov_data['first_name'], gov_data['last_name'] = lines.pop(0).replace('Office of Governor ', '').rsplit(' ', 1)

    if 'Governor\'s website' in lines[-1]:
        gov_data['url'] = gov_div.find('a')['href']
        lines.pop(-1)

    if 'Fax:' in lines[-1]:
        gov_data['fax'] = lines.pop(-1).replace('Fax: ', '').replace('/', '-')

    if 'Phone:' in lines[-1]:
        gov_data['phone'] = lines.pop(-1).replace('Phone: ', '').replace('/', '-').replace(' ', '')

    if re.search(r'\d{5}', lines[-1]):
        gov_data['city'], gov_data['state_abbr'], gov_data['zip'] = re.match(r'(?P<city>.*)\,\s(?P<state_abbr>[A-Z]{2})\s(?P<zip>[\d\-]+)$', lines.pop(-1)).groups()

    if len(lines) == 1:
        gov_data['address1'] = lines[0]
    else:
        gov_data['address1'], gov_data['address2'] = lines

    # cleanup aura
    if gov_data['state_name'] == 'California':
        gov_data['first_name'] = gov_data['first_name'].replace('Edmund', 'Jerry')

    governors.append(gov_data)

# SQLlite export
scraperwiki.sqlite.save(unique_keys=['state_name'], data=governors)

# CSV export
with open('data.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['state_name', 'first_name', 'last_name',
                                           'address1', 'address2',
                                           'city', 'state_abbr', 'zip',
                                           'phone', 'fax', 'url'])

    writer.writeheader()
    for gov in governors:
        row = {k:v.encode('utf8') for k,v in gov.items()}
        writer.writerow(row)

# JSON export
with open('data.json', 'w') as f:
    json.dump(governors, f, sort_keys=True, indent=4)
