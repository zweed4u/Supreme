import urllib, urllib2, json, time, datetime, requests, os, sys, tweepy
import urllib2 as net
from time import gmtime, strftime
from xml.dom import minidom
from tweepy.auth import OAuthHandler
from datetime import datetime
from dateutil import tz

'''@ application'''
#enter the corresponding information from your Twitter application:
CONSUMER_KEY = ''#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = ''#keep the quotes, replace this with your consumer secret key
ACCESS_KEY = '-'#keep the quotes, replace this with your access token
ACCESS_SECRET = ''#keep the quotes, replace this with your access token secret
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

def UTCtoEST():
	zulu=strftime("%Y-%m-%d %H:%M:%S", gmtime())
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz('America/New_York')
	utc=datetime.strptime(zulu, "%Y-%m-%d %H:%M:%S")
	utc = utc.replace(tzinfo=from_zone)
	eastern = utc.astimezone(to_zone)
	return str(eastern) + ' EST'

req = urllib2.Request('http://www.supremenewyork.com/mobile_stock.json')
req.add_header('User-Agent', "User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25")
resp = urllib2.urlopen(req)
data = json.loads(resp.read())

items=[];theirVars=[];newItems=[];newVars=[];
for i in range(len(data[u'products_and_categories'].values())):
	for j in range(len(data[u'products_and_categories'].values()[i])):
		item=data[u'products_and_categories'].values()[i][j]
		name=str(item[u'name'].encode('ascii','ignore'))
		variant=str(item[u'id'])
		items.append(name)
		theirVars.append(variant)

'''
for i in items:
	newItems.append(i)
for i in theirVars:
	newVars.append(i)
'''

'''
for i in range(len(items)):
	print items[i]+' :: http://www.supremenewyork.com/shop/'+theirVars[i]
'''

def update():
	global newItem
	global items
	global theirVars
	global newItems
	global newVars
	newItems=[];newVars=[]
	req = urllib2.Request('http://www.supremenewyork.com/mobile_stock.json')
	req.add_header('User-Agent', "User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25")
	resp = urllib2.urlopen(req)
	data = json.loads(resp.read())
	for i in range(len(data[u'products_and_categories'].values())):
		for j in range(len(data[u'products_and_categories'].values()[i])):
			newItem=data[u'products_and_categories'].values()[i][j]
			newName=str(newItem[u'name'].encode('ascii','ignore'))
			newVariant=str(newItem[u'id'])
			newItems.append(newName)
			newVars.append(newVariant)
	#print newItems
	#print items
	if (newItems==items) and (newVars==theirVars):
		#same items and same variants		
		print UTCtoEST()+' :: '+str(len(newItems))+' items referenced'	
		#print str(len(newItems))+' = ' +str(len(items))
		#include timestamp from UTCtoEST function
		time.sleep(5)
		update()
	else:
		#not equal - print timestamp
		if len(newItems)>len(items):
			#items added
			itemsAdded=list(set(newItems)-set(items))
			varsAdded=list(set(newVars)-set(theirVars))
			for i in range(len(itemsAdded)):
				api.update_status(status=UTCtoEST()+' :: ' + itemsAdded[i]+' :: http://www.supremenewyork.com/shop/'+varsAdded[i])
				print itemsAdded[i]+' :: http://www.supremenewyork.com/shop/'+varsAdded[i]
		elif len(newItems)<len(items):
			#items removed
			itemsRemoved=list(set(items)-set(newItems))
			varsRemoved=list(set(theirVars)-set(newVars))
			for i in range(len(itemsRemoved)):
				api.update_status(status=UTCtoEST()+' :: ' + itemsRemoved[i]+'REMOVED :: http://www.supremenewyork.com/shop/'+varsRemoved[i])
				print itemsRemoved[i]+'REMOVED :: http://www.supremenewyork.com/shop/'+varsRemoved[i]
		else:
			print 'SAME NUMBER OF ITEMS BUT DIFFERENT LISTS OF VARIANTS- IDK - REPARSING'
			update()
		
update()
