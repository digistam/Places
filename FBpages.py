#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import csv
import datetime
now = datetime.datetime.now()
import requests
import longtermaccesstoken
import pprint as pp
import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.http import MediaFileUpload
from apiclient import errors
import facebookobjects

access_token = longtermaccesstoken.access_token
outfile_path = 'feed_%i%i%i%i%i.csv' % (now.year,now.month,now.day,now.hour,now.minute)

def write_csv_header():
	outfile_path = 'feed_%i%i%i%i%i.csv' % (now.year,now.month,now.day,now.hour,now.minute)
	# open it up, the w means we will write to it
	with open(outfile_path, 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter='|')
		headers = ['object_id','type','object_name','post_id','post_url','actor','actor_url','actor_id','actor_pic','date','message','story','link','description','comments','likes','application']
		writer.writerow(headers)

def parse_stream(object_id):
	try:
	  # open it up, the a means we will append to it
    with open(outfile_path, 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter='|')
      headers = ['object_id','type','object_name','post_id','post_url','actor','actor_url','actor_id','actor_pic','date','message','story','link','picture','description','comments','likes','application']
	    writer.writerow(headers)
			url = requests.get('https://graph.facebook.com/v2.6/%s?fields=name,feed.limit(15){from,created_time,comments,message,story,permalink_url,full_picture,story_tags,link,description,type}&access_token=%s' % (object_id,access_token))
			parsed_json = url.json()
			dict = []
			likedict = []
			for item in parsed_json['feed']['data']:
				#initialize the row
				row = []
				row.append(object_id)
				if item.has_key("type"):
					row.append(item['type'])
				else:
					row.append(' ')
				row.append(parsed_json['name'])
				row.append(item['id'])
				if str(item['id']).find("_") == -1:
					post_url = str(item['id'])
				else:
					post_url = str.split(str(item['id']),'_')[1]
				row.append(item['permalink_url'])
				row.append(unicode(item['from']['name']).encode('utf-8'))
				row.append('http://www.facebook.com/' + item['from']['id'])
				row.append(item['from']['id'])
				row.append('http://graph.facebook.com/' + item['from']['id'] + '/picture')
				row.append(item['created_time'])
				if item.has_key("message"):
					row.append((unicode(item['message']).encode('utf-8')).replace('|',' '))
				else:
					row.append(' ')
				if item.has_key("story"):
					row.append(item['story'].encode('utf-8'))
				else:
					row.append(' ')
				if item.has_key("link"):
					row.append(item['link'].encode('utf-8'))
				else:
					row.append('')
				if item.has_key("full_picture"):
					row.append(item["full_picture"])
				else:
					row.append("")
				if item.has_key("description"):
					row.append(item['description'])
				else:
					row.append('description')
				try:
					row.append(' ')
				except KeyError, e:
					row.append(' ')
				try:
					row.append('')
				except KeyError, e:
					row.append('')
				if item.has_key("application"):
					row.append('application')
				else:
					row.append('application')
				dict.append(row)
				writer.writerow(row)
				print row
				try:
					for i in range(len(item['comments']['data'])):
						row = []
						row.append(object_id)
						row.append('comment')
						row.append(parsed_json['name'])
						row.append(item['comments']['data'][i]['id'])
						if str(item['comments']['data'][i]['id']).find("_") == -1:
							post_url = str(item['comments']['data'][i]['id'])
						else:
							post_url = str.split(str(item['comments']['data'][i]['id']),'_')[1]
						row.append(item['permalink_url'])
						row.append(unicode(item['comments']['data'][i]['from']['name']).encode('utf-8'))
						row.append('http://www.facebook.com/' + item['comments']['data'][i]['from']['id'])
						row.append(item['comments']['data'][i]['from']['id'])
						row.append('http://graph.facebook.com/' + item['comments']['data'][i]['from']['id'] + '/picture')
						row.append(item['comments']['data'][i]['created_time'])
						row.append((unicode(item['comments']['data'][i]['message']).encode('utf-8')).replace('|',' '))
						row.append('')
						row.append('')
						if item.has_key("full_picture"):
							row.append(item["full_picture"])
						else:
							row.append('')
						row.append('')
						row.append('')
						row.append('')
						row.append('application')
						dict.append(row)
						writer.writerow(row)
						print row
				
				except KeyError, e:
					e
	except KeyError, e:
       		print "KeyError: %s" % e
	except ValueError, e:
        	print "ValueError: %s" % e
        	print "#####"
        	print item
        	print "#####"

def fill_fusiontable(outfile_path):
    # Procedure to dump CSV file to Fusion Tables
	try:
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
	  media_body = MediaFileUpload(filename=outfile_path, mimetype="application/octet-stream")
		print service.table().importRows(tableId='1DT2tM2bsPcAo5TTUoYt8QVR02du8PI0eVCZe3swm', media_body=media_body, encoding="auto-detect", delimiter="|",startLine=1,	isStrict=True).execute()
	except ValueError, e:
		print 'er is iets mis gegaan:',e
	except errors.HttpError, e:
		print 'er is iets mis gegaan:',e

for i in range(len(facebookobjects.objects)):
	object_id = facebookobjects.objects[i]
	parse_stream(facebookobjects.objects[i])
fill_fusiontable(outfile_path)
