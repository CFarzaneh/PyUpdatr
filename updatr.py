from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from requests import get
from tqdm import tqdm
import plistlib
import os

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

if __name__ == "__main__":

	appsPath = '/Applications'

	apps = os.listdir(appsPath)
	apps = [x for x in apps if not x.startswith('.') and x.endswith('.app')]

	outdated = []
	print('Scanning applications...')
	for app in tqdm(apps):
		
		fp = open(appsPath+'/'+app+'/Contents/Info.plist', 'rb')
		pl = plistlib.load(fp)

		if 'com.apple' in pl['CFBundleIdentifier'] or 'TorGuard' in app:
			fp.close()
			continue

		appName = pl['CFBundleName']
		appName.replace(' ', '%20')
		installedVersion = pl['CFBundleShortVersionString']

		raw_html = simple_get('https://www.macupdate.com/find/mac/'+appName)

		html = BeautifulSoup(raw_html, 'html.parser')
		currentVersion = html.find('span',itemprop="version").text

		if installedVersion != currentVersion:
			outdated.append((appName, currentVersion, installedVersion))

		fp.close()

	print('\nThere are',len(outdated),'outdated applications installed!')
	for name,currentVersion,installedVersion in outdated:
		print(name)
		print('Current version:',currentVersion)
		print('Installed version:', installedVersion)
		print()