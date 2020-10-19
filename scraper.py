import scraperwiki
from bs4 import BeautifulSoup
import re
import csv, json

US_STATES = dict((
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
    ('AS', 'American Samoa'), ('GU', 'Guam'), ('MP', 'Northern Mariana Islands'), ('PR', 'Puerto Rico'), ('VI', 'Virgin Islands'),
))

# Scrape data from National Governors Association
ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
html = scraperwiki.scrape("https://www.nga.org/governors/addresses/", user_agent=ua)
soup = BeautifulSoup(html, "html5lib")

governors = []
for gov_div in soup.select('#primary .wpb_column.vc_col-sm-4'):
    lines = gov_div.find('p').text.split('\n')
    headings = gov_div.find_all('h2')

    gov_data = {}
    for h in headings:
        if h.text:
            gov_data['state_name'] = h.text

    if lines[0].startswith('Office of Governor'):
        full_name = lines.pop(0).replace('Office of Governor ', '').replace(u'\u201c', '"').replace(u'\u201d','"')
        gov_data['first_name'], gov_data['last_name'] = full_name.rsplit(' ', 1)

    if 'website' in lines[-1]:
        urls = gov_div.find_all('a', href=True)
        if urls:
            gov_data['url'] = urls[0]['href']
        lines.pop(-1)

    if 'Fax:' in lines[-1]:
        gov_data['fax'] = lines.pop(-1).replace('Fax: ', '').replace('/', '-')

    if 'Phone:' in lines[-1]:
        gov_data['phone'] = lines.pop(-1).replace('Phone: ', '').replace('/', '-').replace(' ', '')

    if re.search(r'\d{5}', lines[-1]):
        addr_line = lines.pop(-1)
        matched_city_state_zip = re.match(r'(?P<city>.*)\,\s(?P<state_abbr>[A-Z]{2})\s(?P<zip>[\d\-]+)$', addr_line)
        if matched_city_state_zip:
            gov_data['city'], gov_data['state_abbr'], gov_data['zip'] = matched_city_state_zip.groups()
        else:
            # if regex doesn't match cleanly, split on space and re-assemble
            addr_split = addr_line.split(' ')
            gov_data['zip'] = addr_split[-1]
            state = addr_split[-2]
            if len(state) == 2:
                gov_data['state_abbr'] = state
            else:
                gov_data['state_name'] = state
                # invert US_STATES and look up abbr
                gov_data['state_abbr'] = {v: k for k, v in US_STATES.items()}[state]
            gov_data['city'] = ' '.join(addr_split[:-2]).replace(',','')

    if len(lines) == 1:
        gov_data['address1'] = lines[0]
    else:
        gov_data['address1'], gov_data['address2'] = lines

    governors.append(gov_data)

# SQLlite export
scraperwiki.sqlite.save(unique_keys=['state_name'], data=governors)

# CSV export
with open('data.csv', 'w', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['state_name', 'first_name', 'last_name',
                                           'address1', 'address2',
                                           'city', 'state_abbr', 'zip',
                                           'phone', 'fax', 'url'])

    writer.writeheader()
    for gov in governors:
        row = {k:v for k,v in gov.items()}
        writer.writerow(row)

# JSON export
with open('data.json', 'w') as f:
    json.dump(governors, f, sort_keys=True, indent=4)
