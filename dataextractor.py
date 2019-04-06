import urllib.request
import urllib.robotparser

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

    awards = get_awards()
    print("Extracted " + str(len(awards)) + " items")
    for award_id, award_name in awards.items():
        main_category_id = get_main_category_id(award_id)
        winner_dict = get_main_category_winners(award_id, main_category_id)
        print(winner_dict)
        for year, movie_id in winner_dict.items():
            if movie_id in cache:
                movie_data = cache[movie_id]
            else:
                movie_data = get_movie_data(movie_id)
                cache[movie_id] = movie_data
            store(award_id, main_category_id, year, movie_data)


def download(url):
    print(url)
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')


def get_main_category_id(festival_id):
    years = get_award_years(festival_id)
    # print(years)
    for year in years:
        # Iterating over years, as for some year there may be no data defined.
        main_award_id = find_main_award_id(festival_id, year)
        if main_award_id is not None:
            return main_award_id


def get_awards():
    awards = {}

    next_url = base_url + "es/all_awards.php?order=all"
    soup = BeautifulSoup(download(next_url), 'html.parser')

    all_awards_list = soup.find('div', {"class": "all-awards-list"})
    for a in all_awards_list.findAll('a'):
        if a.has_attr('title'):
            link = a.get('href')
            award_id = link.split("award_id=")[1]
            award_name = a.get('title')
            awards[award_id] = award_name
    # print (awards)
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
                    movie_id = link.replace(base_url, "").replace("/es/","").replace(".html", "")
                    winners[year] = movie_id

    return winners


def get_movie_data(movie_id):
    next_url = base_url + "es/" + movie_id + ".html"
    print(next_url)
    data = download(next_url)
    a = Movie("title", 2000, "director", "country", 4.5, 12312)
    return a


def store(festival_id, main_award_id, year, movie_data):
    pass


class Movie:
    def __init__(self, title, year, director, country, score, n_votes):
        self.title = title
        self.year = year
        self.director = director
        self.country = country
        self.score = score
        self.n_votes = n_votes


if __name__ == "__main__":
    main()
