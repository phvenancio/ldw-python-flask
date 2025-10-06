from flask import render_template, request, redirect, url_for
import urllib, json, unicodedata, random, urllib.parse
from datetime import datetime
from models.database import db, Musics, Artists

def init_app(app):
    # ----------  FUNÇÕES AUXILIARES  ----------
    # Normaliza strings para buscas
    def normalize_string(s):
        s = s.lower() # converte para minúsculas
        s = "".join(c for c in unicodedata.normalize("NFD", s) 
                    if unicodedata.category(c) != "Mn") # remove acentuação
        s = s.replace(" ", "") # remove espaços
        return s 


    # Listas para armazenar dados temporários
    def fetch_music_data(search="rock", limit=200):
        search = search or "pop"
        search = normalize_string(search)
        search_encoded = urllib.parse.quote(search) 
        limit = max(1, min(limit, 200))  # limita entre 1 e 200
        url = f"https://itunes.apple.com/search?term={search_encoded}&entity=song&limit={limit}"
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            return json.loads(data).get("results", [])
        except urllib.error.HTTPError as e:
            print(f"Erro HTTP ao buscar '{search}': {e}")
            return []
        except urllib.error.URLError as e:
            print(f"Erro de URL ao buscar '{search}': {e}")
            return []


    # ----------  ROTAS DA APLICAÇÃO  ----------
    # Rota para a página inicial
    @app.route("/")
    def home():   
        # Busca músicas para destaques
        musics_list = fetch_music_data(limit=50)
        highlights = random.sample(musics_list, min(4, len(musics_list)))
        # Filtra músicas que possuem releaseDate
        music_list = fetch_music_data(search="pop")
        musics_with_date = [m for m in music_list if m.get("releaseDate")]
        # Converte releaseDate para datetime
        for m in musics_with_date:
            try:
                m["releaseDateParsed"] = datetime.strptime(m["releaseDate"], "%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                # Se falhar na conversão, atribui uma data mínima
                m["releaseDateParsed"] = datetime.min
        # Ordena por releaseDate e pega as 4 mais recentes
        new_releases_sorted = sorted(
            musics_with_date,
            key=lambda x: x["releaseDateParsed"],
            reverse=True
        )
        new_releases = new_releases_sorted[:4]
        # Descubra algo novo
        random_music = random.choice(musics_list) if musics_list else None
        return render_template("index.html", highlights=highlights, new_releases=new_releases, random_music=random_music)
    

    # Rota para a página de músicas
    @app.route("/musics", methods=["GET", "POST"])
    @app.route("/musics/delete/<int:id>", methods=["GET", "POST"])
    def musics(id=None):
        if id:
            music = Musics.query.get(id)
            # Deleta a música cadastrada pela ID
            db.session.delete(music)
            db.session.commit()
            return redirect(url_for("musics"))
        # Cadastra uma nova música
        if request.method == "POST":
            newmusic = Musics(request.form["title"], 
                              request.form["artist"], 
                              request.form["album"], 
                              request.form["release_year"])
            db.session.add(newmusic)
            db.session.commit()
            return redirect(url_for("musics"))
        else:
            page = request.args.get("page", 1, type=int)
            per_page = 3
            musics_page = Musics.query.paginate(page=page, per_page=per_page)
            artists = Artists.query.all()
            return render_template("musics.html", musics_list=musics_page, artists=artists)
    # Rota para editar música
    @app.route("/musics/edit/<int:id>", methods=["GET", "POST"])
    def musicEdit(id):
        music = Musics.query.get(id)
        if request.method == "POST":
            music.title = request.form["title"]
            music.artist_id = request.form["artist"]
            music.album = request.form["album"]
            music.release_year = request.form["release_year"]
            db.session.commit()
            return redirect(url_for("musics"))
        artists = Artists.query.all()
        return render_template("editmusic.html", music=music, artists=artists)


    # Rota para a página de artistas
    @app.route("/artists", methods=["GET", "POST"])
    @app.route("/artists/delete/<int:id>", methods=["GET", "POST"])
    def artists(id=None):
        if id:
            artist = Artists.query.get(id)
            # Deleta o artista cadastrado pela ID
            db.session.delete(artist)
            db.session.commit()
            return redirect(url_for("artists"))
        # Cadastra um novo artista
        if request.method == "POST":
            newartist = Artists(
                request.form["name"], 
                request.form["birth_year"], 
                request.form["nacionality"])
            db.session.add(newartist)
            db.session.commit()
            return redirect(url_for("artists"))
        else:
            page = request.args.get("page", 1, type=int)
            per_page = 3
            artists_page = Artists.query.paginate(page=page, per_page=per_page)
            return render_template("artists.html", artists_list=artists_page)
    @app.route("/artists/edit/<int:id>", methods=["GET", "POST"])
    def artistEdit(id):
        artist = Artists.query.get(id)
        if request.method == "POST":
            artist.name = request.form["name"]
            artist.birth_year = request.form["birth_year"]
            artist.nacionality = request.form["nacionality"]
            db.session.commit()
            return redirect(url_for("artists"))
        return render_template("editartist.html", artist=artist)


    # Rota para a página de detalhes da música via API
    @app.route("/apimusic", methods=["GET", "POST"])
    @app.route("/apimusic/<int:id>", methods=["GET", "POST"])
    def apimusic(id=None):
        # Valores padrão
        sort_by = request.args.get("sort_by", "trackName")
        page = int(request.args.get("page", 1))
        results_per_page = 25
        search = "rock"

        # Atualiza search via POST
        if request.method == "POST":
            search = request.form.get("genre", search)
            sort_by = request.form.get("sort_by", sort_by)
            page = 1  # reseta página ao buscar
        else:  # GET
            search = request.args.get("genre", search)
            sort_by = request.args.get("sort_by", sort_by)
            page = int(request.args.get("page", page))

        # Normaliza search
        search_normalized = normalize_string(search)
        # Busca na API usando função centralizada
        music_list = fetch_music_data(search=search_normalized, limit=200)
        
        # Se houver ID específico
        if id:
            url = f"https://itunes.apple.com/lookup?id={id}"
            response = urllib.request.urlopen(url)
            data = response.read()
            music_info_list = json.loads(data).get("results", [])
            if music_info_list:
                music_info = music_info_list[0]
                # Músicas do mesmo gênero
                same_genre_musics = [m for m in music_list if m.get("primaryGenreName") == music_info.get("primaryGenreName")]
                # IDs anterior e próximo
                previous_id = next_id = None
                for idx, m in enumerate(music_list):
                    if m.get("trackId") == id:
                        if idx > 0:
                            previous_id = music_list[idx-1].get("trackId")
                        if idx < len(music_list)-1:
                            next_id = music_list[idx+1].get("trackId")
                        break 
                # Destaques aleatórios
                highlights = random.sample(same_genre_musics, min(4, len(same_genre_musics)))
                return render_template("musicInfo.html",
                    music_info=music_info,
                    previous_id=previous_id,
                    next_id=next_id,
                    highlights=highlights
                )
            else:
                return f"Música com a ID {id} não foi encontrada."

        # Ordenação
        music_list.sort(key=lambda x: x.get(sort_by, "").lower())
        # Paginação
        total_results = len(music_list)
        start_index = (page - 1) * results_per_page
        end_index = start_index + results_per_page
        music_list_paginated = music_list[start_index:end_index]
        total_pages = (total_results + results_per_page - 1) // results_per_page

        if not music_list:
            return render_template("apimusic.html",
                music_list=[],
                search=search,
                sort_by=sort_by,
                page=1,
                total_pages=1,
                no_results=True
            )
        return render_template("apimusic.html",
            music_list=music_list_paginated,
            search=search,
            sort_by=sort_by,
            page=page,
            total_pages=total_pages
        )