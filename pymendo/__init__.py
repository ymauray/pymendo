import urllib2
import json


def main():
    dev_mode = True

    if dev_mode:
        pages = 1
    else:
        pages = 100

    page = 0
    while page < pages:
        if dev_mode:
            response = urllib2.urlopen('file:jamendo.json')
        else:
            url = 'https://api.jamendo.com/v3.0/tracks/?client_id=4e3f05b4&format=json&order=downloads_total_desc' \
                  '&include=licenses+musicinfo+stats&limit=200&offset=%d' % 200 * page
            response = urllib2.urlopen(url)
        page = page + 1
        data = json.load(response)
        headers = data['headers']
        status = headers['status']
        code = headers['code']
        if status != 'success':
            raise RuntimeError('status : %s' % status)
        if code != 0:
            raise RuntimeError('code : %d' % code)
        results_count = headers['results_count']
