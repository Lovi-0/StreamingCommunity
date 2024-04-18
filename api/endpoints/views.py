import json

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from Src.Api import search, get_version_and_domain, download_film, anime_download_film
from Src.Api.anime import EpisodeDownloader
from Src.Api.site import media_search_manager, anime_search


class SearchView(viewsets.ViewSet):

    def list(self, request):
        self.search_query = request.query_params.get("search_terms")
        self.type_search = request.query_params.get("type")

        media_search_manager.media_list = []
        self.site_version, self.domain = get_version_and_domain()
        self.len_database = 0
        if self.type_search == "film":
            self.len_database = search(self.search_query, self.domain)
        elif self.type_search == "anime":
            self.len_database = anime_search(self.search_query)

        media_list = media_search_manager.media_list

        if self.len_database != 0:
            data_to_return = []
            for _, media in enumerate(media_list):
                if self.type_search == "anime" and media.type == "TV":
                    media.type = "TV_ANIME"
                data_to_return.append(media.to_dict)

            return Response({"media": data_to_return})

        return Response({"error": "No media found with that search query"})

    @action(detail=False, methods=['get'])
    def get_episodes_info(self, request):
        self.media_id = request.query_params.get("media_id")
        self.media_slug = request.data.get("media_slug")
        self.type_media = request.query_params.get("type_media")

        self.site_version, self.domain = get_version_and_domain()

        match self.type_media.upper():
            case "TV":
                pass
            case "TV_ANIME":
                episodes = []
                episodes_downloader = EpisodeDownloader(self.media_id, self.media_slug)
                episoded_count = episodes_downloader.get_count_episodes()
                for i in range(0, episoded_count - 210): # TODO: need to implement pagination, more than 5/6 episodes is slow
                    print(f"Getting info for episode {i}")
                    episode_info = episodes_downloader.get_info_episode(index_ep=i)
                    episodes.append(episode_info)
                return Response({"episodes_count": episodes})

        return Response({"error": "No media found with that search query"})


class DownloadView(viewsets.ViewSet):

    def create(self, request):
        self.media_id = request.data.get("media_id")
        self.media_slug = request.data.get("media_slug")
        self.type_media = request.data.get("type_media").upper()

        self.site_version, self.domain = get_version_and_domain()

        response_dict = {"error": "No media found with that search query"}

        if self.type_media == "FILM":
            download_film(self.media_id, self.media_slug, self.domain)
            response_dict = {"message": "Download done, it is saved in Video folder inside project root"}
        elif self.type_media == "TV":
            pass
        elif self.type_media == "TV_ANIME":
            pass
        elif self.type_media == "OVA":
            anime_download_film(
                id_film=self.media_id,
                title_name=self.media_slug
            )
            response_dict = {"message": "Download done, it is saved in Video folder inside project root"}

        return Response(response_dict)
