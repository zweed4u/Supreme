#!/bin/env python2.7

# Run around 1059 as early as 1055.
# Polling times vary pick something nice.
# Ghost checkout timer can be changed by 
# adjusting for loop range near bottom.
# Fill out personal data in checkout payload dict.

import sys, json, time, requests, urllib2
from datetime import datetime

qty='1'

def UTCtoEST():
    current=datetime.now()
    return str(current) + ' EST'
print
poll=raw_input("Polling interval? ")
poll=int(poll)
keyword=raw_input("Product name? ").title()       # hardwire here by declaring keyword as a string 
color=raw_input("Color? ").title()                # hardwire here by declaring keyword as a string
sz=raw_input("Size? ").title()                    # hardwire here by declaring keyword as a string
print 
print UTCtoEST(),':: Parsing page...'
def main():
    global ID
    global variant
    global cw
    req = urllib2.Request('http://www.supremenewyork.com/mobile_stock.json')
    req.add_header('User-Agent', "User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25")
    resp = urllib2.urlopen(req)
    data = json.loads(resp.read())
    ID=0
    for i in range(len(data[u'products_and_categories'].values())):
        for j in range(len(data[u'products_and_categories'].values()[i])):
            item=data[u'products_and_categories'].values()[i][j]
            name=str(item[u'name'].encode('ascii','ignore'))
            # SEARCH WORDS HERE
            # if string1 in name or string2 in name:
            if keyword in name:
                # match/(es) detected!
                # can return multiple matches but you're 
                # probably buying for resell so it doesn't matter
                myproduct=name                
                ID=str(item[u'id'])
                print UTCtoEST(),'::',name, ID, 'found ( MATCHING ITEM DETECTED )'
    if (ID == 0):
        # variant flag unchanged - nothing found - rerun
        time.sleep(poll)
        print UTCtoEST(),':: Reloading and reparsing page...'
        main()
    else:
        print UTCtoEST(),':: Selecting',str(myproduct),'(',str(ID),')'
        jsonurl = 'http://www.supremenewyork.com/shop/'+str(ID)+'.json'
        req = urllib2.Request(jsonurl)
        req.add_header('User-Agent', "User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B350 Safari/8536.25")
        resp = urllib2.urlopen(req)
        data = json.loads(resp.read())
        found=0
        for numCW in data['styles']:
            # COLORWAY TERMS HERE
            # if string1 in numCW['name'] or string2 in numCW['name']:
            if color in numCW['name'].title():
                for sizes in numCW['sizes']:
                    # SIZE TERMS HERE
                    if str(sizes['name'].title()) == sz: # Medium
                        found=1;
                        variant=str(sizes['id'])
                        cw=numCW['name']
                        print UTCtoEST(),':: Selecting size:', sizes['name'],'(',numCW['name'],')','(',str(sizes['id']),')'
                        
        if found ==0:
            # DEFAULT CASE NEEDED HERE - EITHER COLORWAY NOT FOUND OR SIZE NOT IN RUN OF PRODUCT
            # PICKING FIRST COLORWAY AND LAST SIZE OPTION
            print UTCtoEST(),':: Selecting default colorway:',data['styles'][0]['name']
            sizeName=str(data['styles'][0]['sizes'][len(data['styles'][0]['sizes'])-1]['name'])
            variant=str(data['styles'][0]['sizes'][len(data['styles'][0]['sizes'])-1]['id'])
            cw=data['styles'][0]['name']
            print UTCtoEST(),':: Selecting default size:',sizeName,'(',variant,')'
main()


session=requests.Session()
addUrl='http://www.supremenewyork.com/shop/'+str(ID)+'/add.json'
addHeaders={
    'Host':              'www.supremenewyork.com',                                                                                                                     
    'Accept':            'application/json',                                                                                                                             
    'Proxy-Connection':  'keep-alive',                                                                                                                                   
    'X-Requested-With':  'XMLHttpRequest',                                                                                                                               
    'Accept-Encoding':   'gzip, deflate',                                                                                                                                
    'Accept-Language':   'en-us',                                                                                                                                        
    'Content-Type':      'application/x-www-form-urlencoded',                                                                                                            
    'Origin':            'http://www.supremenewyork.com',                                                                                                                
    'Connection':        'keep-alive',                                                                                                                                   
    'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257',                               
    'Referer':           'http://www.supremenewyork.com/mobile'   
}
addPayload={
    'size': str(variant),
    'qty':  '1'
}
print UTCtoEST() +' :: Adding product to cart...'
addResp=session.post(addUrl,data=addPayload,headers=addHeaders)

