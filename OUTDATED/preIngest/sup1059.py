import urllib, urllib2, json, time, datetime, requests, os, tweepy, sys
from selenium import webdriver;
from requests.utils import dict_from_cookiejar
from time import gmtime, strftime
from datetime import datetime
from dateutil import tz
from tweepy.auth import OAuthHandler

'''
CONSUMER_KEY = ''#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = ''#keep the quotes, replace this with your consumer secret key
ACCESS_KEY = '-'#keep the quotes, replace this with your access token
ACCESS_SECRET = ''#keep the quotes, replace this with your access token secret
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
'''


def UTCtoEST():
	zulu=strftime("%Y-%m-%d %H:%M:%S", gmtime())
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz('America/New_York')
	utc=datetime.strptime(zulu, "%Y-%m-%d %H:%M:%S")
	utc = utc.replace(tzinfo=from_zone)
	eastern = utc.astimezone(to_zone)
	return str(eastern) + ' EST'


#keyword lowercase!!!!
keyword=raw_input("Product name? ")

req = urllib2.Request('http://www.supremenewyork.com/mobile_stock.json')
req.add_header('User-Agent', "User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25")
resp = urllib2.urlopen(req)
data = json.loads(resp.read())


for i in range(len(data[u'products_and_categories'].values())):
	for j in range(len(data[u'products_and_categories'].values()[i])):
		item=data[u'products_and_categories'].values()[i][j]
		name=str(item[u'name'].encode('ascii','ignore'))
		variant=str(item[u'id'])
		#api.update_status(status=UTCtoEST()+' :: '+name+' :: http://www.supremenewyork.com/shop/'+variant)
		#print name+' :: http://www.supremenewyork.com/shop/'+variant


while data[u'products_and_categories']=={}:
	#empty - new season
	time.sleep(1)
	resp = urllib2.urlopen(req)
	data = json.loads(resp.read())
	print UTCtoEST()
	#print data

exist=0
numOfMatches=0
productMatch=['']
def productInCatalog():
	global exist
	global numOfMatches
	global productMatch
	resp = urllib2.urlopen(req)
	data = json.loads(resp.read())
	for i in data[u'products_and_categories'].keys():
		categories=data[u'products_and_categories']
		itemsInCategory=categories[i]
		for item in itemsInCategory:
			name=item[u'name'].encode('ascii','ignore').lower()
			idNum=str(item[u'id'])
			if keyword in name:
				urlNum=idNum
				numOfMatches+=1
				exist=1
				productMatch.append(urlNum)
				print '\n'
				print str(numOfMatches)+') ' +name + ' :: '+urlNum


productInCatalog()
while exist==0:
	print UTCtoEST()+' :: Item not found'
	time.sleep(5)
	productInCatalog()



print '\n'
if numOfMatches==1:
	urlNum=productMatch[1]
else:
	whichProduct=raw_input("Product num? ")
	urlNum=productMatch[int(whichProduct)]
#print urlNum
#print UTCtoEST()



jsonurl = 'http://www.supremenewyork.com/shop/'+urlNum+'.json'
response = urllib.urlopen(jsonurl)
data = json.loads(response.read())
print '\n'
'''
if data[u'new_item']==True:
	#item is new????
'''
#numOfCW=len(data[u'styles'])
pick=0;cwPicker=[''];varPicker=[''];
for colorWays in data[u'styles']:
	colorWay=colorWays[u'name'].encode('ascii','ignore').lower()
	cwPicker.append(colorWay)
	print colorWay+' :: '+urlNum
	print 'http://www.supremenewyork.com/shop/'+str(urlNum)
	for sizes in colorWays[u'sizes']:
		pick+=1
		size=sizes[u'name'].encode('ascii','ignore')
		varId= str(sizes[u'id'])
		varPicker.append(varId)
		print str(pick)+') '+size+ ' :: '+varId
	print '\n'
#CHECK IF THATS SOLDOUT
#print 'If not 1 then need to reparse for product url'
itemPick=raw_input('Which colorway do you want? ')
varItemPick=varPicker[int(itemPick)]


formQueriedURL='http://www.supremenewyork.com/shop/'+str(urlNum)+'/add'
session=requests.Session()

#Payload --- scrape for auth token down here or recent one
data={'utf8': '%E2%9C%93',
	  'authenticity_token': 'FYtB9%2BNegm3wPfrHewKHO8xc7NceANeDkGRtzSRJxT8%3D',
	  'size': str(varItemPick),
	  'commit': 'add+to+cart'}
session.cookies.clear()
response=session.post(formQueriedURL,data=data)
response=session.get('http://supremenewyork.com/shop/cart')
cookies = dict_from_cookiejar(response.cookies)
driver=webdriver.Chrome(os.getcwd()+'/chromedriver')
driver.get('http://www.supremenewyork.com/shop/cart')
driver.delete_all_cookies()
for key, value in cookies.items():
	driver.add_cookie({'name': key, 'value': value})
driver.refresh()
