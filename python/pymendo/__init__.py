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
        update_tables()
    except RuntimeError as re:
        print re
    db.cnx.close()


def fetch_data():
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


def update_tables():
    cursor = db.cnx.cursor()
    sql = ('INSERT INTO weekly_sum SELECT s.track_id, s.weekly_key, SUM(s.score) score FROM stats s WHERE '
           'weekly_key = DATE_FORMAT(NOW(), "%x-%v") GROUP BY s.track_id, s.weekly_key ON DUPLICATE KEY UPDATE '
           'score = VALUES(score)')
    cursor.execute(sql)
    sql = ('INSERT INTO weekly_score SELECT ws0.weekly_key, @monday:=STR_TO_DATE(CONCAT(ws0.weekly_key, "-1"), '
           '"%x-%v-%w") monday, ws0.track_id, @score0:=ws0.score score0, @score1:=IFNULL(ws1.score, 0) score1, '
           '@score2:=IFNULL(ws2.score, 0) score2, @score3:=IFNULL(ws3.score, 0) score3, '
           '4 * @score0 + 3 * @score1 + 2 * @score2 + @score3 weekly_score FROM weekly_sum ws0 LEFT JOIN '
           'weekly_sum ws1 on ws0.track_id = ws1.track_id AND DATE_FORMAT(DATE_ADD(@monday, INTERVAL -1 WEEK), '
           '"%x-%v") = ws1.weekly_key LEFT JOIN weekly_sum ws2 on ws0.track_id = ws2.track_id AND '
           'DATE_FORMAT(DATE_ADD(@monday, INTERVAL -2 WEEK), "%x-%v") = ws2.weekly_key LEFT JOIN weekly_sum ws3 '
           'ON ws0.track_id = ws3.track_id AND DATE_FORMAT(DATE_ADD(@monday, INTERVAL -3 WEEK), "%x-%v") = '
           'ws3.weekly_key WHERE ws0.weekly_key = DATE_FORMAT(NOW(), "%x-%v") ORDER BY weekly_key DESC, '
           'weekly_score DESC ON DUPLICATE KEY UPDATE score0 = VALUES(score0), score1 = VALUES(score1), '
           'score2 = VALUES(score2), score3 = VALUES(score3), weekly_score = VALUES(weekly_score)')
    cursor.execute(sql)
    sql = ('INSERT INTO weekly_charts SELECT ws.weekly_key, @row:=@row+1 position, t.artist_name, t.track_name, '
           '(CASE t.album_id WHEN 0 THEN CONCAT(t.track_name, " (Single)") ELSE t.album_name END) album_name, '
           'ws.track_id, ws.weekly_score FROM (SELECT @row := 0) r, weekly_score ws LEFT JOIN tracks t ON '
           't.id = ws.track_id WHERE ws.weekly_key = DATE_FORMAT(NOW(), "%x-%v") ORDER BY ws.weekly_score DESC '
           'ON DUPLICATE KEY UPDATE artist_name = VALUES(artist_name), track_name = VALUES(track_name), '
           'album_name = VALUES(album_name), track_id = VALUES(track_id), weekly_score = VALUES(weekly_score)')
    cursor.execute(sql)
    sql = ('INSERT INTO weekly_progression SELECT wc0.weekly_key, wc0.track_id, wc0.position position0, '
           'wc1.position position1, wc1.position - wc0.position progression FROM weekly_charts wc0 '
           'LEFT JOIN weekly_charts wc1 ON wc1.track_id = wc0.track_id AND wc1.weekly_key = '
           'DATE_FORMAT(DATE_ADD(STR_TO_DATE(CONCAT(wc0.weekly_key, "-1"), "%x-%v-%w"), INTERVAL -1 WEEK), '
           '"%x-%v") WHERE wc0.weekly_key = DATE_FORMAT(NOW(), "%x-%v") ORDER BY wc0.position ASC '
           'ON DUPLICATE KEY UPDATE position0 = VALUES(position0), position1 = VALUES(position0), '
           'progression = VALUES(progression)')
    cursor.execute(sql)
    sql = ('INSERT INTO quick_album SELECT DISTINCT (CASE t.album_id WHEN 0 THEN t.id ELSE t.album_id END) AS id, '
           '(CASE t.album_id WHEN 0 THEN t.track_name ELSE t.album_name END) AS name, t.artist_id, t.artist_name, '
           '(CASE t.album_id WHEN 0 THEN 1 ELSE 0 END) single, t.releasedate, t.image FROM tracks t ORDER BY '
           't.releasedate DESC, single ASC, id DESC ON DUPLICATE KEY UPDATE image = VALUES(image);')
    cursor.execute(sql)
    db.cnx.commit()
    cursor.close()


def insert_tags(tag_type, track_id, tags):
    cursor = db.cnx.cursor()
    tag_data = {
        'track_id': track_id,
        'tag_type': tag_type,
        'tag_value': ''
    }

    sql = 'delete from tags where track_id = %(track_id)s and tag_type = %(tag_type)s'
    cursor.execute(sql, tag_data)

    sql = 'insert into tags(track_id, tag_type, tag_value) values(%(track_id)s, %(tag_type)s, %(tag_value)s)'
    for tag in tags:
        tag_data.update({'tag_value': tag})
        cursor.execute(sql, tag_data)
    cursor.close()
