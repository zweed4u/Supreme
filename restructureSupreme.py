#!/usr/bin/python
import os, sys, json, time, requests, urllib2, threading, ConfigParser
from datetime import datetime
from functionCreate import copy_func

global stopPoll
global mobileStockJson

rootDirectory = os.getcwd()
c = ConfigParser.ConfigParser()
configFilePath = os.path.join(rootDirectory, 'config.cfg')
c.read(configFilePath)

class Config:
    poll = int(c.get('timeComponents','poll'))
    ghostCheckoutPrevention = int(c.get('timeComponents','ghostCheckoutPrevention'))
    billingName = c.get('cardInfo','firstAndLast')
    email = c.get('cardInfo','email')
    phone = c.get('cardInfo','phone')
    streetAddress = c.get('cardInfo','address')
    zipCode = c.get('cardInfo','zip')
    shippingCity = c.get('cardInfo','city')
    shippingState = c.get('cardInfo','state')
    shippingCountry = c.get('cardInfo','country')
    cardType = c.get('cardInfo','cardType')
    cardNumber = c.get('cardInfo','cardNumber')
    cardMonth = c.get('cardInfo','cardMonth')
    cardYear = c.get('cardInfo','cardYear')
    cardCVV = c.get('cardInfo','cardCVV')

def UTCtoEST():
    current=datetime.now()
    return str(current) + ' EST'

