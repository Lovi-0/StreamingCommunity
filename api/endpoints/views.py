from rest_framework import viewsets
from rest_framework.response import Response

from Src.Api import search, get_version_and_domain
from Src.Api.site import media_search_manager, anime_search


class SearchView(viewsets.ViewSet):
    def list(self, request):
        search_query = request.query_params.get("search_terms")
        type_search = request.query_params.get("type")

        media_search_manager.media_list = []
        site_version, domain = get_version_and_domain()
        if type_search == "film":
            len_database = search(search_query, domain)
        elif type_search == "anime":
            len_database = anime_search(search_query)
        if len_database != 0:
            media_list = media_search_manager.media_list
            data_to_return = []
            for i, media in enumerate(media_list):
                data_to_return.append({
                    "id": i,
                    "name": media.name,
                    "type": media.type,
                    "score": media.score,
                    "last_air_date": media.last_air_date
                })

            return Response({"media": data_to_return})

        return Response({"error": "No media found with that search query"})
