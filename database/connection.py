import mysql.connector

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="moy123",
        database="admon_project",
        use_pure=True
    )

    return conexion
