#!/usr/bin/python2
import os
import sys
import json
import time
import requests
import urllib
import random
import threading
import ConfigParser
from datetime import datetime
from functionCreate import copy_func
from selenium import webdriver
from requests.utils import dict_from_cookiejar
from colorCodes import *
from tokenContainer import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

global mobileStockJson

rootDirectory = os.getcwd()
c = ConfigParser.ConfigParser()
configFilePath = os.path.join(rootDirectory, 'config.cfg')
c.read(configFilePath)


class Config:
    poll = int(c.get('timeComponents', 'poll'))
    ghostCheckoutPrevention = int(
        c.get('timeComponents', 'ghostCheckoutPrevention'))
    billingName = c.get('cardInfo', 'firstAndLast')
    email = c.get('cardInfo', 'email')
    phone = c.get('cardInfo', 'phone')
    streetAddress = c.get('cardInfo', 'address')
    zipCode = c.get('cardInfo', 'zip')
    shippingCity = c.get('cardInfo', 'city')
    shippingState = c.get('cardInfo', 'state')
    shippingCountry = c.get('cardInfo', 'country')
    cardType = c.get('cardInfo', 'cardType')
    cardNumber = c.get('cardInfo', 'cardNumber')
    cardMonth = c.get('cardInfo', 'cardMonth')
    cardYear = c.get('cardInfo', 'cardYear')
    cardCVV = c.get('cardInfo', 'cardCVV')


def UTCtoEST():
    current = datetime.now()
    return str(current) + ' EST'


