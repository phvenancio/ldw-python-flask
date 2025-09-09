from flask import render_template, request, redirect, url_for

def init_app(app):
    dict_musics = []
    list_artists = []


    @app.route("/")
    def home():
        destaques = dict_musics[:3]
        return render_template("index.html", destaques=destaques, dict_musics=dict_musics)
    

    @app.route("/musics", methods=["GET", "POST"])
    def musics():
        if request.method == "POST":
            title = request.form.get("title")
            artist = request.form.get("artist")
            album = request.form.get("album")
            year = request.form.get("year")
            
            if all([title, artist, album, year]):
                dict_musics.append({
                    "Titulo": title,
                    "Artista": artist,
                    "Album": album,
                    "Ano": year
                })
                return redirect(url_for("musics"))
        return render_template("musics.html", dict_musics=dict_musics)
    

    @app.route("/artists", methods=["GET", "POST"])
    def artists():
        if request.method == "POST":
            list_artists.append(request.form.get("artist"))
            return redirect(url_for("artists"))
        return render_template("artists.html", list_artists=list_artists)