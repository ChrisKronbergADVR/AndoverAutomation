import requests

class Address:
    number_of_addresses = 1
    city = None
    state = None
    address1 = None
    address2 = None

    addresses = {
        "CT": ["CT", "Waterbury", "1250 W Main St"],
        "IL": ["IL", "Urbana", "1401 W Green St"],
        "ME": ["ME", "South Portland", "364 Maine Mall Rd"],
        "MA": ["MA", "Cambridge", "1662 Massechusetts AVe"],
        "NH": ["NH", "Manchester", "1111 S Willow St"],
        "NJ": ["NJ", "Jackson", "50 Hannah Hill Rd"],
        "NY": ["NY", "New York", "1500 Broadway"],
        "RI": ["RI", "Providence", "468 Angell St"],
    }

    custom_address = {"Address": "", "Address2": "", "City": "", "Flag": False}

    def verify_address(self,city, state, address1, address2=None):
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
