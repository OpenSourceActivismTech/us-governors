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
    # enumerate over lines with index, so we can roll back
    rollback = 0
    for index, line in enumerate(lines):
        if index == 0:
            gov['state'] = line
        if index == 1:
            gov['name'] = line.replace('Office of Governor ', '')
        if index == 2:
            gov['address_1'] = line
        if index - rollback == 3:
            if ',' in line:
                gov['city_state_zip'] = line
            else:
                gov['address_2'] = line
                rollback = 1  # roll back one line
        if index - rollback == 4:
            gov['phone'] = line.replace('Phone: ', '').replace('/', '-')
        if index - rollback == 5:
            gov['fax'] = line.replace('Fax: ', '').replace('/', '-')

    # do url parsing outside of line block
    try:
        gov['url'] = e.cssselect('a')[0].attrib['href']
    except IndexError:
        pass

    governors.append(gov)

scraperwiki.sqlite.save(unique_keys=['state'], data=governors)
