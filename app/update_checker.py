import logging
import requests

GITHUB_API_URL = "https://api.github.com/repos/RekaaSv/BrikkesysTillegg/releases/latest"

def check_latest_version(current_version: str):
    """
    Sjekker GitHub for siste release.
    Returnerer (is_newer, latest_version, download_url)
    """
    logging.info("check_latest_version")

    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        data = response.json()

        latest_version = data.get("tag_name", "").lstrip("v")

        def version_tuple(v):
            return tuple(map(int, v.split(".")))

        # Finn riktig ZIP-asset
        assets = data.get("assets", [])
        download_url = None

        for asset in assets:
            name = asset.get("name", "")
            if name.lower().endswith(".zip"):
                download_url = asset.get("browser_download_url")
                break

        if not download_url:
            logging.error("Fant ingen ZIP-asset i GitHub release")
            return False, latest_version, None

        # Sammenlign versjoner
        if latest_version and version_tuple(latest_version) > version_tuple(current_version):
            return True, latest_version, download_url

        return False, latest_version, download_url

    except Exception as e:
        logging.error("Feil i check_latest_version: %s", e)
        return False, None, None
