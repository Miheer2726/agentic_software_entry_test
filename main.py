
import requests
from datetime import datetime


def check_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    dependencies_checked = len(lines)
    packages_not_found = 0
    versions_not_found = 0

    oldest_date = None
    oldest_package = None

    for line in lines:
        name, version = line.split("==", 1)
        name = name.strip()
        version = version.strip()

        # Check if the package exists on PyPI
        package_url = f"https://pypi.org/pypi/{name}/json"
        package_response = requests.get(package_url, timeout=15)

        if package_response.status_code == 404:
            packages_not_found += 1
            continue

        package_response.raise_for_status()

        # Check if the pinned version exists
        version_url = f"https://pypi.org/pypi/{name}/{version}/json"
        version_response = requests.get(version_url, timeout=15)

        if version_response.status_code == 404:
            versions_not_found += 1
            continue

        version_response.raise_for_status()

        # Get the first file's upload timestamp
        data = version_response.json()
        files = data.get("urls", [])

        if not files:
            continue

        upload_time = files[0]["upload_time"]
        release_date = datetime.fromisoformat(upload_time)

        # Find the oldest valid pinned release
        if oldest_date is None or release_date < oldest_date:
            oldest_date = release_date
            oldest_package = f"{name}=={version}"

    # Print all four required outputs
    print(f"Dependencies checked: {dependencies_checked}")
    print(f"Packages not on PyPI: {packages_not_found}")
    print(f"Versions not on PyPI: {versions_not_found}")

    if oldest_package is not None:
        print(
            f"Oldest pinned release: "
            f"{oldest_package} ({oldest_date.year})"
        )
    else:
        print("Oldest pinned release: None")


if __name__ == "__main__":
    check_requirements()
