# import requests
import logging
import xml.etree.ElementTree as ET

import requests


def get_clubs(api_key: str, filter_on_code: str = None) -> list[dict]:
    """ Uttrekk av Notodden OL som eksempel på hvordan XML'en ser ut:
<Organisation>
	<OrganisationId>243</OrganisationId>
	<Name>Notodden OL</Name>
	<ShortName>Notodden OL</ShortName>
	<MediaName>Notodden OL</MediaName>
	<OrganisationTypeId>3</OrganisationTypeId>
	<Country><CountryId value="578" />
		<Alpha3 value="NOR" />
		<Name languageId="en">Norway</Name>
		<Name languageId="sv">Norge</Name>
	</Country>
	<Address careOf="Torgrim Gjestrud" street=" Tinnegrendvegen 171" city="Notodden" zipCode="3683">
		<AddressType value="official" />
		<Country>
			<CountryId value="578" />
			<Alpha3 value="NOR" />
			<Name languageId="en">Norway</Name>
			<Name languageId="sv">Norge</Name>
		</Country>
	</Address>
	<Tele mobilePhoneNumber="91138168" mailAddress="torgrim.gjestrud@gmail.com">
		<TeleType value="official" />
	</Tele>
	<ParentOrganisation>
		<OrganisationId>19</OrganisationId>
	</ParentOrganisation>
	<OrganisationStatusId>1</OrganisationStatusId>
	<ModifyDate>
		<Date>2016-05-28</Date>
		<Clock>10:42:00</Clock>
	</ModifyDate>
</Organisation>
"""
    url = "https://eventor.orientering.no/api/organisations"
    headers = {
        "Accept": "application/xml",
        "ApiKey": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # kaster HTTPError ved 4xx/5xx
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 403:
            logging.warning("API-nøkkel er ugyldig (403)")
            raise ValueError("Ugyldig API-nøkkel: tilgang nektet (403). Sjekk API-nøkkel i Eventor") from e
        else:
            logging.error(f"HTTP-feil: {e}")
            raise RuntimeError(f"API-feil: {e.response.status_code if e.response else 'ukjent'}") from e

    root = ET.fromstring(response.content)

    organisasjoner = []

    for org in root.findall(".//Organisation"):
        org_id = org.findtext("OrganisationId")
        name = org.findtext("Name")
        short_name = org.findtext("ShortName")
        org_level = org.findtext("OrganisationTypeId")

        country_alpha3_elt = org.find(".//Country/Alpha3")
        country_code = country_alpha3_elt.attrib["value"] if country_alpha3_elt is not None else None

        # Filtrering
        if org_level != "3":
            continue

        if filter_on_code and country_code != filter_on_code:
            continue

        # Address
        adr_elem = org.find("Address")
        adr_care_of = adr_elem.attrib["careOf"] if adr_elem is not None and "careOf" in adr_elem.attrib else None
        adr_street = adr_elem.attrib["street"] if adr_elem is not None and "street" in adr_elem.attrib else None
        adr_city = adr_elem.attrib["city"] if adr_elem is not None and "city" in adr_elem.attrib else None
        adr_zip_code = adr_elem.attrib["zipCode"] if adr_elem is not None and "zipCode" in adr_elem.attrib else None
        adr_country_elt = org.find(".//Address/Country/Name[@languageId='sv']")
        adr_country = adr_country_elt.text if adr_country_elt is not None else None

        # Contact info
        tele = org.find("Tele")
        mail_adr = tele.attrib["mailAddress"] if tele is not None and "mailAddress" in tele.attrib else None
        phone_number = tele.attrib["phoneNumber"] if tele is not None and "phoneNumber" in tele.attrib else None
        mobile_phone_number = tele.attrib["mobilePhoneNumber"] if tele is not None and "mobilePhoneNumber" in tele.attrib else None

        modify_date_elt = org.find(".//ModifyDate/Date")
        modify_date = modify_date_elt.text if modify_date_elt is not None else None
        modify_clock_elt = org.find(".//ModifyDate/Clock")
        modify_clock = modify_clock_elt.text if modify_clock_elt is not None else None
        modified = modify_date if modify_date is not None else None
        if modified:
            modified = modified + " " + modify_clock if modify_clock is not None else modified

#        logging.debug(ET.tostring(org, encoding="unicode"))

        organisasjoner.append({
            "org_id": org_id,
            "name": name,
            "short_name": short_name,
            "country_code": country_code,
            "adr_care_of": adr_care_of,
            "adr_street": adr_street,
            "adr_city": adr_city,
            "adr_zip_code": adr_zip_code,
            "adr_country": adr_country,
            "mail_adr": mail_adr,
            "phone_number": phone_number,
            "mobile_phone_number": mobile_phone_number,
            "modified": modified,
        })

    return organisasjoner
