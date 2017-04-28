#!/usr/bin/python
import os, sys, json, time, requests, urllib2, threading, ConfigParser, types, functools

global mobileStockJson
global stopPoll
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

def copy_func(f):
    g = types.FunctionType(f.func_code, f.func_globals, name=f.func_name,
                           argdefs=f.func_defaults,
                           closure=f.func_closure)
    g = functools.update_wrapper(g, f)
    return g

def productThread(name, size, color, qty):
    #include sleep and found flag to break in main - try catch fo NULL init handling
    while 1:
        while not(mobileStockJson):
            pass
        for category in range(0, len(mobileStockJson['products_and_categories'].values())):
            for item in range(0, len(mobileStockJson['products_and_categories'].values()[category])):
                #print mobileStockJson['products_and_categories'].values()[category][item]['name']
                if name in mobileStockJson['products_and_categories'].values()[category][item]['name']:
                    #Retain useful info here like index but mostly the id for add request
                    stopPoll=1
                    listedProductName=mobileStockJson['products_and_categories'].values()[category][item]['name']
                    productID=mobileStockJson['products_and_categories'].values()[category][item]['id']
                    print
                    print "Item found! :: ",listedProductName,productID
                    print
        if (stopPoll!=1): 
            print "Item not found :: ",name
            time.sleep(user_config.poll)
        else:
            #Item found continue to add and checkout
            break


if __name__ == '__main__':
    mobileStockJson=None
    stopPoll=0
    user_config = Config()
    assert len(c.options('productName'))==len(c.options('productSize'))==len(c.options('productColor'))==len(c.options('productQty')),'Assertion Error: Product section lengths unmatched'
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
        if (stopPoll!=1):
            mobileStockJson = mobileStockPollSession.get('http://www.supremenewyork.com/mobile_stock.json', headers=headers).json()
            time.sleep(user_config.poll)
        else:
            #Item/s found! wait for thread completion
            pass 