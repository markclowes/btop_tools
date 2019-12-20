import urllib.parse
import sys
from time import sleep
import requests
import json

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def send_btop_sms(username, password, phone_number, sms_txt):
    # Hello there, hi, welcome!
    # This was reverse engineered by monitoring the comms
    # between the BT One Phone Alert Client software and
    # their systems using Fiddler MITM proxying!

    # For future reference:
    # Their system utilises 'cometd' and the bayeux protocol
    # The BTOP system is actually ECT INtellECT VPBX system

    # sms_txt cannot exceed 255 chars
    # which is interesting, as the alert client limits to 160
    # so it will send concat SMS up to this 255 limit
    # some sort of internal memory limit
    try:
        # escape quotes that would break JSON
        sms_txt = sms_txt.replace('"','\\"')

        session = requests.Session()

        url = "https://vpbxapp.btonephone.com/vpbx/j_spring_security_client_check"
        comedt = "https://vpbxapp.btonephone.com/vpbx/cometd"

        # Clone Alert Client headers
        headers = {
            "Referer": "app:/AlertClient.swf",
            "Accept": "text/xml, application/xml, application/xhtml+xml, "
            "text/html;q=0.9, text/plain;q=0.8, text/css, image/png, image/jpeg, "
            "image/gif;q=0.8, application/x-shockwave-flash, video/mp4;q=0.9, "
            "flv-application/octet-stream;q=0.8, video/x-flv;q=0.7, audio/mp4, "
            "application/futuresplash, */*;q=0.5, application/x-mpegURL",
            "x-flash-version": "25,0,0,127",
            "Content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,deflate",
            "User-Agent": "Mozilla/5.0 (Windows; U; en-GB) AppleWebKit/533.19.4 (KHTML, like Gecko) AdobeAIR/25.0",
            "Connection": "Keep-Alive",
        }

        #####################################

        print("\n***** Logging in")
        # This gets us a login cookie
        # Requests module session handles all this for us subsequently

        body = ('j%5Fusername=' + username + '&j%5Fpassword=' + password)

        print('Sending:', body)
        r = session.post(url=url, data=body, headers=headers, verify=False)
        print('Received: ', r.headers)
        print('Received: ', r.text.strip('\n'))
        d = json.loads(r.text)
        print('Given response: ', d['response'])
        if d['response'].lower() != 'ok':
            print("Login failure!")
            return False

        #####################################
        sleep(0.2)

        print("\n***** Handshaking!")
        # This gets us a clientId, needed for all future comms

        raw = ('[{"id":"0",' +
        '"minimumVersion":"0.9",' +
        '"supportedConnectionTypes":["long-polling","long-polling-json-encoded","callback-polling"],' +
        '"version":"1.0",' +
        '"ext":{"json-comment-filtered":false},' +
        '"channel":"/meta/handshake"}]')

        print('Sending: ', raw)
        body = 'message=' + urllib.parse.quote(raw)
        r = session.post(url=comedt, data=body, headers=headers, verify=False)

        print('Received: ', r.headers)
        print('Received: ', r.text)
        
        # strip first and last chars [ ] 
        d = json.loads(r.text[1:-1])
        print('Given clientId: ', d['clientId'])
        print('Given success: ', d['successful'])
        clientId = d['clientId']

        d = json.loads(r.text[1:-1])
        if not d['successful']:
            print("Login failure!")
            return False

        #####################################
        sleep(0.2)

        print("\n***** Connecting!")

        raw = ('[{"clientId":"' + d['clientId'] + '",' +
        '"id":1337,' +
        '"connectionType":"long-polling",' +
        '"channel":"/meta/connect"}]')

        print('Sending: ', raw)
        body = 'message=' + urllib.parse.quote(raw)
        r = session.post(url=comedt, data=body, headers=headers, verify=False)

        print('Received: ', r.headers)
        print('Received: ', r.text)

        d = json.loads(r.text[1:-1])
        if not d['successful']:
            print("Login failure!")
            return False
        
        #####################################

        sleep(0.2)

        print("\n***** Subscribing!")
        raw = ('[{"clientId":"' + clientId + '",' +
        '"subscription":"/service/client",' +
        '"channel":"/meta/subscribe"}]')

        print('Sending: ', raw)
        body = 'message=' + urllib.parse.quote(raw)
        r = session.post(url=comedt, data=body, headers=headers, verify=False)

        print('Received: ', r.headers)
        print('Received: ', r.text)

        d = json.loads(r.text[1:-1])
        if not d['successful']:
            print("Login failure!")
            return False

        #####################################

        # split long text into multiple SMS
        for chunk in chunkstring(sms_txt, 255):
            sleep(1)
            print("\n***** Sending SMS!")

            raw = ('[{"clientId":"' + clientId + '",' +
            '"data":{"class":"com.ect.mo.acsoap.messages.SendSmsMessage",' +
            '"phoneNumber":"' + phone_number + '",' +
            '"message":"' + chunk + '",' +
            '"sendTo":null},' +
            '"channel":"/service/client"}]')
            print(session.cookies.get_dict())

            print(raw)
            # urllib parse won't do the forward slashes!
            # or dots!
            urlencoded = urllib.parse.quote(raw)
            urlencoded = urlencoded.replace('/', '%2F')
            urlencoded = urlencoded.replace('.', '%2E')
            body = 'message=' + urlencoded

            print('Sending: ', body)
            r = session.post(url=comedt, data=body, headers=headers, verify=False)

            print('Received: ', r.headers)
            print('Received: ', r.text)

        #####################################

        sleep(0.2)

        print("\n***** Unsubscribing!")
        raw = ('[{"clientId":"' + clientId + '",' +
        '"subscription":"/service/client",' +
        '"channel":"/meta/unsubscribe"}]')

        print('Sending: ', raw)
        body = 'message=' + urllib.parse.quote(raw)
        r = session.post(url=comedt, data=body, headers=headers, verify=False)

        print('Received: ', r.headers)
        print('Received: ', r.text)

        #####################################
        sleep(0.2)

        print("\n***** Disconnecting!")

        raw = ('[{"clientId":"' + clientId + '",' +
        '"channel":"/meta/disconnect"}]')

        print('Sending: ', raw)
        body = 'message=' + urllib.parse.quote(raw)
        r = session.post(url=comedt, data=body, headers=headers, verify=False)

        print('Received: ', r.headers)
        print('Received: ', r.text)

        print('***** All done!')

    except:
        raise
        return False

    return True

