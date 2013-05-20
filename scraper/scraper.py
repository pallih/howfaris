import scraperwiki
import requests
import lxml.html
from urlparse import urlparse, parse_qsl

LANDSHLUTAR_BASE_URL = 'http://www.vegagerdin.is/vegakerfid/vegalengdir/eftir-landshluta/%s'
LANDSHLUTAR = {'hofudborgarsvaedid', 'reykjanes', 'vesturland', 'vestfirdir',
'nordurland-vestra', 'nordurland-eystra', 'austurland', 'sudurland', 'halendid'}


def get_places():
    for landshluti in LANDSHLUTAR:
        response = requests.get(LANDSHLUTAR_BASE_URL % landshluti)
        root = lxml.html.fromstring(response.text)
        places = root.xpath('//*[starts-with(@class,"area")]/li/a')
        batch = []
        for place in places:
            data = {}
            id = parse_qsl(urlparse(place.attrib['href'])[4])[0][1]
            data['place'] = place.text
            data['id'] = id
            data['landshluti'] = landshluti
            batch.append(data)
        scraperwiki.sqlite.save(['id'], data=batch, table_name='places')

get_places()