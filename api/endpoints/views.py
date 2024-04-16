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

    def retrieve(self, request, pk=None):
        # Ottieni il queryset dalle impostazioni comuni
        media_list = self.get_queryset()

        # FIXME: Non funziona perchè si aspetta un termine di ricerca da usare nel queryset,
        #  implementare una ricerca per ID nell'api per permettere questo metodo

        # Cerca il media in base allo site_id
        media = next((m for m in media_list if m.get_site_id == pk), None)
        if media:
            return Response(media.to_dict)
        else:
            return Response({"error": "Media not found"}, status=404)
