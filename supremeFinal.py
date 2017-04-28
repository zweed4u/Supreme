#!/bin/env python2.7

# Run around 1059 as early as 1055.
# Polling times vary pick something nice.
# Ghost checkout timer can be changed by 
# adjusting for loop range near bottom.
# Fill out personal data in checkout payload dict.

#TODO: wrap search and checkout in function
#implement better threading/search thread
#use config vals
import os, sys, json, time, requests, urllib2, threading, ConfigParser
from datetime import datetime

rootDirectory = os.getcwd()
c = ConfigParser.ConfigParser()
configFilePath = os.path.join(rootDirectory, 'config.cfg')
c.read(configFilePath)

class Config:
    poll=int(c.get('timeComponents','poll'))
    ghostCheckoutPrevention=c.get('timeComponents','ghostCheckoutPrevention')

    billingName=c.get('cardInfo','firstAndLast')
    email=c.get('cardInfo','email')
    phone=c.get('cardInfo','phone')
    streetAddress=c.get('cardInfo','address')
    zipCode=c.get('cardInfo','zip')
    shippingCity=c.get('cardInfo','city')
    shippingState=c.get('cardInfo','state')
    shippingCountry=c.get('cardInfo','country')
    cardType=c.get('cardInfo','cardType')
    cardNumber=c.get('cardInfo','cardNumber')
    cardMonth=c.get('cardInfo','cardMonth')
    cardYear=c.get('cardInfo','cardYear')
    cardCVV=c.get('cardInfo','cardCVV')

user_config = Config()

def UTCtoEST():
    current=datetime.now()
    return str(current) + ' EST'
print

print 
print UTCtoEST(),':: Parsing page...'
def supremeItemBuy(keyword, poll, color, sz, qty, ghostCheckoutPrevention):
    #while loop start here... (parameterize with different combinations of items/sizes/colors)
    def pollStock(keyword,poll,color,sz,qty):
        global ID
        global variant
        global cw
        global styleNum
        global myproduct
        global sizeName
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
            pollStock(keyword,poll,color,sz,qty)
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
                    styleNum=numCW['id']
                    for sizes in numCW['sizes']:
                        # SIZE TERMS HERE
                        if str(sizes['name'].title()) == sz: # Medium
                            found=1;
                            variant=str(sizes['id'])
                            cw=numCW['name']
                            sizeName=sizes['name']
                            print UTCtoEST(),':: Selecting size:', sizes['name'],'(',numCW['name'],')','(',str(sizes['id']),')'
            if found ==0:
                # DEFAULT CASE NEEDED HERE - EITHER COLORWAY NOT FOUND OR SIZE NOT IN RUN OF PRODUCT
                # PICKING FIRST COLORWAY AND LAST SIZE OPTION
                print UTCtoEST(),':: Selecting default colorway:',data['styles'][0]['name']
                sizeName=str(data['styles'][0]['sizes'][len(data['styles'][0]['sizes'])-1]['name'])
                variant=str(data['styles'][0]['sizes'][len(data['styles'][0]['sizes'])-1]['id'])
                cw=data['styles'][0]['name']
                styleNum=data['styles'][0]['id']
                print UTCtoEST(),':: Selecting default size:',sizeName,'(',variant,')'
    pollStock(keyword,poll,color,sz,qty)

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
        'style' : str(styleNum),
        'size': str(variant),
        'qty':  qty
    }
    print UTCtoEST() +' :: Adding product to cart...'
    addResp=session.post(addUrl,data=addPayload,headers=addHeaders)

    print UTCtoEST() +' :: Checking status code of response...'

    if addResp.status_code!=200:
        print UTCtoEST() +' ::',addResp.status_code,'Error \nExiting...' #CHECK THIS - DID ITEM ADD TO CART? MAKE POST AGAIN - something like while status != 200 - wait and request again
        print
        sys.exit()
    else:
        if addResp.json()==[]: #FIGURE OUT WHY EMPTY JSON RESPONSE 
            print UTCtoEST() +' :: Response Empty! - Problem Adding to Cart\nExiting...'  #CHECK THIS - DID ITEM ADD TO CART? MAKE POST AGAIN
            print
            sys.exit()
        assert addResp.json()[0]["in_stock"]==True,"Error Message: Not in stock"
        assert addResp.json()[0]["size_id"]==str(variant),"Error Message: Incorrect variant returned in response"
        print UTCtoEST() +' :: '+str(myproduct)+' - '+str(cw)+' - '+str(sizeName)+' added to cart!'
        
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

        ###########################################
        # FILL OUT THESE FIELDS AS NEEDED IN CONFIG
        ###########################################
        captchaResponse=''
        checkoutPayload={
            'store_credit_id':          '',      
            'from_mobile':              '1',
            'cookie-sub':               '%7B%22'+str(variant)+'%22%3A1%7D',                          # cookie-sub: eg. {"VARIANT":1} urlencoded
            'same_as_billing_address':  '1',
            'order[billing_name]':      user_config.billingName,
            'order[email]':             user_config.email,
            'order[tel]':               user_config.phone,
            'order[billing_address]':   user_config.streetAddress,
            'order[billing_address_2]': '',
            'order[billing_zip]':       user_config.zipCode,
            'order[billing_city]':      user_config.shippingCity,
            'order[billing_state]':     user_config.shippingState,
            'order[billing_country]':   user_config.shippingCountry,
            'store_address':            '1',
            'credit_card[type]':        user_config.cardType,
            'credit_card[cnb]':         user_config.cardNumber,
            'credit_card[month]':       user_config.cardMonth,
            'credit_card[year]':        user_config.cardYear,
            'credit_card[vval]':        user_config.cardCVV,
            'order[terms]':             '0',
            'order[terms]':             '1',
            'g-recaptcha-response':     captchaResponse,                         #Could integrate harvestor with below information
            'is_from_ios_native':       '1'
        }

        # GHOST CHECKOUT PREVENTION WITH ROLLING PRINT
        for countDown in range(ghostCheckoutPrevention):
                sys.stdout.write("\r" +UTCtoEST()+ ' :: Sleeping for '+str(ghostCheckoutPrevention-countDown)+' seconds to avoid ghost checkout...')
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


if __name__ == '__main__':
    assert len(c.options('productName'))==len(c.options('productSize'))==len(c.options('productColor'))==len(c.options('productQty')),'Assertion Error: Product section lengths unmatched'
    for enumerableItem in range(0, len(c.options('productName'))):
        itemName=c.get('productName',c.options('productName')[enumerableItem]).title()
        itemSize=c.get('productSize',c.options('productSize')[enumerableItem]).title()
        itemColor=c.get('productColor',c.options('productColor')[enumerableItem]).title()
        itemQty=c.get('productQty',c.options('productQty')[enumerableItem])
        print itemName, itemSize, itemColor, itemQty,'Thread initialized!'
        print
        t = threading.Thread(target=supremeItemBuy, args=(itemName, user_config.poll, itemColor, itemSize, itemQty, user_config.ghostCheckoutPrevention,))
        t.start()
    print
    