# btop_tools

Tools to interact with BT One Phone vPBX. **If you do not have a BT OnePhone account** this is (probably) of **no use to you**. Accounts are only available to UK businesses.

BT OnePhone tech appears to be licensed from ECT INtellECT VPBX systems. These systems utilise cometd and the bayeux protocol. It is possible this software will work on systems from other countries that also license the same system; you would need to identify and update these URLs:

    url = "https://vpbxapp.btonephone.com/vpbx/j_spring_security_client_check"
    comedt = "https://vpbxapp.btonephone.com/vpbx/cometd"

This repo currently contains only one tool that will send SMS messages. Tools to interact with the address book/directory are viable.

## btop_sms.py

This python3 script will send an SMS through the BT OnePhone vPBX system. 

### Usage

Username and password are for the BT OnePhone account from which to send the SMS. Phone number and SMS_text are the recipient.

    import btop_sms
    
    btop_sms.send_btop_sms(
        username='447700900000',
        password='password',
        phone_number='07700900001',
        sms_txt='This is a test message')

The Alert Client software provided with BT OnePhone accounts limits to 160 characters (i.e. max SMS message size). However the API will correctly (sort of) send concatenated SMS up to 255 chars, which is presumably due to an internal memory limit in the vPBX.
