from flask_sqlalchemy import SQLAlchemy

# Criando uma instância do SQLAlchemy
db = SQLAlchemy()

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    year = db.Column(db.Integer)
    category = db.Column(db.String(150))
    platform = db.Column(db.String(150))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    # Criando a chave estrangeira
    console_id = db.Column(db.Integer, db.ForeignKey("console.id"))
    # Definindo o relacionamento entre as tabelas
    console = db.relationship("Console", backref=db.backref("games", lazy=True))
    
    # Método construtor da classe
    def __init__(self, title, year, category, platform, price, quantity, console_id):
        self.title = title
        self.year = year
        self.category = category
        self.platform = platform
        self.price = price
        self.quantity = quantity
        self.console_id = console_id