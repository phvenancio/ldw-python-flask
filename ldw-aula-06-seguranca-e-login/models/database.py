from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Classe responsável por criar a entidade "Console" com seus atributos.
class Console(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150))
    fabricante = db.Column(db.String(150))
    ano_lancamento = db.Column(db.Integer)

    def __init__(self, nome, fabricante, ano_lancamento):
        self.nome = nome
        self.fabricante = fabricante
        self.ano_lancamento = ano_lancamento

# Classe responsável por criar a entidade "Games" com seus atributos.
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150))
    ano = db.Column(db.Integer)
    categoria = db.Column(db.String(150))
    preco = db.Column(db.Float)
    quantidade = db.Column(db.Integer)
    console_id = db.Column(db.Integer, db.ForeignKey('console.id'))
    
    console = db.relationship('Console', backref=db.backref('game', lazy=True))
    

    def __init__(self, titulo, ano, categoria, preco, quantidade, console_id):
        self.titulo = titulo
        self.ano = ano
        self.categoria = categoria
        self.preco = preco
        self.quantidade = quantidade
        self.console_id = console_id

# Classe de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password