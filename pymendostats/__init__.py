import pymendo.db
import datetime


def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)


def main():
    cursor = pymendo.db.cnx.cursor()
    sql = ("""update stats set score = listens + 2 * downloads + playlists + favorites + 2 * likes - 2 * dislikes""")
    cursor.execute(sql)
    pymendo.db.cnx.commit()
    sql = ("""select * from stats order by track_id desc, date desc """)
    cursor.execute(sql)
    for row in cursor:
        print row
        date = row[1]
        print date
