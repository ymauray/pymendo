import urllib2
import json
import datetime
import mysql.connector


connection_config = {
    'user': 'pymendo',
    'password': 'pymendo',
    'host': '127.0.0.1',
    'database': 'pymendo',
    'raise_on_warnings': True
}
cnx = mysql.connector.connect(**connection_config)

now = datetime.datetime.now()
isocalendar = now.isocalendar()
chronokey = "%04d-%02d" % (isocalendar[0], isocalendar[1])


def main():
    year = now.year
    try:
        while fetch_data_for(year):
            year -= 1
    except RuntimeError as re:
        print re
    cnx.close()


def fetch_data_for(year):
    page = 0
    datebetween = "%d-01-01_%d-12-31" % (year, year)
    url = 'https://api.jamendo.com/v3.0/tracks/?client_id=4e3f05b4&format=json&order=releasedate_desc' \
          '&include=licenses+musicinfo+stats&datebetween=%s&limit=200' % datebetween
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
            if page == 0:
                return False
            else:
                return True

        cursor = cnx.cursor()
        results = data['results']
        for result in results:
            track_data = {
                'id': int(result['id']),
                'track_name': result['name'],
                'artist_id': int(result['artist_id']),
                'artist_name': result['artist_name'],
                'album_name': result['album_name'],
                'album_id': int(result['album_id']),
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

            sql = ('INSERT INTO tracks(id, track_name, artist_id, artist_name, album_name, album_id, releasedate, '
                   'album_image, audio, audiodownload, shorturl, shareurl, image, vocalinstrumental, lang, ccnc, '
                   'ccnd, ccsa) VALUES (%(id)s, %(track_name)s, %(artist_id)s, %(artist_name)s, %(album_name)s, '
                   '%(album_id)s, %(releasedate)s, %(album_image)s, %(audio)s, %(audiodownload)s, %(shorturl)s, '
                   '%(shareurl)s, %(image)s, %(vocalinstrumental)s, %(lang)s, %(ccnc)s, %(ccnd)s, %(ccsa)s) ON '
                   'DUPLICATE KEY UPDATE track_name = %(track_name)s, artist_id = %(artist_id)s, '
                   'artist_name = %(artist_name)s, album_name = %(album_name)s, album_id = %(album_id)s, '
                   'releasedate = %(releasedate)s, album_image = %(album_image)s, audio = %(audio)s, '
                   'audiodownload = %(audiodownload)s, shorturl = %(shorturl)s, shareurl = %(shareurl)s, '
                   'image = %(image)s, vocalinstrumental = %(vocalinstrumental)s, lang = %(lang)s, ccnc = %(ccnc)s, '
                   'ccnd = %(ccnd)s, ccsa = %(ccsa)s')
            print '%s - %s - %s' % (track_data['releasedate'], track_data['artist_name'], track_data['track_name'])
            cursor.execute(sql, track_data)

            genres = []
            for tag in result['musicinfo']['tags']['genres']:
                genres.append(tag)
            instruments = []
            for tag in result['musicinfo']['tags']['instruments']:
                instruments.append(tag)
            vartags = []
            for tag in result['musicinfo']['tags']['vartags']:
                vartags.append(tag)
            cnx.commit()
        cursor.close()
        page += 1
