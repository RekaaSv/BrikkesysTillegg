import requests

GITHUB_API_URL = "https://api.github.com/repos/RekaaSv/BrikkesysTillegg/releases/latest"
DOWNLOAD_URL = "https://github.com/RekaaSv/BrikkesysTillegg/releases/latest"

def check_latest_version(current_version: str):
    """
    Sjekker GitHub for siste release.
    current_version: f.eks. "1.0.0"
    Returnerer (is_newer, latest_version, download_url)
    """
    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        data = response.json()

        latest_version = data.get("tag_name", "").lstrip("v")

        def version_tuple(v):
            return tuple(map(int, v.split(".")))

        if latest_version and version_tuple(latest_version) > version_tuple(current_version):
            return True, latest_version, DOWNLOAD_URL

        return False, latest_version, DOWNLOAD_URL

    except Exception:
        return False, None, DOWNLOAD_URL