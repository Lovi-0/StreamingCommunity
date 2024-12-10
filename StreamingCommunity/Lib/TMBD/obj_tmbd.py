# 17.09.24

from typing import Dict


class Json_film:
    def __init__(self, data: Dict):
        self.adult = data.get('adult', False)
        self.backdrop_path = data.get('backdrop_path')
        self.budget = data.get('budget', 0)
        self.homepage = data.get('homepage')
        self.id = data.get('id', 0)
        self.imdb_id = data.get('imdb_id')
        self.origin_country = data.get('origin_country', [])
        self.original_language = data.get('original_language')
        self.original_title = data.get('original_title')
        self.overview = data.get('overview')
        self.popularity = data.get('popularity', 0.0)
        self.poster_path = data.get('poster_path')
        self.release_date = data.get('release_date')
        self.revenue = data.get('revenue', 0)
        self.runtime = data.get('runtime', 0)
        self.status = data.get('status')
        self.tagline = data.get('tagline')
        self.title = data.get('title')
        self.video = data.get('video', False)
        self.vote_average = data.get('vote_average', 0.0)
        self.vote_count = data.get('vote_count', 0)

    def __repr__(self):
        return (f"Film(adult={self.adult}, backdrop_path='{self.backdrop_path}', "
                f"budget={self.budget}, "
                f"homepage='{self.homepage}', id={self.id}, "
                f"imdb_id='{self.imdb_id}', origin_country={self.origin_country}, "
                f"original_language='{self.original_language}', original_title='{self.original_title}', "
                f"overview='{self.overview}', popularity={self.popularity}, poster_path='{self.poster_path}', "
                f"release_date='{self.release_date}', revenue={self.revenue}, runtime={self.runtime}, "
                f"status='{self.status}', tagline='{self.tagline}', "
                f"title='{self.title}', video={self.video}, vote_average={self.vote_average}, vote_count={self.vote_count})")
