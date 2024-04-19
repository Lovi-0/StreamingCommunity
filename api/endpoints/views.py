import json

from django.core.paginator import Paginator

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from Src.Api import search, get_version_and_domain, download_film, anime_download_film
from Src.Api.anime import EpisodeDownloader
from Src.Api.Class.Video import VideoSource
from Src.Api.series import STREAM_SITE_NAME
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
        self.page = self.request.query_params.get("page")


        match self.type_media:
            case "TV":
                self.site_version, self.domain = get_version_and_domain()

                video_source = VideoSource()
                video_source.set_url_base_name(STREAM_SITE_NAME)
                video_source.set_version(self.site_version)
                video_source.set_domain(self.domain)
                video_source.set_series_name(self.media_slug)
                video_source.set_media_id(self.media_id)

                video_source.collect_info_seasons()
                seasons_count = video_source.obj_title_manager.get_length()


                episodes = {}
                for i_season in range(1, seasons_count + 1):
                    video_source.obj_episode_manager.clear()
                    video_source.collect_title_season(i_season)
                    episodes_count = video_source.obj_episode_manager.get_length()
                    episodes[i_season] = {}
                    for i_episode in range(1, episodes_count + 1):
                        episode = video_source.obj_episode_manager.episodes[i_episode - 1]
                        episodes[i_season][i_episode] = episode.__dict__

                return Response({"episodes": episodes})
            case "TV_ANIME":
                episodes = []
                episodes_downloader = EpisodeDownloader(self.media_id, self.media_slug)
                episoded_count = episodes_downloader.get_count_episodes()
                items_per_page = 5
                try:
                    paginator = Paginator(range(episoded_count), items_per_page)

                    page_number = self.page if self.page else 1
                    page_indices = paginator.page(page_number)

                    for i in page_indices:
                        print(f"Getting info for episode {i}")
                        episode_info = episodes_downloader.get_info_episode(index_ep=i)
                        episodes.append(episode_info)
                    return Response({"episodes": episodes})
                except Exception as e:
                    return Response({"error": "Error while getting episodes info", "message": str(e)})

        return Response({"error": "No media found with that search query"})


class DownloadView(viewsets.ViewSet):

    def create(self, request):
        self.media_id = request.data.get("media_id")
        self.media_slug = request.data.get("media_slug")
        self.type_media = request.data.get("type_media").upper()
        self.episode_id = request.data.get("episode_id")

        self.site_version, self.domain = get_version_and_domain()

        response_dict = {"error": "No media found with that search query"}

        if self.type_media == "MOVIE":
            download_film(self.media_id, self.media_slug, self.domain)
            response_dict = {"message": "Download done, it is saved in Video folder inside project root"}
        elif self.type_media == "TV":
            pass
        elif self.type_media == "TV_ANIME":
            # TODO test this
            episodes_downloader = EpisodeDownloader(self.media_id, self.media_slug)
            episodes_downloader.download_episode(self.episode_id)
        elif self.type_media == "OVA":
            anime_download_film(
                id_film=self.media_id,
                title_name=self.media_slug
            )
            response_dict = {"message": "Download done, it is saved in Video folder inside project root"}

        return Response(response_dict)
