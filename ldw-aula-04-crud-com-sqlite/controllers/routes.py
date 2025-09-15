from flask import render_template, request, redirect, url_for
import urllib, json 
from models.database import Game, db
# Envia requisições a uma URL / Faz a conversão de dados json -> dicionário

def init_app(app): 
    # Lista em Python (array)
    players = ["Yan", "Ferrari", "Valéria", "Amanda"]
     
    gamelist = [{"Titulo":"CS 1.6", "Ano":1996, "Categoria":"FPS Online"}]
    # Definindo a rota principal da aplicação "/"
    @app.route("/")
    def home(): # Função que será executada ao acessar a rota
        return render_template("index.html")


    @app.route("/games", methods=["GET", "POST"])
    def games():
        title = "Tarisland"
        year = 2022
        category = "MMORPG"
        # Dicionário em Python (objeto)
        console = {"Nome" : "Playstation 5", "Fabricante" : "Sony", "Ano" : 2020}
        
        # Tratando uma requisição POST com request
        if request.method == "POST":   
            # Coletando o texto da input
            if request.form.get("player"):
                players.append(request.form.get("player"))
                return redirect(url_for("games"))
        
        return render_template("games.html", title=title, year=year, players=players, category=category, console=console)
    
    
    @app.route("/newgame", methods=["GET", "POST"])
    def newgame():
        if request.method == "POST":
            if request.form.get("title") and request.form.get("year") and request.form.category("category"):
                gamelist.append({"Titulo": request.form.get("title"), "Ano": request.form.get("year"), "Categoria": request.form.get("category")})
                return redirect(url_for("newgame"))
                
        return render_template("newgame.html", gamelist=gamelist)
    

    @app.route("/apigames", methods=["GET", "POST"])
    # Criando parametros para a rota
    @app.route("/apigames/<int:id>", methods=["GET", "POST"])
    def apigames(id=None):
        url = "https://www.freetogame.com/api/games"
        response = urllib.request.urlopen(url)
        data = response.read()
        gamesList = json.loads(data)
        # Verificando se o parametro foi enviado
        if id:
            gameInfo = []
            for game in gamesList:
                if game["id"] == id: # Comparando os IDs
                    gameInfo = game
                    break
            if gameInfo:
                return render_template("gameInfo.html", gameInfo=gameInfo)
            else:
                return f"Game com a ID {id} não foi encontrado."
        else:       
            return render_template("apigames.html", gamesList=gamesList)
    
    
    @app.route('/estoque', methods=["GET", "POST"])
    @app.route('/estoque/delete/<int:id>')
    def estoque(id=None):
        if id:
            game = Game.query.get(id)
            db.session.delete(game)
            db.session.commit()
            return redirect(url_for('estoque'))
        if request.method == 'POST':
            newGame = Game(request.form['title'], request.form['year'], request.form['category'], request.form['platform'], request.form['price'], request.form['quantity'])
            db.session.add(newGame)
            db.session.commit()
            return redirect(url_for('estoque'))
        gamesEstoque = Game.query.all()
        return render_template('estoque.html', gamesEstoque=gamesEstoque)
    
    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(id):
        game = Game.query.get(id)
        
        if request.method == 'POST':
            game.title = request.form['title']
            game.year = request.form['year']
            game.category = request.form['category']
            game.platform = request.form['platform']
            game.price = request.form['price']
            game.quantity = request.form['quantity']
            db.session.commit()
            return redirect(url_for('estoque'))
        return render_template('editgame.html', game=game)
        
    