def productThread(name, size, color, qty, textColor, selectedCaptchaToken):
    # include sleep and found flag to break in main - try catch fo NULL init handling
    global stopPoll, checkedOut
    stopPoll = 0
    checkedOut = 0
    while 1:
        while not mobileStockJson:
            pass
        for category in range(0, len(
                mobileStockJson['products_and_categories'].values())):
            for item in range(0, len(
                    mobileStockJson['products_and_categories'].values()[
                        category])):
                if name.lower() in mobileStockJson['products_and_categories'].values()[
                    category][item]['name'].lower():
                    # Retain useful info here like index but mostly the id for add request
                    stopPoll = 1
                    listedProductName = \
                        mobileStockJson['products_and_categories'].values()[
                            category][item]['name']
                    productID = \
                        mobileStockJson['products_and_categories'].values()[
                            category][item]['id']
                    sys.stdout.write("[[" + textColor + str(
                        threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: [[' + textColor + listedProductName + COLOR_END + ']] ' + str(
                        productID) + ' found ( MATCHING ITEM DETECTED )' + '\n')
        if (stopPoll != 1):
            sys.stdout.write("[[" + textColor + str(
                threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Reloading and reparsing page...' + '\n')
            time.sleep(user_config.poll)
        else:
            # Item found continue to add and checkout
            foundItemColor = 0
            foundItemSize = 0
            atcSession = requests.session()
            sys.stdout.write("[[" + textColor + str(
                threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Selecting [[' + textColor + listedProductName + COLOR_END + ']] ( ' + str(
                productID) + ' )' + '\n')
            productItemData = atcSession.get(
                'http://www.supremenewyork.com/shop/' + str(
                    productID) + '.json', headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257'}).json()
            for listedProductColors in productItemData['styles']:
                if color.lower() in listedProductColors['name'].lower():
                    foundItemColor = 1
                    selectedColor = color
                    colorProductId = listedProductColors['id']
                    for listedProductSizes in listedProductColors['sizes']:
                        if size.lower() in listedProductSizes['name'].lower():
                            foundItemSize = 1
                            selectedSize = size
                            sizeProductId = listedProductSizes['id']
                            sys.stdout.write("[[" + textColor + str(
                                threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Selecting size for [[' + textColor + listedProductName + COLOR_END + ']] - ' + selectedSize + ' ( ' + selectedColor + ' ) ' + ' ( ' + str(
                                sizeProductId) + ' )' + '\n')
                            break
            if foundItemColor == 0 or foundItemSize == 0:
                # couldn't find user desired selection of color and size. picking defaults
                sys.stdout.write("[[" + textColor + str(
                    threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Selecting default colorway: ' +
                                 productItemData['styles'][0]['name'] + '\n')
                selectedSize = str(productItemData['styles'][0]['sizes'][len(
                    productItemData['styles'][0]['sizes']) - 1]['name'])
                sizeProductId = str(productItemData['styles'][0]['sizes'][len(
                    productItemData['styles'][0]['sizes']) - 1]['id'])
                selectedColor = productItemData['styles'][0]['name']
                colorProductId = productItemData['styles'][0]['id']
                sys.stdout.write("[[" + textColor + str(
                    threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Selecting default size: ' + selectedSize + ' ( ' + selectedColor + ' ) ' + ' ( ' + str(
                    sizeProductId) + ' )' + '\n')

            productATCSession = requests.session()
            addUrl = 'http://www.supremenewyork.com/shop/' + str(
                productID) + '/add.json'
            atcSessionHeaders = {
                'Host': 'www.supremenewyork.com',
                'Accept': 'application/json',
                'Proxy-Connection': 'keep-alive',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-us',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'http://www.supremenewyork.com',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34',
                'Referer': 'http://www.supremenewyork.com/mobile'
            }
            addPayload = {
                's': str(sizeProductId),
                'st': str(colorProductId),
                'qty': qty
            }
            sys.stdout.write("[[" + textColor + str(
                threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Adding [[' + textColor + listedProductName + COLOR_END + ']] to cart...' + '\n')
            addResp = productATCSession.post(addUrl, data=addPayload,
                                             headers=atcSessionHeaders)
            if addResp.status_code != 200:  # DID ITEM ADD TO CART - wait/sleep and make POST again
                sys.stdout.write("[[" + textColor + str(
                    threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' ::',
                                 addResp.status_code,
                                 'Error [[' + textColor + listedProductName + COLOR_END + ']] ' + FAIL + 'FAILED!' + COLOR_END + '\n')
                sys.stdout.write("[[" + textColor + str(
                    threading.current_thread().getName()) + COLOR_END + "]] " + addResp.json() + '\n')
                sys.exit()
            else:
                if addResp.json() == []:  # request was OK but did not add item to cart - wait/sleep and make POST again
                    sys.stdout.write("[[" + textColor + str(
                        threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Response Empty! - Problem Adding to Cart! [[' + textColor + listedProductName + COLOR_END + ']] ' + FAIL + 'FAILED!' + COLOR_END + '\n')  # CHECK THIS - DID ITEM ADD TO CART? MAKE POST AGAIN
                    sys.exit()
                sys.stdout.write("[[" + textColor + str(
                    threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: [[' + textColor + listedProductName + ' - ' + str(
                    selectedColor) + ' - ' + str(
                    selectedSize) + COLOR_END + ']] added to cart!' + '\n')

                """
                This is where we should implement a webdriver
                Grab cookies from current thread's session and import them in webdriver
                Also print these cookies in EditThisCookie import format  
                Take values used in payload/from config and make use of send keys
                Try/except where if selector cant be found user can manually enter
                """

                cookie_dict_wrapper = []
                for key, value in requests.utils.dict_from_cookiejar(
                        addResp.cookies).items():
                    dict_template = {
                        "domain": ".supremenewyork.com",
                        "expiry": int(time.time() + 7200),
                        "httpOnly": False,
                        "path": "/",
                        "secure": False
                    }
                    dict_template['name'] = key
                    dict_template['value'] = value
                    cookie_dict_wrapper.append(dict_template)
                print '\tEditThisCookie Import\t'
                print '####################################################################################################################################{}'.format(
                    textColor)
                print json.dumps(cookie_dict_wrapper, indent=4)
                print '{}####################################################################################################################################'.format(
                    COLOR_END)
                driver = webdriver.Chrome('{}/chromedriver'.format(
                    os.getcwd()))  # chromedriver bin must be in folder of invocation -implement check
                driver.get(
                    'http://www.supremenewyork.com/shop/cart')  # commonly carts
                driver.delete_all_cookies()
                for key, value in dict_from_cookiejar(addResp.cookies).items():
                    driver.add_cookie({'name': key, 'value': value})
                driver.refresh()
                driver.get('https://www.supremenewyork.com/checkout')
                # print json.dumps(driver.get_cookies(), indent=4)  # trust that cookies were transferred to selenium properly - EditThisCookie use case
                # This is awful - sorry - safeguard against selector changes
                try:
                    customer_name = driver.find_element_by_name('order[billing_name]')
                    customer_name.clear()
                    customer_name.send_keys(user_config.billingName)
                except:
                    print 'Couldn\'t find order billing name field'
                    raw_input('Click to continue automation...')
                try:
                    customer_email = driver.find_element_by_name('order[email]')
                    customer_email.clear()
                    customer_email.send_keys(user_config.email)
                except:
                    print 'Couldn\'t find order email field'
                    raw_input('Click to continue automation...')
                try:
                    customer_telephone = driver.find_element_by_id('order_tel')
                    customer_telephone.clear()
                    customer_telephone.send_keys(user_config.phone)
                except:
                    print 'Couldn\'t find order tel field'
                    raw_input('Click to continue automation...')
                try:
                    customer_address = driver.find_element_by_name('order[billing_address]')
                    customer_address.clear()
                    customer_address.send_keys(user_config.streetAddress)
                except:
                    print 'Couldn\'t find order[billing_address] field (address)'
                    raw_input('Click to continue automation...')
                try:
                    customer_zip = driver.find_element_by_name('order[billing_zip]')
                    customer_zip.clear()
                    customer_zip.send_keys(user_config.zipCode)
                except:
                    print 'Couldn\'t find order billing zip field'
                    raw_input('Click to continue automation...')
                try:
                    # Let zip code auto fill this
                    pass
                    # customer_city = driver.find_element_by_id('order_billing_city')
                    # customer_city.click()
                    # customer_city.clear()
                    # customer_city.send_keys(user_config.shippingCity)
                except:
                    print 'Couldn\'t find order billing city field'
                    raw_input('Click to continue automation...')
                try:
                    customer_state = Select(driver.find_element_by_id('order_billing_state'))
                    customer_state.select_by_value(user_config.shippingState.upper())  # or visible text
                except:
                    print 'Couldn\'t find order billing state dropdown/value'
                    raw_input('Click to continue automation...')
                try:
                    customer_country = Select(driver.find_element_by_name(
                        'order[billing_country]'))
                    customer_country.select_by_value(user_config.shippingCountry.upper())  # or visible text (USA or CANADA)
                except:
                    print 'Couldn\'t find order billing country drowpdown/value'
                    raw_input('Click to continue automation...')
                try:
                    customer_card_number = driver.find_element_by_id('nnaerb')
                    customer_card_number.clear()
                    customer_card_number.send_keys(user_config.cardNumber)
                except:
                    print 'Couldn\'t find nnaerb field (card number)'
                    raw_input('Click to continue automation...')
                try:
                    customer_card_month = Select(driver.find_element_by_name(
                    'credit_card[month]'))  # month must be padded eg. 09
                    customer_card_month.select_by_value(user_config.cardMonth)
                except:
                    print 'Couldn\'t find credit card month dropdown/value'
                    raw_input('Click to continue automation...')
                try:
                    customer_card_year = Select(driver.find_element_by_name(
                        'credit_card[year]'))
                    customer_card_year.select_by_value(user_config.cardYear)
                except:
                    print 'Couldn\'t find credit card year dropdown/value'
                    raw_input('Click to continue automation...')
                try:
                    customer_card_cvv = driver.find_element_by_name(
                        'credit_card[rvv]')
                    customer_card_cvv.clear()
                    customer_card_cvv.send_keys(user_config.cardCVV)
                except:
                    print 'Couldn\'t find credit_card[rvv] field (card cvv)'
                    raw_input('Click to continue automation...')
                try:
                    accept_terms = driver.find_element_by_css_selector(
                        '#cart-cc > fieldset > p:nth-child(4) > label > div > ins')
                    accept_terms.click()
                except:
                    print 'Couldn\'t find accept terms radio button'
                    raw_input('Click to continue automation...')
                raw_input('NEXT STEP IS TO CHECKOUT')
                try:
                    checkout_button = driver.find_element_by_css_selector(
                        '#pay > input')
                    checkout_button.click()
                except:
                    print 'Couldn\'t find process/pay/checkout button'
                    raw_input('Click to continue automation...')

                #########################################################################
                #########################################################################
                #########################################################################
                """
                checkoutUrl = 'https://www.supremenewyork.com/checkout.json'
                del atcSessionHeaders['X-Requested-With']
                ###########################################
                # FILL OUT THESE FIELDS AS NEEDED IN CONFIG
                ###########################################
                checkoutPayload = {
                    'store_credit_id': '',
                    'from_mobile': '1',
                    'cookie-sub': urllib.quote_plus(
                        '{"' + str(sizeProductId) + '":1}'),
                    # cookie-sub: eg. {"VARIANT":1} urlencoded
                    'same_as_billing_address': '1',
                    'order[billing_name]': user_config.billingName,
                    'order[email]': user_config.email,
                    'order[tel]': user_config.phone,
                    'order[billing_address]': user_config.streetAddress,
                    'order[billing_address_2]': '',
                    'order[billing_zip]': user_config.zipCode,
                    'order[billing_city]': user_config.shippingCity,
                    'order[billing_state]': user_config.shippingState,
                    'order[billing_country]': user_config.shippingCountry,
                    'credit_card[cnb]': user_config.cardNumber,
                    'credit_card[month]': user_config.cardMonth,
                    'credit_card[year]': user_config.cardYear,
                    'credit_card[rsusr]': user_config.cardCVV,
                    'order[terms]': '0',
                    'g-recaptcha-response': selectedCaptchaToken,
                    # This is the param passed that can be found in tokenContainer.py - picked at random - manually populate that list in that file with tokens
                    'is_from_ios_native': '1'
                }
                # GHOST CHECKOUT PREVENTION WITH ROLLING PRINT
                for countDown in range(user_config.ghostCheckoutPrevention):
                    sys.stdout.write("\r[[" + textColor + str(
                        threading.current_thread().getName()) + COLOR_END + "]] Waiting for " + str(
                        user_config.ghostCheckoutPrevention - countDown) + " seconds to avoid ghost checkout!" + '\n')
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write("[[" + textColor + str(
                    threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Firing checkout request for [[' + textColor + listedProductName + COLOR_END + ']]' + '\n')
                checkoutResp = productATCSession.post(checkoutUrl,
                                                      data=checkoutPayload,
                                                      headers=atcSessionHeaders)
                if checkoutResp.status_code != 200:
                    sys.stdout.write("[[" + textColor + str(
                        threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Checkout response for [[' + textColor + listedProductName + COLOR_END + ']] NOT 200!' + '\n')
                    sys.exit()
                else:
                    # sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Checkout response for [['+listedProductName+']] 200!'+'\n')                 
                    # sys.stdout.write("[["+textColor+str(threading.current_thread().getName())+COLOR_END+"]] "+UTCtoEST()+' :: Checking status of [['+listedProductName+']] checkout'+'\n')                 
                    try:  # handle if 'status' key not in json response
                        if 'fail' in checkoutResp.json()['status'].lower():
                            sys.stdout.write("[[" + textColor + str(
                                threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Checkout for [[' + textColor + listedProductName + COLOR_END + ']] ' + FAIL + 'FAILED!' + COLOR_END + '\n')
                            sys.stdout.write("[[" + textColor + str(
                                threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: [[' + textColor + listedProductName + COLOR_END + ']] :: ' + FAIL + str(
                                checkoutResp.json()[
                                    'errors']) + COLOR_END + '\n')
                        else:
                            sys.stdout.write("[[" + textColor + str(
                                threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: Checkout for [[' + textColor + listedProductName + COLOR_END + ']] ' + str(
                                checkoutResp.json()['status']) + '\n')
                    except:  # couldnt find key - notify and just print whole response
                        sys.stdout.write("[[" + textColor + str(
                            threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: "status" key not found in [[' + textColor + listedProductName + COLOR_END + ']] checkout response' + '\n')
                        sys.stdout.write("[[" + textColor + str(
                            threading.current_thread().getName()) + COLOR_END + "]] " + UTCtoEST() + ' :: [[' + textColor + listedProductName + COLOR_END + ']] ' + str(
                            checkoutResp.json()) + '\n')
                    """
                checkedOut = 1
            break


if __name__ == '__main__':
    stopPoll = 0
    checkedOut = 0
    mobileStockJson = None
    user_config = Config()
    assert len(c.options('productName')) == len(
        c.options('productSize')) == len(c.options('productColor')) == len(
        c.options(
            'productQty')), 'Assertion Error: Product section lengths unmatched'
    for enumerableItem in range(0, len(c.options('productName'))):
        colorText = random.choice(list(colorCodes.values()))
        colorCodes = {key: val for key, val in colorCodes.items() if
                      val != colorText}  # update dict to not use the same color for another thread
        myCaptchaToken = random.choice(captchaTokenArray)
        captchaTokenArray.remove(
            myCaptchaToken)  # update list as to not reuse the same token
        itemName = c.get('productName',
                         c.options('productName')[enumerableItem]).title()
        itemSize = c.get('productSize',
                         c.options('productSize')[enumerableItem]).title()
        itemColor = c.get('productColor',
                          c.options('productColor')[enumerableItem]).title()
        itemQty = c.get('productQty', c.options('productQty')[enumerableItem])
        exec ('productThread' + str(
            enumerableItem + 1) + " = copy_func(productThread)")
        # myThreadFunc = 'productThread'+str(enumerableItem+1)+'("'+itemName+'","'+itemSize+'","'+itemColor+'","'+itemQty+'")'
        myThreadFunc = eval('productThread' + str(enumerableItem + 1))
        print "[[" + colorText + "Thread-" + str(
            enumerableItem + 1) + COLOR_END + "]] " + str(colorText) + str(
            itemName) + ' :: ' + str(itemSize) + ' :: ' + str(
            itemColor) + ' :: ' + str(
            itemQty) + ' :: Thread initialized!' + str(COLOR_END)
        t = threading.Thread(target=myThreadFunc, args=(
            itemName, itemSize, itemColor, itemQty, colorText,
            myCaptchaToken,))
        t.daemon = True
        t.start()
    print ''

    mobileStockPollSession = requests.session()
    headers = {
        'Host': 'www.supremenewyork.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Proxy-Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34',
        'Referer': 'http://www.supremenewyork.com/mobile',
        'Accept-Language': 'en-us',
        'X-Requested-With': 'XMLHttpRequest'
    }

    while 1:
        if stopPoll != 1:
            mobileStockJson = mobileStockPollSession.get(
                'http://www.supremenewyork.com/mobile_stock.json',
                headers=headers).json()
            time.sleep(user_config.poll)
        else:
            # Item/s found! wait for thread completion
            if checkedOut == 1:
                sys.exit()
