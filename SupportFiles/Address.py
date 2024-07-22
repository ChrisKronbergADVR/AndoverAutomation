import requests


class Address:
    number_of_addresses = 1
    city = None
    state = None
    address1 = None
    address2 = None

    addresses = {
        "CT1": ["CT", "Waterbury", "1250 W Main St"],
        "CT2": ["CT", "Milddletown", "871 Washington St"],
        "IL1": ["IL", "Urbana", "1401 W Green St"],
        "IL2": ["IL", "Fairview Heights", "4701 N Illinois St"],
        "ME1": ["ME", "South Portland", "364 Maine Mall Rd"],
        "ME2": ["ME", "Portland", "1080 Forest Ave"],
        "MA1": ["MA", "Cambridge", "1662 Massechusetts AVe"],
        "MA2": ["MA", "Arlington", "1465 Massachusetts Ave"],
        "NH1": ["NH", "Manchester", "1111 S Willow St"],
        "NH2": ["NH", "Salem", "203 S Broadway"],
        "NJ1": ["NJ", "Jackson", "50 Hannah Hill Rd"],
        "NJ2": ["NJ", "Jackson", "426 Chandler Rd"],
        "NY1": ["NY", "New York", "1500 Broadway"],
        "NY2": ["NY", "New York", "424 Park Ave S"],
        "RI1": ["RI", "Providence", "468 Angell St"],
        "RI2": ["RI", "Warwick", "25 Pace Blvd"]
    }

    custom_address = {"Address": "", "Address2": "", "City": "", "Flag": False}

    def verify_address(city, state, address1, address2=None):
        global verified
        verified = False

        if address2 == None:
            address_validaiton_request = requests.post(f"""http://production.shippingapis.com/ShippingAPI.dll?API=Verify
                                                        &XML=<AddressValidateRequest USERID="005FSELF04917"><Address
                                                        ID="0"><Address1>{address1}</Address1>
                                                        <Address2></Address2><City>{city}</City><State>{state}</State>
                                                        <Zip5></Zip5><Zip4></Zip4></Address></AddressValidateRequest>""")
        else:
            address_validaiton_request = requests.post(f"""http://production.shippingapis.com/ShippingAPI.dll?API=Verify
                                                        &XML=<AddressValidateRequest USERID="005FSELF04917"><Address
                                                        ID="0"><Address1>{address1}</Address1>
                                                        <Address2>{address2}</Address2><City>{city}</City><State>{state}</State>
                                                        <Zip5></Zip5><Zip4></Zip4></Address></AddressValidateRequest>""")

        if not address_validaiton_request.text.__contains__('Error'):
            verified = True

        return verified
