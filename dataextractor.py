import urllib.request
import urllib.robotparser

base_url = "https://www.filmaffinity.com/"


def main():
    print("Start.")
    default_user_agent = "Python-urllib/3.7"

    # Process robots.txt
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(base_url + "robots.txt")
    rp.read()

    cache = {}

    award_ids = get_award_ids()
    for award_id in award_ids:
        main_category_id = get_main_category_id(award_id)
        winner_dict = get_main_category_winners(award_id, main_category_id)
        for year, movie_id in winner_dict.items():
            if movie_id in cache:
                movie_data = cache[movie_id]
            else:
                movie_data = get_movie_data(movie_id)
                cache[movie_id] = movie_data
            store(award_id, main_category_id, year, movie_data)


def download(url):
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')
    return data


def get_main_category_id(festival_id):
    years = get_award_years(festival_id)
    for year in years:
        # Iterating over years, as for some year there may be no data defined.
        main_award_id = find_main_award_id(festival_id, year)
        if main_award_id is not None:
            return main_award_id


def get_award_ids():
    next_url = base_url + "es/all_awards.php?order=all"
    print(next_url)
    data = download(next_url)
    a = ["goya"]
    return a


def get_award_years(festival_id):
    next_url = base_url + "es/award_data.php?award_id=" + festival_id
    print(next_url)
    data = download(next_url)
    a = [2018]
    return a


def find_main_award_id(festival_id, year):
    next_url = base_url + "es/awards.php?award_id=" + festival_id + "&year=" + str(year)
    print(next_url)
    data = download(next_url)
    return "best_picture"


def get_main_category_winners(festival_id, main_award_id):
    next_url = base_url + "es/awards-history.php?award_id=" + festival_id + "&cat_id=" + main_award_id
    print(next_url)
    data = download(next_url)
    a = {2019: "film206800", 2018: "film114695"}
    return a


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
