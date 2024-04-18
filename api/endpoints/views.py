import json

from rest_framework import viewsets
from rest_framework.response import Response

from Src.Api import search, get_version_and_domain
from Src.Api.site import media_search_manager, anime_search


class SearchView(viewsets.ViewSet):
    def get_queryset(self):
        # Questa funzione viene chiamata prima di list e retrieve
        self.search_query = self.request.query_params.get("search_terms")
        self.type_search = self.request.query_params.get("type")

        media_search_manager.media_list = []
        self.site_version, self.domain = get_version_and_domain()
        self.len_database = 0
        if self.type_search == "film":
            self.len_database = search(self.search_query, self.domain)
        elif self.type_search == "anime":
            self.len_database = anime_search(self.search_query)

        return media_search_manager.media_list

    def list(self, request):
        # Ottieni il queryset dalle impostazioni comuni
        media_list = self.get_queryset()

        if self.len_database != 0:
            data_to_return = []
            for _, media in enumerate(media_list):
                data_to_return.append(media.to_dict)

            return Response({"media": data_to_return})

        return Response({"error": "No media found with that search query"})
