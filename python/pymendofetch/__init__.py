import datetime
import json
import sys
import urllib2

import db

now = datetime.datetime.now()
isocalendar = now.isocalendar()
weekly_key = "%04d-%02d" % (isocalendar[0], isocalendar[1])
quiet = False
cursor = db.cnx.cursor()


def main():
    global quiet, cursor
    if len(sys.argv) > 1 and sys.argv[1] == "-q":
        quiet = True
    try:
        fetch_tracks()
    except RuntimeError as re:
        print re
    cursor.close()
    db.cnx.close()


def safe_int(val):
    return int(val) if val != '' else 0


def track_keys(l):
    for e in l:
        if e != "musicinfo" and e != "licenses" and e != "stats":
            yield e


def musicinfo_keys(l):
    for e in l:
        if e != "tags":
            yield e


def licenses_keys(l):
    for e in l:
        if e == "licenses":
            yield e


def prepare(table, d, filter_keys):
    colonnes = []
    values = []
    updates = []
    o = {}
    keys = filter_keys(d) if filter_keys is not None else d.keys()
    for key in keys:
        colonnes.append(key)
        values.append("%%(%s)s" % key)
        updates.append("%s = %%(%s)s" % (key, key))
        o[key] = d[key] if d[key] != 'true' and d[key] != 'false' else True if d[key] == 'true' else False

    sql = "INSERT INTO %s(%s) VALUES (%s) " \
          "ON DUPLICATE KEY UPDATE date_updated = CURRENT_TIMESTAMP(), %s" \
          % (table, ", ".join(colonnes), ", ".join(values), ", ".join(updates))

    return o, sql


def fetch_tracks():
    global cursor, now
    page = 0
    datebetween = "%04d-%02d-%02d_%04d-%02d-%02d" % (now.year - 1, now.month, now.day, now.year, now.month, now.day)
    url = ('https://api.jamendo.com/v3.0/tracks/?client_id=4e3f05b4&format=json&type=single+albumtrack&order='
           'releasedate_desc&include=licenses+musicinfo+stats&datebetween=%s&limit=200') % datebetween
    while True:
        offseturl = "%s&offset=%d" % (url, 200 * page)
        response = urllib2.urlopen(offseturl)
        data = json.load(response)
        headers = data['headers']
        status = headers['status']
        if status != 'success':
            raise RuntimeError('status : %s' % status)
        code = headers['code']
        if code != 0:
            raise RuntimeError('code : %d' % code)
        results_count = headers['results_count']
        if results_count == 0:
            return

        results = data['results']
        for result in results:
            (o, sql) = prepare("fetch_track", result, track_keys)
            if o['album_id'] == '':
                o['album_id'] = '0'
            cursor.execute(sql, o)

            track_id = o['id']

            result['musicinfo']['track_id'] = track_id
            (o, sql) = prepare("fetch_musicinfo", result['musicinfo'], musicinfo_keys)
            cursor.execute(sql, o)

            result['licenses']['track_id'] = track_id
            (o, sql) = prepare("fetch_licenses", result['licenses'], None)
            cursor.execute(sql, o)

            result['stats']['track_id'] = track_id
            result['stats']['date'] = now.strftime('%Y-%m-%d')
            (o, sql) = prepare("fetch_stats", result['stats'], None)
            cursor.execute(sql, o)

            for tag in result['musicinfo']['tags']['genres']:
                (o, sql) = prepare("fetch_tags", {
                    'track_id': track_id,
                    'tag_type': 'genre',
                    'tag_value': tag
                }, None)
                cursor.execute(sql, o)

            for tag in result['musicinfo']['tags']['instruments']:
                (o, sql) = prepare("fetch_tags", {
                    'track_id': track_id,
                    'tag_type': 'instrument',
                    'tag_value': tag
                }, None)
                cursor.execute(sql, o)

            for tag in result['musicinfo']['tags']['vartags']:
                (o, sql) = prepare("fetch_tags", {
                    'track_id': track_id,
                    'tag_type': 'vartag',
                    'tag_value': tag
                }, None)
                cursor.execute(sql, o)

        break
    db.cnx.commit()
#https://api.jamendo.com/v3.0/tracks/?client_id=c4d49542&format=jsonpretty&type=single+albumtrack&include=licenses+musicinfo+stats&order=releasedate_desc&limit=200&datebetween=2016-08-24_2017-08-24