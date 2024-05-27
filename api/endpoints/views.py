import json
import os

from django.http import StreamingHttpResponse

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from Src.Api.Animeunity import title_search as anime_search
from Src.Api.Animeunity.Core.Vix_player.player import VideoSource as anime_source
from Src.Api.Animeunity.site import media_search_manager as anime_media_manager

from Src.Api.Streamingcommunity import title_search as sc_search, get_version_and_domain
from Src.Api.Streamingcommunity.Core.Vix_player.player import VideoSource as film_video_source
from Src.Api.Streamingcommunity.site import media_search_manager as film_media_manager


class SearchView(viewsets.ViewSet):

    def list(self, request):
        self.search_query = request.query_params.get("search_terms")
        self.type_search = request.query_params.get("type")

        media_manager = anime_media_manager if self.type_search == "anime" else film_media_manager
        media_manager.media_list = []
        self.len_database = 0
        if self.type_search == "film":
            _, self.domain = get_version_and_domain()
            self.len_database = sc_search(self.search_query, self.domain)
        elif self.type_search == "anime":
            self.len_database = anime_search(self.search_query)

        media_list = media_manager.media_list

        if self.len_database != 0:
            data_to_return = []
            for _, media in enumerate(media_list):
                if self.type_search == "anime":
                    if media.type == "TV":
                        media.type = "TV_ANIME"
                    if media.type == "Movie":
                        media.type = "OVA"
                data_to_return.append(media.to_dict)

            return Response({"media": data_to_return})

        return Response({"error": "No media found with that search query"})

    @action(detail=False, methods=["get"])
    def get_episodes_info(self, request):
        self.media_id = request.query_params.get("media_id")
        self.media_slug = request.query_params.get("media_slug")
        self.type_media = request.query_params.get("type_media")

        try:
            match self.type_media:
                case "TV":

                    def stream_episodes():
                        self.version, self.domain = get_version_and_domain()

                        video_source = film_video_source()
                        video_source.setup(
                            version=self.version,
                            domain=self.domain,
                            media_id=self.media_id,
                            series_name=self.media_slug
                        )
                        video_source.collect_info_seasons()
                        seasons_count = video_source.obj_title_manager.get_length()

                        episodes = {}
                        for i_season in range(1, seasons_count + 1):
                            video_source.obj_episode_manager.clear()
                            video_source.collect_title_season(i_season)
                            episodes_count = (
                                video_source.obj_episode_manager.get_length()
                            )
                            episodes[i_season] = {}
                            for i_episode in range(1, episodes_count + 1):
                                episode = video_source.obj_episode_manager.episodes[
                                    i_episode - 1
                                ]
                                episodes[i_season][i_episode] = episode.to_dict()

                        yield f'{json.dumps({"episodes": episodes})}\n\n'

                    response = StreamingHttpResponse(
                        stream_episodes(), content_type="text/event-stream"
                    )
                    return response

                case "TV_ANIME":
                    def stream_episodes():
                        video_source = anime_source()
                        video_source.setup(
                            media_id = self.media_id,
                            series_name = self.media_slug
                        )
                        episoded_count = video_source.get_count_episodes()

                        for i in range(0, episoded_count):
                            episode_info = video_source.get_info_episode(i).to_dict()
                            episode_info["episode_id"] = i
                            episode_info["episode_total"] = episoded_count
                            print(f"Getting episode {i} of {episoded_count} info...")
                            yield f"{json.dumps(episode_info)}\n\n"

                    response = StreamingHttpResponse(
                        stream_episodes(), content_type="text/event-stream"
                    )
                    return response

        except Exception as e:
            return Response(
                {
                    "error": "Error while getting episodes info",
                    "message": str(e),
                }
            )

        return Response({"error": "No media found with that search query"})
    
    @action(detail=False, methods=["get"])
    def get_preview(self, request):
        self.media_id = request.query_params.get("media_id")
        self.media_slug = request.query_params.get("media_slug")
        self.type_media = request.query_params.get("type_media")

        try:
            if self.type_media in  ["TV", "MOVIE"]:
                version, domain = get_version_and_domain()
                video_source = film_video_source()
                video_source.setup(media_id=self.media_id, version=version, domain=domain, series_name=self.media_slug)
                video_source.get_preview()
                return Response(video_source.obj_preview.to_dict())
            if self.type_media in  ["TV_ANIME", "OVA", "SPECIAL"]:
                video_source = anime_source()
                video_source.setup(media_id=self.media_id, series_name=self.media_slug)
                video_source.get_preview()
                return Response(video_source.obj_preview.to_dict())
        except Exception as e:
            return Response(
                {
                    "error": "Error while getting preview info",
                    "message": str(e),
                }
            )

        return Response({"error": "No media found with that search query"})


'''
class DownloadView(viewsets.ViewSet):

    def create(self, request):
        self.media_id = request.data.get("media_id")
        self.media_slug = request.data.get("media_slug")
        self.type_media = request.data.get("type_media").upper()
        self.download_id = request.data.get("download_id")
        self.tv_series_episode_id = request.data.get("tv_series_episode_id")

        if self.type_media in ["TV", "MOVIE"]:
            self.site_version, self.domain = get_version_and_domain()

        response_dict = {"error": "No media found with that search query"}

        try:
            match self.type_media:
                case "MOVIE":
                    download_film(self.media_id, self.media_slug, self.domain)
                case "TV":
                    video_source = VideoSource()
                    video_source.set_url_base_name(STREAM_SITE_NAME)
                    video_source.set_version(self.site_version)
                    video_source.set_domain(self.domain)
                    video_source.set_series_name(self.media_slug)
                    video_source.set_media_id(self.media_id)

                    video_source.collect_info_seasons()
                    video_source.obj_episode_manager.clear()

                    video_source.collect_title_season(self.download_id)
                    episodes_count = video_source.obj_episode_manager.get_length()
                    for i_episode in range(1, episodes_count + 1):
                        episode_id = video_source.obj_episode_manager.episodes[
                            i_episode - 1
                        ].id

                        # Define filename and path for the downloaded video
                        mp4_name = remove_special_characters(
                            f"{map_episode_title(self.media_slug,video_source.obj_episode_manager.episodes[i_episode - 1],self.download_id)}.mp4"
                        )
                        mp4_path = remove_special_characters(
                            os.path.join(
                                ROOT_PATH,
                                SERIES_FOLDER,
                                self.media_slug,
                                f"S{self.download_id}",
                            )
                        )
                        os.makedirs(mp4_path, exist_ok=True)

                        # Get iframe and content for the episode
                        video_source.get_iframe(episode_id)
                        video_source.get_content()
                        video_source.set_url_base_name(STREAM_SITE_NAME)

                        # Download the episode
                        obj_download = Downloader(
                            m3u8_playlist=video_source.get_playlist(),
                            key=video_source.get_key(),
                            output_filename=os.path.join(mp4_path, mp4_name),
                        )

                        obj_download.download_m3u8()

                case "TV_ANIME":
                    episodes_downloader = EpisodeDownloader(
                        self.media_id, self.media_slug
                    )
                    episodes_downloader.download_episode(self.download_id)
                case "OVA" | "SPECIAL":
                    anime_download_film(
                        id_film=self.media_id, title_name=self.media_slug
                    )
                case _:
                    raise Exception("Type media not supported")

            response_dict = {
                "message": "Download done, it is saved in Video folder inside project root"
            }
        except Exception as e:
            response_dict = {
                "error": "Error while downloading the media",
                "message": str(e),
            }

        return Response(response_dict)
'''