print UTCtoEST() +' :: Checking status code of response...'

if addResp.status_code!=200:
    print UTCtoEST() +' ::',addResp.status_code,'Error \nExiting...'
    print
    sys.exit()
else:
    if addResp.json()==[]:
        print UTCtoEST() +' :: Response Empty! - Problem Adding to Cart\nExiting...'
        print
        sys.exit()
    print UTCtoEST() +' :: '+str(cw)+' - '+addResp.json()[0]['name']+' - '+ addResp.json()[0]['size_name']+' added to cart!'
    
    checkoutUrl='https://www.supremenewyork.com/checkout.json'
    checkoutHeaders={
        'host':              'www.supremenewyork.com',
        'If-None-Match':    '"*"',
        'Accept':            'application/json',                                                                                                                             
        'Proxy-Connection':  'keep-alive',                                                                                                                                   
        'Accept-Encoding':   'gzip, deflate',                                                                                                                                
        'Accept-Language':   'en-us',                                                                                                                                        
        'Content-Type':      'application/x-www-form-urlencoded',                                                                                                            
        'Origin':            'http://www.supremenewyork.com',                                                                                                                
        'Connection':        'keep-alive',                                                                                                                                   
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257',                               
        'Referer':           'http://www.supremenewyork.com/mobile'   
    }

    #################################
    # FILL OUT THESE FIELDS AS NEEDED
    #################################
    checkoutPayload={
        'store_credit_id':    '',      
        'from_mobile':              '1',
        'cookie-sub':               '%7B%22'+str(variant)+'%22%3A1%7D',       # cookie-sub: eg. {"VARIANT":1} urlencoded
        'same_as_billing_address':  '1',                                    
        'order[billing_name]':      'anon mous',                              # FirstName LastName
        'order[email]':             'anon@mailinator.com',                    # email@domain.com
        'order[tel]':               '999-999-9999',                           # phone-number-here
        'order[billing_address]':   '123 Seurat lane',                        # your address
        'order[billing_address_2]': '',
        'order[billing_zip]':       '90210',                                  # zip code
        'order[billing_city]':      'Beverly Hills',                          # city
        'order[billing_state]':     'CA',                                     # state
        'order[billing_country]':   'USA',                                    # country
        'store_address':            '1',                                
        'credit_card[type]':        'visa',                                   # master or visa
        'credit_card[cnb]':         '9999 9999 9999 9999',                    # credit card number
        'credit_card[month]':       '01',                                     # expiration month
        'credit_card[year]':        '2026',                                   # expiration year
        'credit_card[vval]':        '123',                                    # cvc/cvv
        'order[terms]':             '0',
        'order[terms]':             '1'                
    }

    # GHOST CHECKOUT PREVENTION WITH ROLLING PRINT
    for i in range(5):
            sys.stdout.write("\r" +UTCtoEST()+ ' :: Sleeping for '+str(5-i)+' seconds to avoid ghost checkout...')
            sys.stdout.flush()
            time.sleep(1)
    print 
    print UTCtoEST()+ ' :: Firing checkout request!'
    checkoutResp=session.post(checkoutUrl,data=checkoutPayload,headers=checkoutHeaders)
    try:
        print UTCtoEST()+ ' :: Checkout',checkoutResp.json()['status'].title()+'!'
    except:
        print UTCtoEST()+':: Error reading status key of response!'
        print checkoutResp.json()
    print 
    print checkoutResp.json()
    if checkoutResp.json()['status']=='failed':
        print
        print '!!!ERROR!!! ::',checkoutResp.json()['errors']
    print
