from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Classe responsável por criar a entidade "Musics" com seus atributos.
class Musics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    album = db.Column(db.String(150))
    release_year = db.Column(db.Integer)

    artist = db.relationship('Artists', backref=db.backref('musics', lazy=True))

    def __init__(self, title, artist_id, album, release_year):
        self.title = title
        self.artist_id = artist_id
        self.album = album
        self.release_year = release_year

# Classe responsável por criar a entidade "Artists" com seus atributos.
class Artists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    birth_year = db.Column(db.Integer)
    nacionality = db.Column(db.String(150))
    
    def __init__(self, name, birth_year, nacionality):
        self.name = name
        self.birth_year = birth_year
        self.nacionality = nacionality
