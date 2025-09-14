from flask import render_template, request, redirect, url_for
import urllib, json, unicodedata, random

def init_app(app):
    dict_musics = []
    list_artists = []


    def normalize_string(s):
        """Remove acentos, espaços e coloca tudo em minúsculo"""
        s = s.lower()  # tudo minúsculo
        s = ''.join(c for c in unicodedata.normalize('NFD', s) 
                    if unicodedata.category(c) != 'Mn')  # remove acentos
        s = s.replace(' ', '')  # remove espaços
        return s


    @app.route("/")
    def home():
        highlights = dict_musics[:3]
        return render_template("index.html", highlights=highlights)
    

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


    @app.route("/apimusic", methods=["GET", "POST"])
    @app.route("/apimusic/<int:id>", methods=["GET", "POST"])
    def apimusic(id=None):
        # Definindo valores padrão
        search = "rock"
        sort_by = request.args.get("sort_by", "trackName")
        sort_order = request.args.get("sort_order", "asc")
        page = int(request.args.get("page", 1))
        results_per_page = 25

        # Formulário POST para atualizar filtros
        if request.method == "POST":
            search = request.form.get("genre", search)
            sort_by = request.form.get("sort_by", sort_by)
            page = 1
        # GET para atualizar ordenação e paginação
        else:
            search = request.args.get("genre", search)
            sort_by = request.args.get("sort_by", sort_by)
            
        # Normaliza a string de pesquisa
        search = normalize_string(search)

        # Requisição à API do iTunes
        url = f"https://itunes.apple.com/search?term={search}&entity=song&limit=200"
        response = urllib.request.urlopen(url)
        data = response.read()
        music_list = json.loads(data).get("results", [])

        # Caso haja um ID específico, buscar detalhes dessa música
        if id:
            url = f"https://itunes.apple.com/lookup?id={id}"
            response = urllib.request.urlopen(url)
            data = response.read()
            music_info_list = json.loads(data).get("results", [])
            # Destaques aleatórios do mesmo gênero
            if music_info_list:
                music_info = music_info_list[0] # Pega o primeiro resultado
                # Pega músicas do mesmo gênero
                same_genre_musics = [m for m in music_list if m.get("primaryGenreName") == music_info.get("primaryGenreName")]
                # Encontrar músicas anterior e próxima na lista atual
                previous_id = next_id = None
                for idx, m in enumerate(music_list):
                    if m.get("trackId") == id:
                        if idx > 0:
                            previous_id = music_list[idx-1].get("trackId")
                        if idx < len(music_list)-1:
                            next_id = music_list[idx+1].get("trackId")
                        break
                # Destaques aleatórios de outras músicas
                highlights = random.sample(same_genre_musics, min(4, len(same_genre_musics)))
                return render_template("musicInfo.html", music_info=music_info, previous_id=previous_id, next_id=next_id, highlights=highlights)
            else:
                return f"Música com a ID {id} não foi encontrada."
            
        # Ordenar Resultados
        reverse_sort = (sort_order == "desc")
        music_list.sort(key=lambda x: x.get(sort_by, "").lower(), reverse=reverse_sort)

        # Paginação
        total_results = len(music_list)
        start_index = (page - 1) * results_per_page
        end_index = start_index + results_per_page
        music_list_paginated = music_list[start_index:end_index]
        total_pages = (total_results + results_per_page - 1) // results_per_page

        return render_template("apimusic.html",
            music_list=music_list_paginated,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            total_pages=total_pages
        )