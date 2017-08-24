import mysql.connector

connection_config = {
    'user': 'pymendo',
    'password': 'pymendo',
    'host': '127.0.0.1',
    'database': 'pymendo',
    'raise_on_warnings': True
}
cnx = mysql.connector.connect(**connection_config)

