#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import csv
import datetime
import time
import requests
import longtermaccesstoken
from bs4 import BeautifulSoup, SoupStrainer
import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

def fetch_places(latitude, longitude, distance, access_token, next_page_token=None):
    params = {
        'location': '%s,%s' % (latitude, longitude),
        'radius': distance,
        'key': access_token,
    }
    if next_page_token:
        params['pagetoken'] = next_page_token
    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?' + '&'.join([k + '=' + str(v) for (k, v) in params.iteritems()]))
    parsed_json = response.json()
    next_page_token = parsed_json.get('next_page_token')
    return parsed_json['results'], next_page_token

def main():
    access_token = longtermaccesstoken.google_places_token
    latitude = str(sys.argv[1])
    longitude = str(sys.argv[2])
    distance = str(sys.argv[3])
    path = str(sys.argv[4])
    next_page_token = None

    now = datetime.datetime.now()
    outfile_path = path + '/geolocations_%i%i%i%i%i.csv' % (now.year, now.month, now.day, now.hour, now.minute)
    with open(outfile_path, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        writer.writerow(['id','cat name','cat id','id','name','lat','lon','street','city','country','picture','url'])
        while True:
            results, next_page_token = fetch_places(latitude, longitude, distance, access_token, next_page_token)

            for item in results:
                row = []
                fb_id = item['id']
                row.append(fb_id)  # append id
                row.append('')  # append cat name
                row.append('')  # append cat id
                row.append(fb_id)  # append id
                name = item['name']
                name = unicode(name).encode('utf8')
                row.append(name)  # append name
                # row.append(item['icon'])
                row.append(item['geometry']['location']['lat'])  # append lat
                row.append(item['geometry']['location']['lng'])  # append lon
                try:
                    row.append(unicode(item['vicinity']).encode('utf-8'))  # append street
                except KeyError:
                    row.append('')
                row.append('')  # append city
                row.append('')  # append country
                row.append(item['icon'])
                try:
                    URL = item['photos'][0]['html_attributions']
                    URL = ''.join(URL)
                    soup = BeautifulSoup(URL, "html5lib")
                    for a in soup.find_all('a', href=True):
                        row.append(a['href'])  # append URL
                    # print URL
                except KeyError:
                    row.append('')
                writer.writerow(row)
                # Here's the file you get from API Console -> Service Account.
                f = file('***.p12', 'rb')
                key = f.read()
                f.close()

                # Create an httplib2.Http object to handle our HTTP requests and authorize it
                # with the Credentials. Note that the first parameter, service_account_name,
                # is the Email address created for the Service account. It must be the email
                # address associated with the key that was created.
                credentials = SignedJwtAssertionCredentials(
                '***@***.iam.gserviceaccount.com',
                key,
                scope='https://www.googleapis.com/auth/fusiontables')
                http = httplib2.Http()
                http = credentials.authorize(http)

                service = build("fusiontables", "v2", http=http)
                # For example, let make SQL query to SELECT ALL from Table with
                # id = 1gvB3SedL89vG5r1128nUN5ICyyw7Wio5g1w1mbk
                print(service.query().sql(sql="INSERT INTO 1vxuRAOv04pq5z3JPj91R92qVzY0c9beI-_DuFh7f (name) VALUES ('%s')" % (item['name'])).execute())
            if not next_page_token:
                break

            time.sleep(2)

if __name__ == '__main__':
    main()
