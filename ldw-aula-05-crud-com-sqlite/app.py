# Importando o Flask
from flask import Flask, render_template
# Importando o controller (routes.py)
from controllers import routes
# Importando os Models
from models.database import db
# Importando a biblioteca para manipulação do S.O.
import os

# Criando uma instância do Flask
app = Flask(__name__, template_folder="views") # __name__ representa o nome do arquivo que está sendo executado
routes.init_app(app)

# Extraindo o Diretório Absoluto
dir = os.path.abspath(os.path.dirname(__file__))

# Criando  o arquivo do banco
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://root@localhost:3306/"

# Se for executado diretamente pelo interpretador
if __name__ == "__main__":
    # Enviando o Flask para o SQLAlchemy
    db.init_app(app=app)
    # Verificando no inicio da aplicação se o banco já existe. Se não, ele cria.
    with app.test_request_context():
        db.create_all()
        
    # Iniciando o servidor
    app.run(host="localhost", port=5000, debug=True)