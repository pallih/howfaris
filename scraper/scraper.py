# -*- coding: utf-8 -*-
import scraperwiki
import requests
import lxml.html
from urlparse import urlparse, parse_qsl
import json

LANDSHLUTAR_BASE_URL = 'http://www.vegagerdin.is/vegakerfid/vegalengdir/eftir-landshluta/%s'
LANDSHLUTAR = {'hofudborgarsvaedid', 'reykjanes', 'vesturland', 'vestfirdir', 'nordurland-vestra', 'nordurland-eystra', 'austurland', 'sudurland', 'halendid'}
PLACE_BASE_URL = 'http://www.vegagerdin.is/vegakerfid/vegalengdir/lengdir?id=%s'

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


def parse_place(id):
    print 'Doing: ', id
    place= scraperwiki.sqlite.select("* from places where id=%s" % id)
    for item in place:
        batch = []
        response = requests.get(PLACE_BASE_URL % item['id'])
        root = lxml.html.fromstring(response.text)
        destinations = root.xpath('//th[@scope="row"]')

        for destination in destinations:
            no_of_destinations = destination.attrib['rowspan']
            data = {}
            data['from'] = id
            to = parse_qsl(urlparse('http://www.vegagerdin.is/' + destination[0].attrib['href'])[4])[0][1]
            data['to'] = to
            data['distance'] = destination.xpath('following-sibling::td')[0].text_content()
            data['url'] = 'http://www.vegagerdin.is' + destination.xpath('following-sibling::td')[0][0].attrib['href']
            busl_mol = destination.xpath('following-sibling::td')[1].text_content()
            data['busl'] = busl_mol.split('/')[0].strip()
            data['mol'] = busl_mol.split('/')[1].strip()
            data['info'] = destination.xpath('following-sibling::td')[2].text_content()
            data['shortest'] = '1'
            batch.append(data)
            for x in range(0,int(no_of_destinations)-1):
                data = {}
                additional_destination = destination.xpath('parent::tr/following-sibling::tr')[x]
                data['from'] = id
                data['to'] = to
                data['distance'] = additional_destination[0].text_content()
                data['url'] = 'http://www.vegagerdin.is' + additional_destination[0][0].attrib['href']
                busl_mol = additional_destination[1].text_content()
                data['busl'] = busl_mol.split('/')[0].strip()
                data['mol'] = busl_mol.split('/')[1].strip()
                data['info'] = additional_destination[2].text_content()
                batch.append(data)
        scraperwiki.sqlite.save(['from','to','distance','info'], data=batch, table_name='distances')

#places_to_do = scraperwiki.sqlite.select("id from places")

#for place in places_to_do:
#     parse_place(place['id'])

def parse_road_descriptions(url,from_id,to_id,distance,busl,mol,info):
    #print url
    data = {}
    response = requests.get(url)
    root = lxml.html.fromstring(response.text)
    legs = root.xpath('//table[@class="vegalengdir-legs"]/tr[not(@class)]')
    data['from'] = from_id
    data['to'] = to_id
    data['url'] = url
    data['distance'] = distance
    data['busl'] = busl
    data['mol'] = mol
    data['info'] = info
    roads = []
    for leg in legs:
        #try:
            roadname = leg[0].text
            roadnumber = leg[0][0].text.replace('(', '').replace(')','').strip()
            roadlength = leg[1].text.replace(' km', '').strip()
            roads.append([roadname,roadnumber,roadlength])
            #print roads
            #data['roadname'] = leg[0].text.replace('null', '-').strip()
            #data['roadnumber'] = leg[0][0].text.replace('(', '').replace(')','').strip()
            #data['roadlength'] = leg[1].text.replace(' km', '').strip()
        #except:
         #   pass
    data['roads'] = json.dumps(roads)
    return data


#todo_parse_road_descriptions = scraperwiki.sqlite.select(' * from distances where shortest=1 LIMIT 1')

#todo_parse_road_descriptions = scraperwiki.sqlite.select(' SELECT * from distances AS D LEFT JOIN road_descriptions AS R on D.url = R.url where R.url is null AND D.shortest = 1 limit 30')

#for leg in todo_parse_road_descriptions:
#    data = parse_road_descriptions(leg['url'],leg['from'],leg['to'],leg['distance'],leg['busl'],leg['mol'],leg['info'])
    #print type(json.loads(data['roads']))
#    scraperwiki.sqlite.save(['from','to','roads'], data=data, table_name='road_descriptions')

# printme = scraperwiki.sqlite.select(' * from road_descriptions')

# for x in printme:
#     for d in json.loads(x['roads']):
#         for m in d:
#             print m

def scrape():
    todo_parse_road_descriptions = scraperwiki.sqlite.select(" * from distances where url NOT IN (SELECT url from road_descriptions) and shortest = 1 limit 15")
    if not todo_parse_road_descriptions:
        return False
    for leg in todo_parse_road_descriptions:
        data = parse_road_descriptions(leg['url'],leg['from'],leg['to'],leg['distance'],leg['busl'],leg['mol'],leg['info'])
        print 'done with:', leg['url']
    #print type(json.loads(data['roads']))
        scraperwiki.sqlite.save(['from','to','roads'], data=data, table_name='road_descriptions')
        return len(data)

while scrape(): pass
