import scraperwiki
import lxml.html
import re
# import pprint

# Scrape data from National Governors Association
html = scraperwiki.scrape("http://www.nga.org/cms/home/governors/staff-directories--contact-infor/col2-content/governors-office-addresses-and-w.html")
root = lxml.html.fromstring(html)
elements = root.cssselect("table td p")

governors = []
for e in elements:
    lines = e.text_content().replace('\t', '').split('\n')

    gov = {}
    for index, line in enumerate(lines):
        if index == 0:
            gov['state_name'] = line
        if index == 1:
            gov['name'] = line.replace('Office of Governor ', '')
        if index == 2:
            gov['address_1'] = line
        if index in [3, 4, 5]:
            if re.search('[\d]{5}', line):
                # city, state, zip
                address_parts = line.split(',')
                gov['city'] = ','.join(address_parts[0:1])
                zip_parts = address_parts[-1].split(' ')
                gov['state'] = zip_parts[1]
                gov['zip'] = zip_parts[-1]
            else:
                if ('Phone' not in line
                and 'Fax' not in line
                and 'website' not in line):
                    gov['address_2'] = line

        if line.startswith('Phone'):
            gov['phone'] = line.replace('Phone: ', '').replace('/', '-').replace(' ', '').replace('011', '+011')
        if line.startswith('Fax'):
            gov['fax'] = line.replace('Fax: ', '').replace('/', '-').replace('011', '+011')

    # do url parsing outside of line block
    try:
        gov['url'] = e.cssselect('a')[0].attrib['href']
    except IndexError:
        pass

    # cleanup aura
    if gov['state'] == 'CA':
        gov['name'] = gov['name'].replace('Edmund Brown', 'Jerry Brown')

    governors.append(gov)

# pp = pprint.PrettyPrinter()
# pp.pprint(governors)
scraperwiki.sqlite.save(unique_keys=['state'], data=governors)
