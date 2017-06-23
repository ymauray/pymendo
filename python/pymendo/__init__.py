import datetime
import json
import sys
import urllib2

import db

now = datetime.datetime.now()
isocalendar = now.isocalendar()
weekly_key = "%04d-%02d" % (isocalendar[0], isocalendar[1])
quiet = False


def main():
    global quiet
    if sys.argv[1] == "-q":
        quiet = True
    try:
        fetch_data()
    except RuntimeError as re:
        print re
    db.cnx.close()


def fetch_data():
    page = 0
    datebetween = "%04d-%02d-%02d_%04d-%02d-%02s" % (now.year - 1, now.month, now.day, now.year, now.month, now.day)
    url = ('https://api.jamendo.com/v3.0/tracks/?client_id=4e3f05b4&format=json&type=single+albumtrack&order='
           'releasedate_desc&include=licenses+musicinfo+stats&datebetween=%s&limit=200') % datebetween
    while True:
        response = urllib2.urlopen("%s&offset=%d" % (url, 200 * page))
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

        cursor = db.cnx.cursor()
        results = data['results']
        for result in results:
            track_data = {
                'id': int(result['id']),
                'now': now,
                'track_name': result['name'],
                'artist_id': int(result['artist_id']),
                'artist_name': result['artist_name'],
                'album_name': result['album_name'],
                'album_id': int(result['album_id']) if result['album_id'] != '' else 0,
                'releasedate': datetime.datetime.strptime(result['releasedate'], '%Y-%m-%d'),
                'album_image': result['album_image'],
                'audio': result['audio'],
                'audiodownload': result['audiodownload'],
                'shorturl': result['shorturl'],
                'shareurl': result['shareurl'],
                'image': result['image'],
                'vocalinstrumental': result['musicinfo']['vocalinstrumental'],
                'lang': result['musicinfo']['lang'],
                'ccnc': result['licenses']['ccnc'] == "true",
                'ccnd': result['licenses']['ccnd'] == "true",
                'ccsa': result['licenses']['ccsa'] == "true",
            }

            sql = ('INSERT INTO tracks(id, date_created, date_updated, track_name, artist_id, artist_name, '
                   'album_name, album_id, releasedate, album_image, audio, audiodownload, shorturl, shareurl, image, '
                   'vocalinstrumental, lang, ccnc, ccnd, ccsa) VALUES (%(id)s, %(now)s, %(now)s, %(track_name)s, '
                   '%(artist_id)s, %(artist_name)s, %(album_name)s, %(album_id)s, %(releasedate)s, %(album_image)s, '
                   '%(audio)s, %(audiodownload)s, %(shorturl)s, %(shareurl)s, %(image)s, %(vocalinstrumental)s, '
                   '%(lang)s, %(ccnc)s, %(ccnd)s, %(ccsa)s) ON DUPLICATE KEY UPDATE date_updated = %(now)s, '
                   'track_name = %(track_name)s, artist_id = %(artist_id)s, artist_name = %(artist_name)s, '
                   'album_name = %(album_name)s, album_id = %(album_id)s, releasedate = %(releasedate)s, '
                   'album_image = %(album_image)s, audio = %(audio)s, audiodownload = %(audiodownload)s, '
                   'shorturl = %(shorturl)s, shareurl = %(shareurl)s, image = %(image)s, '
                   'vocalinstrumental = %(vocalinstrumental)s, lang = %(lang)s, ccnc = %(ccnc)s, ccnd = %(ccnd)s, '
                   'ccsa = %(ccsa)s')
            if not quiet:
                print '%s - %s - %s' % (track_data['releasedate'], track_data['artist_name'], track_data['track_name'])
            cursor.execute(sql, track_data)

            insert_tags('genres', track_data['id'], result['musicinfo']['tags']['genres'])
            insert_tags('instruments', track_data['id'], result['musicinfo']['tags']['instruments'])
            insert_tags('vartags', track_data['id'], result['musicinfo']['tags']['vartags'])

            downloads = int(result['stats']['rate_downloads_total'])
            listens = int(result['stats']['rate_listened_total'])
            playlists = int(result['stats']['playlisted'])
            favorites = int(result['stats']['favorited'])
            likes = int(result['stats']['likes'])
            dislikes = int(result['stats']['dislikes'])
            score = 2 * downloads + listens + playlists + favorites + 2 * likes - 2 * dislikes
            stats_data = {
                'track_id': track_data['id'],
                'now': now,
                'date': now.date(),
                'weekly_key': weekly_key,
                'downloads': downloads,
                'listens': listens,
                'playlists': playlists,
                'favorites': favorites,
                'likes': likes,
                'dislikes': dislikes,
                'score': score,
            }
            sql = ('insert into stats(track_id, date_created, date_updated, date, weekly_key, downloads, listens, '
                   'playlists, favorites, likes, dislikes, score) values(%(track_id)s, %(now)s, %(now)s, %(date)s, '
                   '%(weekly_key)s, %(downloads)s, %(listens)s, %(playlists)s, %(favorites)s, %(likes)s, '
                   '%(dislikes)s, %(score)s) ON DUPLICATE KEY UPDATE date_updated = %(now)s, '
                   'downloads = %(downloads)s, listens = %(listens)s, playlists = %(playlists)s, '
                   'favorites = %(favorites)s, likes = %(likes)s, dislikes = %(dislikes)s, score = %(score)s')
            cursor.execute(sql, stats_data)
            db.cnx.commit()
        cursor.close()
        page += 1


def insert_tags(tag_type, track_id, tags):
    cursor = db.cnx.cursor()
    tag_data = {
        'track_id': track_id,
        'tag_type': tag_type,
        'tag_value': ''
    }

    sql = ('delete from tags where track_id = %(track_id)s and tag_type = %(tag_type)s')
    cursor.execute(sql, tag_data)

    sql = ('insert into tags(track_id, tag_type, tag_value) values(%(track_id)s, %(tag_type)s, %(tag_value)s)')
    for tag in tags:
        tag_data.update({'tag_value': tag})
        cursor.execute(sql, tag_data)
    cursor.close()
