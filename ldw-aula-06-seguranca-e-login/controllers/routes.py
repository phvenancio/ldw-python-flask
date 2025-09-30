from flask import render_template, request, url_for, redirect, flash, session
from models.database import db, Game, Console, Usuario
from werkzeug.security import generate_password_hash, check_password_hash
import urllib
import json

# Lista de jogadores
jogadores = ['Jogador 1', 'Jogador 2', 'Jogador 3',
             'Jogador 4', 'Jogador 5', 'Jogador 6', 'Jogador 7']
# Lista de jogos
gamelist = [{'Título': 'CS-GO', 'Ano': 2012, 'Categoria': 'FPS Online'}]


def init_app(app):
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/games', methods=['GET', 'POST'])
    def games():
        game = gamelist[0]

        if request.method == 'POST':
            if request.form.get('jogador'):
                jogadores.append(request.form.get('jogador'))
                return redirect(url_for('games'))
        return render_template('games.html',
                               game=game,
                               jogadores=jogadores)

    @app.route('/cadgames', methods=['GET', 'POST'])
    def cadgames():
        if request.method == 'POST':
            if request.form.get('titulo') and request.form.get('ano') and request.form.get('categoria'):
                gamelist.append({'Título': request.form.get('titulo'), 'Ano': request.form.get(
                    'ano'), 'Categoria': request.form.get('categoria')})
                return redirect(url_for('cadgames'))

        return render_template('cadgames.html',
                               gamelist=gamelist)

    # CRUD GAMES - LISTAGEM, CADASTRO E EXCLUSÃO
    @app.route('/games/estoque', methods=['GET', 'POST'])
    @app.route('/games/estoque/delete/<int:id>')
    def gamesEstoque(id=None):
        if id:
            game = Game.query.get(id)
            # Deleta o jogo cadastro pela ID
            db.session.delete(game)
            db.session.commit()
            return redirect(url_for('gamesEstoque'))
        # Cadastra um novo jogo
        if request.method == 'POST':
            newgame = Game(request.form['titulo'], request.form['ano'], request.form['categoria'],
                           request.form['preco'], request.form['quantidade'], request.form['console'])
            db.session.add(newgame)
            db.session.commit()
            return redirect(url_for('gamesEstoque'))
        else:
            # Captura o valor de 'page' que foi passado pelo método GET
            # Define como padrão o valor 1 e o tipo inteiro
            page = request.args.get('page', 1, type=int)
            # Valor padrão de registros por página (definimos 3)
            per_page = 3
            # Faz um SELECT no banco a partir da pagina informada (page)
            # Filtrando os registro de 3 em 3 (per_page)
            games_page = Game.query.paginate(page=page, per_page=per_page)
            
            consoles = Console.query.all()

            return render_template('gamesestoque.html', gamesestoque=games_page, consoles=consoles)

    # CRUD GAMES - EDIÇÃO
    @app.route('/games/edit/<int:id>', methods=['GET', 'POST'])
    def gameEdit(id):
        g = Game.query.get(id)
        # Edita o jogo com as informações do formulário
        if request.method == 'POST':
            g.titulo = request.form['titulo']
            g.ano = request.form['ano']
            g.categoria = request.form['categoria']
            g.preco = request.form['preco']
            g.quantidade = request.form['quantidade']
            g.console_id = request.form['console']
            db.session.commit()
            return redirect(url_for('gamesEstoque'))
        consoles = Console.query.all()
        return render_template('editgame.html', g=g, consoles=consoles)

    # CRUD CONSOLES - LISTAGEM, CADASTRO E EXCLUSÃO
    @app.route('/consoles/estoque', methods=['GET', 'POST'])
    @app.route('/consoles/estoque/delete/<int:id>')
    def consolesEstoque(id=None):
        if id:
            console = Console.query.get(id)
            # Deleta o console cadastro pela ID
            db.session.delete(console)
            db.session.commit()
            return redirect(url_for('consolesEstoque'))
        # Cadastra um novo console
        if request.method == 'POST':
            newconsole = Console(
                request.form['nome'], request.form['fabricante'], request.form['ano_lancamento'])
            db.session.add(newconsole)
            db.session.commit()
            return redirect(url_for('consolesEstoque'))
        else:
            # Captura o valor de 'page' que foi passado pelo método GET
            # Define como padrão o valor 1 e o tipo inteiro
            page = request.args.get('page', 1, type=int)
            # Valor padrão de registros por página (definimos 3)
            per_page = 3
            # Faz um SELECT no banco a partir da pagina informada (page)
            # Filtrando os registro de 3 em 3 (per_page)
            consoles_page = Console.query.paginate(
                page=page, per_page=per_page)
            return render_template('consolesestoque.html', consolesestoque=consoles_page)

    # CRUD CONSOLES - EDIÇÃO
    @app.route('/consoles/edit/<int:id>', methods=['GET', 'POST'])
    def consoleEdit(id):
        console = Console.query.get(id)
        # Edita o console com as informações do formulário
        if request.method == 'POST':
            console.nome = request.form['nome']
            console.fabricante = request.form['fabricante']
            console.ano_lancamento = request.form['ano_lancamento']
            db.session.commit()
            return redirect(url_for('consolesEstoque'))
        return render_template('editconsole.html', console=console)

    @app.route('/apigames', methods=['GET', 'POST'])
    @app.route('/apigames/<int:id>', methods=['GET', 'POST'])
    def apigames(id=None):
        url = 'https://www.freetogame.com/api/games'
        res = urllib.request.urlopen(url)
        data = res.read()
        gamesjson = json.loads(data)
        if id:
            ginfo = []
            for g in gamesjson:
                if g['id'] == id:
                    ginfo = g
                    break
            if ginfo:
                return render_template('gameinfo.html', ginfo=ginfo)
            else:
                return f'Game com a ID {id} não foi encontrado.'
        else:
            return render_template('apigames.html', gamesjson=gamesjson)


    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            # Buscando o usuário no banco
            user = Usuario.query.filter_by(username=username).first()
            # Usuario existe e a senha está correta
            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                session["username"] = user.username
                nickname = user.username.split("@")
                flash(f"Login realizado com sucesso! Bem-vindo {nickname[0]}!")
                return redirect(url_for("home"))
            # Usuário não existe ou senha incorreta
            else:
                flash("Falha no login. Verifique o nome de usuário e senha", "danger")
                return redirect(url_for("login"))
        return render_template("login.html")
    
    
    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.clear()
        return redirect(url_for("home"))
    
    
    @app.route("/caduser", methods=["GET", "POST"])
    def caduser():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            # Verificando se o usuario já existe
            user = Usuario.query.filter_by(username=username).first()
            if user:
                flash("Usuário já cadastrado, Faça o login!", "danger")
                return redirect(url_for("caduser"))
            # Se não existir
            else:
                hashed_password = generate_password_hash(password, method="scrypt")
                newUser = Usuario(username=username, password=hashed_password)
                db.session.add(newUser)
                db.session.commit(newUser)
                flash("Registro realixado com sucesso1 Você já pode fazer o login!", "success")
                return redirect(url_for("login"))
        return render_template("caduser.html")