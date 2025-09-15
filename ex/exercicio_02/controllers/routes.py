from flask import render_template, request, redirect, url_for
import urllib, json, unicodedata, random, urllib.parse
from datetime import datetime

def init_app(app):
    dict_musics = []
    list_artists = []

    def normalize_string(s):
        s = s.lower() # converte para minúsculas
        s = ''.join(c for c in unicodedata.normalize('NFD', s) 
                    if unicodedata.category(c) != 'Mn') # remove acentuação
        s = s.replace(' ', '') # remove espaços
        return s 

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
    

    @app.route("/musics", methods=["GET", "POST"])
    def musics():
        if request.method == "POST":
            title = request.form.get("title")
            artist = request.form.get("artist")
            album = request.form.get("album")
            year = request.form.get("year")

            if all([title, artist, album, year]): # Verifica se todos os campos foram preenchidos
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
            list_artists.append(request.form.get("artist")) # Adiciona o artista à lista
            return redirect(url_for("artists"))
        return render_template("artists.html", list_artists=list_artists)


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