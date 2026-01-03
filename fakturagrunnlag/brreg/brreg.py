import logging

import requests

def get_orgnummer(clubname: str) -> str:
#    logging.info(f"brreg.get_orgnummer({clubname})")
    # Bygg opp søke-URL mot Enhetsregisteret API
    url = "https://data.brreg.no/enhetsregisteret/api/enheter"
    params = {"navn": clubname}

    # Gjør API-kall
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    # Sjekk om vi fikk treff
    if "_embedded" in data and "enheter" in data["_embedded"]:
        enheter = data["_embedded"]["enheter"]
        if len(enheter) > 0:
            # Ta første treff
            return enheter[0].get("organisasjonsnummer")
    return ''

