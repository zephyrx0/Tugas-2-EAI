import datetime
import jwt
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import datetime

app = Flask(__name__)

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'festival'
mysql = MySQL(app)

# Secret key for token authentication
app.config['SECRET_KEY'] = 'token'


# Function to generate authentication token
def generate_token():
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {'exp': expiration}
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


@app.route('/event', methods=['GET', 'POST', 'PUT', 'DELETE'])
def event():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM event")

        data = [
            {cursor.description[i][0]: (value.strftime('%d-%b-%Y')
                                         if cursor.description[i][0] == 'tanggal_event' and value else value)
             for i, value in enumerate(row)}
            for row in cursor.fetchall()
        ]

        cursor.close()

        return jsonify({"status": "success", "data": data, "message": "Data berhasil ditemukan", "timestamp": timestamp}), 200

    elif request.method == 'POST':
        data = request.get_json()

        cursor = mysql.connection.cursor()
        sql = ("INSERT INTO event (nama_event, tanggal_event, harga_event) VALUES (%s, %s, %s)")
        val = (data['nama_event'], data['tanggal_event'], data['harga_event'])
        cursor.execute(sql, val)

        mysql.connection.commit()
        cursor.close()

        return jsonify({"status": "success", "message": "Data berhasil ditambahkan", "timestamp": timestamp}), 201

    elif request.method == 'PUT':
        if 'id' in request.args:
            data = request.get_json()

            cursor = mysql.connection.cursor()
            sql = ("UPDATE event SET nama_event = %s, tanggal_event = %s, harga_event = %s WHERE id_event = %s")
            val = (data['nama_event'], data['tanggal_event'], data['harga_event'], request.args['id'])
            cursor.execute(sql, val)

            mysql.connection.commit()
            cursor.close()

            return jsonify({"status": "success", "message": "Data berhasil diperbarui", "timestamp": timestamp}), 200

    elif request.method == 'DELETE':
        if 'id' in request.args:
            cursor = mysql.connection.cursor()
            sql = ("DELETE FROM event WHERE id_event = %s ")
            val = (request.args['id'],)
            cursor.execute(sql, val)

            mysql.connection.commit()
            cursor.close()

            return jsonify({"status": "success", "message": "Data berhasil dihapus", "timestamp": timestamp}), 200


@app.route('/detailEvent')
def detail_event():
    cursor = mysql.connection.cursor()

    if 'id' in request.args:
        sql = "SELECT * FROM event WHERE id_event = %s"
        val = (request.args['id'],)
    elif 'nama_event' in request.args:
        sql = "SELECT * FROM event WHERE nama_event LIKE %s"
        val = ("%" + request.args['nama_event'] + "%",)
    else:
        return jsonify({"error": "Parameter 'id' atau 'nama_event' diperlukan"}), 400

    cursor.execute(sql, val)

    data = [
        {cursor.description[i][0]: (value.strftime('%d-%b-%Y')
                                     if cursor.description[i][0] == 'tanggal_event' and value else value)
         for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]

    cursor.close()

    return jsonify({"status": "success", "data": data, "message": "Data berhasil ditemukan"}), 200


@app.route('/auth')
def authenticate():
    token = generate_token()
    return jsonify({"token": token.decode('utf-8')}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
