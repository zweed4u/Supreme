#!/usr/bin/python
import os, sys, json, time, requests, urllib, random, threading, ConfigParser
from datetime import datetime
from functionCreate import copy_func
from colorCodes import *
from tokenContainer import *

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

def productThread(name, size, color, qty, textColor, selectedCaptchaToken):
    #include sleep and found flag to break in main - try catch fo NULL init handling
    stopPoll = 0
    while 1:
        while not(mobileStockJson):
            pass
        for category in range(0, len(mobileStockJson['products_and_categories'].values())):
            for item in range(0, len(mobileStockJson['products_and_categories'].values()[category])):
                if name in mobileStockJson['products_and_categories'].values()[category][item]['name']:
                    #Retain useful info here like index but mostly the id for add request
                    stopPoll = 1
                    listedProductName = mobileStockJson['products_and_categories'].values()[category][item]['name']
                    productID = mobileStockJson['products_and_categories'].values()[category][item]['id']
                    sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: [['+textColor+listedProductName+COLOR_END+']] '+str(productID)+' found ( MATCHING ITEM DETECTED )'+ '\n')
        if (stopPoll != 1): 
            sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Reloading and reparsing page...'+ '\n')
            time.sleep(user_config.poll)
        else:
            #Item found continue to add and checkout
            foundItemColor = 0
            foundItemSize = 0
            atcSession = requests.session()
            sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Selecting [['+textColor+listedProductName+COLOR_END+']] ( '+str(productID)+' )' + '\n')
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
                            sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Selecting size for [['+textColor+listedProductName+COLOR_END+']] - '+ selectedSize+' ( '+selectedColor+' ) '+' ( '+str(sizeProductId)+' )' + '\n')
                            break
            if (foundItemColor == 0 or foundItemSize == 0):
                #couldn't find user desired selection of color and size. picking defaults
                sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Selecting default colorway: '+productItemData['styles'][0]['name'] + '\n')
                selectedSize = str(productItemData['styles'][0]['sizes'][len(productItemData['styles'][0]['sizes'])-1]['name'])
                sizeProductId = str(productItemData['styles'][0]['sizes'][len(productItemData['styles'][0]['sizes'])-1]['id'])
                selectedColor = productItemData['styles'][0]['name']
                colorProductId = productItemData['styles'][0]['id']
                sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Selecting default size: '+ selectedSize+' ( '+selectedColor+' ) '+' ( '+str(sizeProductId)+' )' + '\n')

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
            sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST() +' :: Adding [['+textColor+listedProductName+COLOR_END+']] to cart...' + '\n')
            addResp = productATCSession.post(addUrl,data=addPayload,headers=atcSessionHeaders)
            if addResp.status_code != 200: #DID ITEM ADD TO CART - wait/sleep and make POST again
                sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST() +' ::',addResp.status_code,'Error \nExiting...' + '\n')
                sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+addResp.json() + '\n')
                sys.exit()
            else:
                if addResp.json() == []: #request was OK but did not add item to cart - wait/sleep and make POST again
                    sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST() +' :: Response Empty! - Problem Adding to Cart\nExiting...' + '\n')  #CHECK THIS - DID ITEM ADD TO CART? MAKE POST AGAIN
                    sys.exit()
                sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST() +' :: [['+textColor+listedProductName+' - '+str(selectedColor)+' - '+str(selectedSize)+COLOR_END+']] added to cart!' + '\n')
                checkoutUrl = 'https://www.supremenewyork.com/checkout.json'
                del atcSessionHeaders['X-Requested-With']
                ###########################################
                # FILL OUT THESE FIELDS AS NEEDED IN CONFIG
                ###########################################
                checkoutPayload = {
                    'store_credit_id':          '',      
                    'from_mobile':              '1',
                    'cookie-sub':               urllib.quote_plus('{"'+str(sizeProductId)+'":1}'), # cookie-sub: eg. {"VARIANT":1} urlencoded
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
                    'g-recaptcha-response':     selectedCaptchaToken, #This is the param passed that can be found in tokenContainer.py - picked at random - manually populate that list in that file with tokens
                    'is_from_ios_native':       '1'
                }
                # GHOST CHECKOUT PREVENTION WITH ROLLING PRINT
                for countDown in range(user_config.ghostCheckoutPrevention):
                        sys.stdout.write("\r[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] Waiting for "+str(user_config.ghostCheckoutPrevention-countDown)+" seconds to avoid ghost checkout!" + '\n')
                        sys.stdout.flush()
                        time.sleep(1)
                sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Firing checkout request for [['+textColor+listedProductName+COLOR_END+']]'+'\n')
                checkoutResp = productATCSession.post(checkoutUrl,data=checkoutPayload,headers=atcSessionHeaders)
                if checkoutResp.status_code != 200:
                    sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Checkout response for [['+textColor+listedProductName+COLOR_END+']] NOT 200!'+'\n')
                    sys.exit()
                else:
                    #sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Checkout response for [['+listedProductName+']] 200!'+'\n')                 
                    #sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Checking status of [['+listedProductName+']] checkout'+'\n')                 
                    try: #handle if 'status' key not in json response
                        if 'fail' in checkoutResp.json()['status'].lower():
                            sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Checkout for [['+textColor+listedProductName+COLOR_END+']] '+FAIL+'FAILED!'+COLOR_END+'\n')
                            sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: [['+textColor+listedProductName+COLOR_END+']] :: '+FAIL+str(checkoutResp.json()['errors'])+COLOR_END+'\n')
                        else:
                            sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Checkout for [['+textColor+listedProductName+COLOR_END+']] '+str(checkoutResp.json()['status'])+'\n')
                    except: #couldnt find key - notify and just print whole response
                        sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: "status" key not found in [['+textColor+listedProductName+COLOR_END+']] checkout response'+'\n')
                        sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: [['+textColor+listedProductName+COLOR_END+']] '+str(checkoutResp.json())+'\n')
            break

if __name__ == '__main__':
    stopPoll = 0
    mobileStockJson = None
    user_config = Config()
    assert len(c.options('productName')) == len(c.options('productSize')) == len(c.options('productColor')) == len(c.options('productQty')),'Assertion Error: Product section lengths unmatched'
    for enumerableItem in range(0, len(c.options('productName'))):
        colorText = random.choice(colorCodes.values())
        colorCodes = {key:val for key, val in colorCodes.items() if val != colorText}   #update dict to not use the same color for another thread
        myCaptchaToken = random.choice(captchaTokenArray)
        captchaTokenArray.remove(myCaptchaToken)    #update list as to not reuse the same token
        itemName = c.get('productName',c.options('productName')[enumerableItem]).title()
        itemSize = c.get('productSize',c.options('productSize')[enumerableItem]).title()
        itemColor = c.get('productColor',c.options('productColor')[enumerableItem]).title()
        itemQty = c.get('productQty',c.options('productQty')[enumerableItem])
        exec('productThread'+str(enumerableItem+1) + " = copy_func(productThread)")
        #myThreadFunc = 'productThread'+str(enumerableItem+1)+'("'+itemName+'","'+itemSize+'","'+itemColor+'","'+itemQty+'")'
        myThreadFunc = eval('productThread'+str(enumerableItem+1))
        print "[["+colorText+"Thread-"+str(enumerableItem+1)+COLOR_END+"]]",colorText,itemName, itemSize, itemColor, itemQty,'Thread initialized!',COLOR_END
        t = threading.Thread(target=myThreadFunc, args=(itemName, itemSize, itemColor, itemQty, colorText, myCaptchaToken,))
        t.start()
    print

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
