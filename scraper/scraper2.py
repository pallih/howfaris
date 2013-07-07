from Queue import Queue
from threading import Thread

import scraperwiki
import requests
import lxml.html
import json
import time

requests.adapters.DEFAULT_RETRIES = 5

# Work queue where you push the URLs onto - size 100
url_queue = Queue(10)

check = len(scraperwiki.sqlite.select(" * from distances where url NOT IN (SELECT url from road_descriptions)"))
print 'left:', check
while check > 0:

    todo_parse_road_descriptions = scraperwiki.sqlite.select(" * from distances where url NOT IN (SELECT url from road_descriptions) limit 2000")

    batch = []

    def saver(data):
        scraperwiki.sqlite.save(['from','to','roads'], data=data, table_name='road_descriptions')

    def worker():
        '''Gets the next url from the queue and processes it'''
        while True:
            leg = url_queue.get()
            data = {}
            response = requests.get(leg['url'])
            root = lxml.html.fromstring(response.text)
            legs = root.xpath('//table[@class="vegalengdir-legs"]/tr[not(@class)]')
            data['from'] = leg['from']
            data['to'] = leg['to']
            data['url'] = leg['url']
            data['distance'] = leg['distance']
            data['busl'] = leg['busl']
            data['mol'] = leg['mol']
            data['info'] = leg['info']
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
            batch.append(data)
            url_queue.task_done()

    # Start a pool of 20 workers
    for i in xrange(20):
         t = Thread(target=worker)
         t.daemon = True
         t.start()

    # Change this to read your links and queue them for processing
    for leg in todo_parse_road_descriptions:
        url_queue.put(leg)

    # Block until everything is finished.
    url_queue.join()

    for x in batch:
        scraperwiki.sqlite.save(['from','to','roads'], data=x, table_name='road_descriptions')
    print 'did 2000'

    check = len(scraperwiki.sqlite.select(" * from distances where url NOT IN (SELECT url from road_descriptions)"))
    print 'left:', check
    time.sleep(3)
    print 'slept. now continuing'
