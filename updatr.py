from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from requests import get
from tqdm import tqdm
import plistlib
import os
import json
import re


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

        # if app != "1Password 7.app":
        # 	continue

        fp = open(appsPath+'/'+app+'/Contents/Info.plist', 'rb')
        pl = plistlib.load(fp)

        try:
            appId = pl['CFBundleIdentifier']
            appName = pl['CFBundleName']
            installedVersion = pl['CFBundleShortVersionString']
        except KeyError:
            fp.close()
            continue
        else:
            if 'com.apple' in appId:
                fp.close()
                continue

        appName.replace(' ', '%20')

        raw_html = simple_get(
            'https://www.macupdate.com/find/mac/context%3D'+appName)
        html = BeautifulSoup(raw_html, 'html.parser')
        urls = html.find_all(
            'a', attrs={"class": "ns_sp_app-results"}, href=True)
        found = False
        maxCheck = min(10, len(urls))
        for i in range(maxCheck):
            htmlAgain = simple_get(
                'https://www.macupdate.com'+urls[i]['href']).decode("utf-8")
            matches = re.findall(
                r'"bundle_identifiers":\[(.+?)\]', htmlAgain)[0]
            if len(matches) == 0:
                continue
            matches = matches.replace('"', '').split(',')
            if appId in matches:
                found = True
                html = BeautifulSoup(htmlAgain, 'html.parser')
                currentVersion = html.find(
                    'span', attrs={"class": "mu_app_header_version"}).contents[0]
                break

        if found and installedVersion != currentVersion:
            outdated.append((appName, currentVersion, installedVersion))

        fp.close()

    print('\nThere are', len(outdated), 'outdated applications installed!')
    for name, currentVersion, installedVersion in outdated:
        print(name)
        print('Current version:', currentVersion)
        print('Installed version:', installedVersion)
        print()
