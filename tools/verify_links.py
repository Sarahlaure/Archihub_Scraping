import requests
import sys

def test_connection(url):
    print(f"Testing connection to {url}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Success! Status: {response.status_code}")
            return True
        else:
            print(f"❌ Failed. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    sources = [
        "https://bensbites.substack.com/archive",
        "https://www.therundown.ai/archive"
    ]
    all_ok = True
    for source in sources:
        if not test_connection(source):
            all_ok = False
    
    if not all_ok:
        sys.exit(1)
