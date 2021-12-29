from flask import Flask

import cx_Oracle
def getConnection() :
    connection = cx_Oracle.connection("sys/sys@localhost:1512/xe");
    return connection


app = Flask(__name__)

if __name__ == "__main__":
    app.run(port=5001)