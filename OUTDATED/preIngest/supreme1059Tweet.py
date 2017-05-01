import urllib, urllib2, time, tweepy, socket, sys, StringIO, gzip, zlib, json, os
from time import gmtime, strftime
from xml.dom import minidom
from tweepy.auth import OAuthHandler
from datetime import datetime
from dateutil import tz

#enter the corresponding information from your Twitter application:
CONSUMER_KEY = ''#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = ''#keep the quotes, replace this with your consumer secret key
ACCESS_KEY = ''#keep the quotes, replace this with your access token
ACCESS_SECRET = ''#keep the quotes, replace this with your access token secret
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

print 'Timeout in seconds? (Polling)\n\nPlease enter a number: ' 
timeoutSec = raw_input('')
sleepTime=int(timeoutSec)

def UTCtoEST():
	zulu=strftime("%Y-%m-%d %H:%M:%S", gmtime())
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz('America/New_York')
	utc=datetime.strptime(zulu, "%Y-%m-%d %H:%M:%S")
	utc = utc.replace(tzinfo=from_zone)
	eastern = utc.astimezone(to_zone)
	return str(eastern) + ' EST'

#Original collection - first parse
#This will be checked against
originalDict={}
socket.setdefaulttimeout(sleepTime)

try:
	#parse
	req = urllib2.Request('http://www.supremenewyork.com/mobile_stock.json')
	req.add_header('User-Agent', "User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25")
	resp = urllib2.urlopen(req)
	data = json.loads(resp.read())
except socket.timeout:
	print 'Timeout on first visit! Restart[!]'
	sys.exit()

#populating dictionary with {itemName:variant}
for i in range(len(data[u'products_and_categories'][u'new'])):
	name = data[u'products_and_categories'][u'new'][i][u'name'].encode('ascii','ignore')
	var = data[u'products_and_categories'][u'new'][i][u'id']
	originalDict.update({name:str(var)})
	#Lists are filled with original values

def main():
	global originalDict
	global newDict
	socket.setdefaulttimeout(sleepTime)
	
	#Clear new dictionary to be filled/refilled
	newDict={}
	try:
		#parse
		req = urllib2.Request('http://www.supremenewyork.com/mobile_stock.json')
		req.add_header('User-Agent', "User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25")
		resp = urllib2.urlopen(req)
		data = json.loads(resp.read())
	except socket.timeout:
		print '\nTimeout on reparse!\n'
		main()
	#populating new dictionary with updated {itemName:variant}
	for i in range(len(data[u'products_and_categories'][u'new'])):
		name = data[u'products_and_categories'][u'new'][i][u'name'].encode('ascii','ignore')
		var = data[u'products_and_categories'][u'new'][i][u'id']
		newDict.update({name:str(var)})
	
	#checking if dictioaries are equal
	if (originalDict == newDict):
		#dictionaries are the same
		print UTCtoEST()+' :: '+str(len(newDict)) +' items indexed...'
		time.sleep(sleepTime)
		main()
	
		'''Compare like this? Nahhhh (-1,0,1)
		if (cmp(originalDict, newDict)==0):
			pass	
		if (cmp(originalDict, newDict)==0):
			pass
		'''

	#dictionaries are not the same
	else:
		#Difference from new dictionary to original are the new items
		#in set([]) format		
		itemsAdded=list(set(newDict)-set(originalDict))
		
		#loop through the set([]) notation
		for i in (itemsAdded):
			#Gets string or new keys of the updated parse
			nameOfItem=i
			#Use this key to get value(variant) of item
			varOfItem=newDict[nameOfItem]
			print nameOfItem+' :: http://www.supremenewyork.com/shop/'+str(varOfItem)
			print '\n'
			try:
				api.update_status(status=UTCtoEST()+' :: ' + str(nameOfItem)+' :: http://www.supremenewyork.com/shop/'+str(varOfItem))
			except tweepy.TweepError as e:
	    			print e.message[0]['message']
				print 'ERROR posting tweet'
				#os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( 2, 200))
				continue

		#Clear original dictionary
		originalDict={}
		
		#Because items have been added - we need to adjust our base for future parses
		#Setting original dictionary to the new parse dictionary
		originalDict=newDict.copy()
		
		time.sleep(sleepTime)
		main();
		
main();
