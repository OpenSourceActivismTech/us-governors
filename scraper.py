import scraperwiki
import lxml.html

# Scrape data from National Governors Association
html = scraperwiki.scrape("http://www.nga.org/cms/home/governors/staff-directories--contact-infor/col2-content/governors-office-addresses-and-w.html")
root = lxml.html.fromstring(html)
elements = root.cssselect("table td p")

governors = []
for e in elements:
    lines = e.text_content().replace('\t', '').split('\n')
    gov = {}
    gov['state'] = lines[0]
    gov['name'] = lines[1].replace('Office of ', '')
    gov['address_1'] = lines[2]
    gov['address_2'] = lines[3]
    gov['city_state'] = lines[4]
    gov['phone'] = lines[5].replace('Phone: ', '').replace('/', '-')
    try:
        gov['fax'] = lines[6].replace('Fax: ', '').replace('/', '-')
        gov['website'] = lines[7]
    except IndexError:
        pass

    governors.append(gov)

scraperwiki.sqlite.save(unique_keys=['state'], data=governors)
