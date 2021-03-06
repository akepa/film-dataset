import urllib.request
import urllib.parse
import urllib.robotparser
import csv
import unidecode
from urllib.error import HTTPError

from bs4 import BeautifulSoup

base_url = "https://www.filmaffinity.com/"

default_user_agent = "Python-urllib/3.7"

# Process robots.txt
rp = urllib.robotparser.RobotFileParser()
rp.set_url(base_url + "robots.txt")
rp.read()


def main():
    print("Start.")

    cache = {}

    with open('film-awards-dataset.csv', 'w', newline='', encoding='utf-8') as film_file:

        fieldnames = ['award_name', 'award_type', 'award_country', 'award_year', 'film_title', 'film_year',
                      'film_director',
                      'film_country', 'film_main_genre', 'score', 'nvotes']
        writer = csv.DictWriter(film_file, fieldnames, delimiter=',', quoting = csv.QUOTE_NONNUMERIC)
        writer.writeheader()

        award_list = get_awards()
        for award_type, awards in award_list.items():
            for award_id, award_data in awards.items():
                main_category_id = get_main_category_id(award_id)
                if main_category_id is not None:
                    winner_dict = get_main_category_winners(award_id, main_category_id)
                    # print(winner_dict)
                    for year, movie_id in winner_dict.items():

                        movie = None
                        if movie_id in cache:
                            movie = cache[movie_id]
                        else:
                            movie = get_movie_data(movie_id)
                            cache[movie_id] = movie
                        if "TV Series" in movie['film_title']:
                            # Stop processing if it is a TV serie
                            break
                        movie['award_name'] = award_data['award_name']
                        movie['award_country'] = award_data['award_country']
                        movie['award_type'] = award_type
                        movie['award_year'] = year
                        writer.writerow(movie)


def download(url):
    print(url)
    try:
        if rp.can_fetch(default_user_agent, url):
            with urllib.request.urlopen(url) as response:
                return response.read().decode('utf-8')
        else:
            print(url + " restricted by robots.txt")
    except HTTPError as e:
        input("Solve captcha manually and press Enter to continue...")
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')

def get_main_category_id(festival_id):
    years = get_award_years(festival_id)
    # print(years)
    for year in years:
        # Iterating over years, as for some year there may be no data defined.
        main_award_id = find_main_award_id(festival_id, year)
        if main_award_id is not None:
            return unidecode.unidecode(main_award_id)


def get_awards():
    awards = {}

    next_url = base_url + "es/all_awards.php?order=bytype"
    soup = BeautifulSoup(download(next_url), 'html.parser')

    all_awards_list = soup.find('div', {"class": "all-awards-list"})
    award_content = all_awards_list.findAll('div', {'class': 'award-by-type-content'})

    awards['Festival'] = get_awards_from_list(award_content[0])
    awards['Premio'] = get_awards_from_list(award_content[1])
    awards['Premio asociacion de criticos'] = get_awards_from_list(award_content[2])
    # print (awards)
    return awards


def get_awards_from_list(award_list):
    awards = {}
    for container in award_list.findAll('div', {'class': 'award-container'}):
        country = container.find('img')['title'] if container.find('img') is not None else None
        a = container.find('a')
        link = a.get('href')
        award_id = link.split("award_id=")[1]
        award_name = a.text
        awards[award_id] = {"award_name": award_name, "award_country": country}
    return awards


def get_award_years(festival_id):
    years = []

    next_url = base_url + "es/award_data.php?award_id=" + festival_id
    soup = BeautifulSoup(download(next_url), 'html.parser')
    all_winners = soup.find('table', {"id": "all-winners"})
    for a in all_winners.findAll('a'):
        link = a.get('href')
        if "year" in link:
            year = link.split("year=")[1]
            years.append(year)

    return years


def find_main_award_id(festival_id, year):
    try:
        next_url = base_url + "es/awards.php?award_id=" + festival_id + "&year=" + str(year)
        soup = BeautifulSoup(download(next_url), 'html.parser')
        div = soup.find('div', {"class": "vwacat"})
        a = div.find('a')
        link = a.get('href')
        cat_id = link.split("cat_id=")[1]
        return cat_id
    except:
        # May be blank page
        return None


def get_main_category_winners(festival_id, main_award_id):
    winners = {}

    next_url = base_url + "es/awards-history.php?award_id=" + festival_id + "&cat_id=" + main_award_id

    soup = BeautifulSoup(download(next_url), 'html.parser')
    awards_history = soup.find('div', {"class": "awards-history"})
    if awards_history is not None:
        fa_shadows = awards_history.findAll('li', {"class": "fa-shadow"})
        for fa_shadow in fa_shadows:
            year_div = fa_shadow.find('div', {"class": "year"})
            if year_div is not None:
                year = year_div.find('a').text
                movie_title_tag = fa_shadow.find('a', {"class": "movie-title-link"})
                if movie_title_tag is not None:
                    link = movie_title_tag.get('href')
                    movie_id = link.replace(base_url, "").replace("/es/", "").replace(".html", "")
                    winners[year] = movie_id

    return winners


def get_movie_data(movie_id):
    movie = {}

    next_url = base_url + "es/" + movie_id + ".html"
    soup = BeautifulSoup(download(next_url), 'html.parser')

    movie_info = soup.find('dl', {"class": "movie-info"})

    dt_list = movie_info.findAll('dt')
    dd_list = movie_info.findAll('dd')

    for idx, field in enumerate(dt_list):
        txt = field.text
        if txt is not None:
            txt = unidecode.unidecode(txt)
            if 'Titulo original' == txt:
                movie['film_title'] = dd_list[idx].text.strip()
            elif 'AKA' == txt:
                movie['film_title'] = movie['film_title'][:-3]
            elif 'Ano' == txt:
                movie['film_year'] = dd_list[idx].text.strip()
            elif 'Pais' == txt:
                movie['film_country'] = dd_list[idx].text.strip()
            elif 'Direccion' == txt:
                movie['film_director'] = get_directors(dd_list[idx])
            elif 'Genero' == txt:
                movie['film_main_genre'] = get_main_genre(dd_list[idx])

    score_field = soup.find('div', {'id': 'movie-rat-avg'})
    votes_field = soup.find('span', {'itemprop': 'ratingCount'})

    movie['score'] = score_field.text.strip().replace(',', '.') if score_field is not None else None
    movie['nvotes'] = votes_field.text.strip().replace('.', '') if votes_field is not None else None

    return movie


def get_directors(directors_field):
    director = ""
    directors = directors_field.findAll('span', {'itemprop': 'name'})
    for d in directors:
        director = director + d.text.strip() + ", "
    return director[:-2]


def get_main_genre(genres_field):
    genre_span = genres_field.find('span', {'itemprop': 'genre'})
    if genre_span is not None:
        a = genre_span.find('a')
        if a is not None:
            return genre_span.find('a').text.strip()
    return None


if __name__ == "__main__":
    main()
