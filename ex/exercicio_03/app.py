from flask import Flask, render_template
from controllers import routes
from models.database import db
import pymysql

app = Flask(__name__, template_folder="views")
routes.init_app(app)

# Configuração do banco de dados
DB_NAME = "musique"
app.config["DATABASE_NAME"] = DB_NAME
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root:@localhost/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if __name__ == "__main__":
    # Cria o banco de dados se não existir
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print("Banco de dados criado ou já existente!")
    except Exception as e:
        print(f"Erro ao criar o banco de dados: {e}")
    finally:
        connection.close()

    # Inicializa e cria as tabelas
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Executa o servidor Flask
    app.run(host="0.0.0.0", port=4000, debug=True)