def productThread(name, size, color, qty):
    #include sleep and found flag to break in main - try catch fo NULL init handling
    stopPoll = 0
    while 1:
        while not(mobileStockJson):
            pass
        for category in range(0, len(mobileStockJson['products_and_categories'].values())):
            for item in range(0, len(mobileStockJson['products_and_categories'].values()[category])):
                #print mobileStockJson['products_and_categories'].values()[category][item]['name']
                if name in mobileStockJson['products_and_categories'].values()[category][item]['name']:
                    #Retain useful info here like index but mostly the id for add request
                    stopPoll = 1
                    listedProductName = mobileStockJson['products_and_categories'].values()[category][item]['name']
                    productID = mobileStockJson['products_and_categories'].values()[category][item]['id']
                    print
                    print UTCtoEST(),'::',listedProductName, productID, 'found ( MATCHING ITEM DETECTED )'
                    print
        if (stopPoll != 1): 
            print UTCtoEST(),':: Reloading and reparsing page...'
            time.sleep(user_config.poll)
        else:
            #Item found continue to add and checkout
            foundItemColor = 0
            foundItemSize = 0
            atcSession = requests.session()
            print UTCtoEST(),':: Selecting',listedProductName,'(',productID,')'
            productItemData = atcSession.get('http://www.supremenewyork.com/shop/'+str(productID)+'.json',headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257'}).json()
            for listedProductColors in productItemData['styles']:
                if color in listedProductColors['name']:
                    foundItemColor = 1
                    selectedColor = color
                    colorProductId = listedProductColors['id']
                    for listedProductSizes in listedProductColors['sizes']:
                        if size in listedProductSizes['name']:
                            foundItemSize = 1
                            selectedSize = size
                            sizeProductId = listedProductSizes['id']
                            print UTCtoEST(),':: Selecting size:', selectedSize,'(',selectedColor,')','(',sizeProductId,')'
                            break
            if (foundItemColor == 0 or foundItemSize == 0):
                #couldn't find user desired selection of color and size. picking defaults
                print UTCtoEST(),':: Selecting default colorway:',productItemData['styles'][0]['name']
                selectedSize = str(productItemData['styles'][0]['sizes'][len(productItemData['styles'][0]['sizes'])-1]['name'])
                sizeProductId = str(productItemData['styles'][0]['sizes'][len(productItemData['styles'][0]['sizes'])-1]['id'])
                selectedColor = productItemData['styles'][0]['name']
                colorProductId = productItemData['styles'][0]['id']
                print UTCtoEST(),':: Selecting default size:', selectedSize,'(',selectedColor,')','(',sizeProductId,')'

            productATCSession = requests.session()
            addUrl = 'http://www.supremenewyork.com/shop/'+str(productID)+'/add.json'
            atcSessionHeaders = {
                'Host':              'www.supremenewyork.com',
                'Accept':            'application/json',
                'Proxy-Connection':  'keep-alive',
                'X-Requested-With':  'XMLHttpRequest',
                'Accept-Encoding':   'gzip, deflate',
                'Accept-Language':   'en-us',
                'Content-Type':      'application/x-www-form-urlencoded',
                'Origin':            'http://www.supremenewyork.com',
                'Connection':        'keep-alive',
                'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34',
                'Referer':           'http://www.supremenewyork.com/mobile'
            }
            addPayload = {
                'style' : str(colorProductId),
                'size': str(sizeProductId),
                'qty':  qty
            }
            print UTCtoEST() +' :: Adding product to cart...'
            addResp = productATCSession.post(addUrl,data=addPayload,headers=atcSessionHeaders)
            if addResp.status_code != 200: #DID ITEM ADD TO CART - wait/sleep and make POST again
                print UTCtoEST() +' ::',addResp.status_code,'Error \nExiting...'
                print addResp.json()
                print
                sys.exit()
            else:
                if addResp.json() == []: #request was OK but did not add item to cart - wait/sleep and make POST again
                    print UTCtoEST() +' :: Response Empty! - Problem Adding to Cart\nExiting...'  #CHECK THIS - DID ITEM ADD TO CART? MAKE POST AGAIN
                    print
                    sys.exit()
                print UTCtoEST() +' :: [['+listedProductName+' - '+str(selectedColor)+' - '+str(selectedSize)+']] added to cart!'
                checkoutUrl = 'https://www.supremenewyork.com/checkout.json'
                del atcSessionHeaders['X-Requested-With']
                captchaResponse = '' #need mutex here to declare from pop of global solved captcha token - define captchaTokens=['token1','token2','token3'] at top/global - captchaResponse = captchaTokens.pop() #last element taken
                ###########################################
                # FILL OUT THESE FIELDS AS NEEDED IN CONFIG
                ###########################################
                checkoutPayload = {
                    'store_credit_id':          '',      
                    'from_mobile':              '1',
                    'cookie-sub':               '%7B%22'+str(sizeProductId)+'%22%3A1%7D', # cookie-sub: eg. {"VARIANT":1} urlencoded
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
                    'g-recaptcha-response':     captchaResponse, #Could integrate harvester
                    'is_from_ios_native':       '1'
                }
                # GHOST CHECKOUT PREVENTION WITH ROLLING PRINT
                '''
                for countDown in range(user_config.ghostCheckoutPrevention):
                        sys.stdout.write("\r" +UTCtoEST()+ ' :: Sleeping for '+str(user_config.ghostCheckoutPrevention-countDown)+' seconds to avoid ghost checkout...')
                        sys.stdout.flush()
                        time.sleep(1)
                '''
                print "[["+str(threading.current_thread().getName())+"]] Waiting for",str(user_config.ghostCheckoutPrevention),"seconds to avoid ghost checkout!"
            print
            break

if __name__ == '__main__':
    stopPoll = 0
    mobileStockJson = None
    user_config = Config()
    assert len(c.options('productName')) == len(c.options('productSize')) == len(c.options('productColor')) == len(c.options('productQty')),'Assertion Error: Product section lengths unmatched'
    for enumerableItem in range(0, len(c.options('productName'))):
        itemName = c.get('productName',c.options('productName')[enumerableItem]).title()
        itemSize = c.get('productSize',c.options('productSize')[enumerableItem]).title()
        itemColor = c.get('productColor',c.options('productColor')[enumerableItem]).title()
        itemQty = c.get('productQty',c.options('productQty')[enumerableItem])
        exec('productThread'+str(enumerableItem+1) + " = copy_func(productThread)")
        myThreadFunc = 'productThread'+str(enumerableItem+1)+'("'+itemName+'","'+itemSize+'","'+itemColor+'","'+itemQty+'")'
        myThreadFunc = eval('productThread'+str(enumerableItem+1))
        print itemName, itemSize, itemColor, itemQty,'Thread initialized!'
        t = threading.Thread(target=myThreadFunc, args=(itemName, itemSize, itemColor, itemQty,))
        #t = threading.Thread(target=exec(myThreadFunc), args=(itemName, user_config.poll, itemColor, itemSize, itemQty, user_config.ghostCheckoutPrevention,))
        t.start()

    mobileStockPollSession = requests.session()
    headers = {
        'Host':              'www.supremenewyork.com',
        'Accept-Encoding':   'gzip, deflate',
        'Connection':        'keep-alive',
        'Proxy-Connection':  'keep-alive',
        'Accept':            'application/json',
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34',
        'Referer':           'http://www.supremenewyork.com/mobile',
        'Accept-Language':   'en-us',
        'X-Requested-With':  'XMLHttpRequest'
    }

    while 1:
        if (stopPoll != 1):
            mobileStockJson = mobileStockPollSession.get('http://www.supremenewyork.com/mobile_stock.json', headers=headers).json()
            time.sleep(user_config.poll)
        else:
            #Item/s found! wait for thread completion
            pass 
