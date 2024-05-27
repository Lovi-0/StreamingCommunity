# 12.04.24

class Preview:
    def __init__(self, data):
        self.id = data.get("id")
        self.title_id = data.get("title_id")
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.video_id = data.get("video_id")
        self.is_viewable = data.get("is_viewable")
        self.zoom_factor = data.get("zoom_factor")
        self.filename = data.get("filename")
        self.embed_url = data.get("embed_url")

    def __str__(self):
        return f"Preview: ID={self.id}, Title ID={self.title_id}, Created At={self.created_at}, Updated At={self.updated_at}, Video ID={self.video_id}, Viewable={self.is_viewable}, Zoom Factor={self.zoom_factor}, Filename={self.filename}, Embed URL={self.embed_url}"

class Genre:
    def __init__(self, data):
        self.id = data.get("id")
        self.name = data.get("name")
        self.type = data.get("type")
        self.hidden = data.get("hidden")
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.pivot = data.get("pivot")

    def __str__(self):
        return f"Genre: ID={self.id}, Name={self.name}, Type={self.type}, Hidden={self.hidden}, Created At={self.created_at}, Updated At={self.updated_at}, Pivot={self.pivot}"

class Image:
    def __init__(self, data):
        self.id = data.get("id")
        self.filename = data.get("filename")
        self.type = data.get("type")
        self.imageable_type = data.get("imageable_type")
        self.imageable_id = data.get("imageable_id")
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.original_url_field = data.get("original_url_field")

    def __str__(self):
        return f"Image: ID={self.id}, Filename={self.filename}, Type={self.type}, Imageable Type={self.imageable_type}, Imageable ID={self.imageable_id}, Created At={self.created_at}, Updated At={self.updated_at}, Original URL Field={self.original_url_field}"

class PreviewManager:
    def __init__(self, json_data):
        self.id = json_data.get("id")
        self.type = json_data.get("type")
        self.runtime = json_data.get("runtime")
        self.release_date = json_data.get("release_date")
        self.quality = json_data.get("quality")
        self.plot = json_data.get("plot")
        self.seasons_count = json_data.get("seasons_count")
        self.genres = [Genre(genre_data) for genre_data in json_data.get("genres", [])]
        self.preview = Preview(json_data.get("preview"))
        self.images = [Image(image_data) for image_data in json_data.get("images", [])]

    def __str__(self):
        genres_str = "\n".join(str(genre) for genre in self.genres)
        images_str = "\n".join(str(image) for image in self.images)
        return f"Title: ID={self.id}, Type={self.type}, Runtime={self.runtime}, Release Date={self.release_date}, Quality={self.quality}, Plot={self.plot}, Seasons Count={self.seasons_count}\nGenres:\n{genres_str}\nPreview:\n{self.preview}\nImages:\n{images_str}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "runtime": self.runtime,
            "release_date": self.release_date,
            "quality": self.quality,
            "plot": self.plot,
            "seasons_count": self.seasons_count,
            "genres": [genre.__dict__ for genre in self.genres],
            "preview": self.preview.__dict__,
            "images": [image.__dict__ for image in self.images]
        }

