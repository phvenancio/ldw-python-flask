# Importando o Flask
from flask import Flask, render_template
# Importando o controller (routes.py)
from controllers import routes

# Criando uma instância do Flask
app = Flask(__name__, template_folder="views") # __name__ representa o nome do arquivo que está sendo executado
routes.init_app(app)
# Se for executado diretamente pelo interpretador
if __name__ == "__main__":
    # Iniciando o servidor
    app.run(host="localhost", port=5000, debug=True) 
    