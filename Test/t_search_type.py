# 15.05.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Import
from Src.Api.Streamingcommunity.Core.Class.SearchType import MediaManager


# Test data
json_media_1 = {'id': 4006, 'slug': 'person-of-interest', 'name': 'Person of Interest', 'type': 'tv', 'score': '8.6', 'sub_ita': 0, 'last_air_date': None, 'seasons_count': 5, 'images': [{'imageable_id': 4006, 'imageable_type': 'title', 'filename': '967d17c0-2a64-43b9-860c-a14b650cfbd3.webp', 'type': 'poster', 'original_url_field': None}, {'imageable_id': 4006, 'imageable_type': 'title', 'filename': '544889c3-67bf-4c4c-999a-5b9480b42c0f.webp', 'type': 'background', 'original_url_field': None}, {'imageable_id': 4006, 'imageable_type': 'title', 'filename': '3c6cb9ec-4cac-4fcc-ae47-eb2bf9f9a397.webp', 'type': 'cover', 'original_url_field': None}, {'imageable_id': 4006, 'imageable_type': 'title', 'filename': '3ce34b59-ff49-41af-9886-b169043e3f4d.webp', 'type': 'cover_mobile', 'original_url_field': None}, {'imageable_id': 4006, 'imageable_type': 'title', 'filename': '9db4b4d2-2148-44c9-bede-c40faa582f33.webp', 'type': 'logo', 'original_url_field': None}]}
json_media_2 = {'id': 2794, 'slug': 'mucca-e-pollo', 'name': 'Mucca e Pollo', 'type': 'tv', 'score': '7.5', 'sub_ita': 0, 'last_air_date': None, 'seasons_count': 4, 'images': [{'imageable_id': 2794, 'imageable_type': 'title', 'filename': '704cc5d9-6e42-4659-a81b-e41c1c626719.webp', 'type': 'poster', 'original_url_field': None}, {'imageable_id': 2794, 'imageable_type': 'title', 'filename': '4608481d-e97c-44c2-8426-0eb86d435b5f.webp', 'type': 'background', 'original_url_field': None}, {'imageable_id': 2794, 'imageable_type': 'title', 'filename': '57240efa-e295-4905-aee5-3240578e3dfe.webp', 'type': 'cover', 'original_url_field': None}, {'imageable_id': 2794, 'imageable_type': 'title', 'filename': '05827a5f-30a1-4c89-ad14-3eac4b4931c9.webp', 'type': 'cover_mobile', 'original_url_field': None}, {'imageable_id': 2794, 'imageable_type': 'title', 'filename': 'e98ab29b-9ea8-4ce0-8dcb-3d28ebaa571c.webp', 'type': 'logo', 'original_url_field': None}]}
json_media_3 = {'id': 5694, 'slug': 'vatican-girl-la-scomparsa-di-emanuela-orlandi', 'name': 'Vatican Girl: la scomparsa di Emanuela Orlandi', 'type': 'tv', 'score': '8.2', 'sub_ita': 0, 'last_air_date': None, 'seasons_count': 1, 'images': [{'imageable_id': 5694, 'imageable_type': 'title', 'filename': '19e7d5c2-d9f0-4467-b1ca-b9d043de57d5.webp', 'type': 'poster', 'original_url_field': None}, {'imageable_id': 5694, 'imageable_type': 'title', 'filename': '6ae75507-4018-4bec-83e1-85718bf8663d.webp', 'type': 'background', 'original_url_field': None}, {'imageable_id': 5694, 'imageable_type': 'title', 'filename': '05c29b8e-e490-49d2-bc36-68ccd1e9183e.webp', 'type': 'cover', 'original_url_field': None}, {'imageable_id': 5694, 'imageable_type': 'title', 'filename': '331c1787-5a64-49f7-baed-ff47df894f2b.webp', 'type': 'cover_mobile', 'original_url_field': None}, {'imageable_id': 5694, 'imageable_type': 'title', 'filename': '70f487dc-08b9-4c95-9da3-53095e9649e5.webp', 'type': 'logo', 'original_url_field': None}]}
json_media_4 = {'id': 861, 'slug': 'pokemon-detective-pikachu', 'name': 'Pokémon Detective Pikachu', 'type': 'movie', 'score': '7.4', 'sub_ita': 0, 'last_air_date': '2019-05-03', 'seasons_count': 0, 'images': [{'imageable_id': 861, 'imageable_type': 'title', 'filename': '2097306c-6a83-438b-911f-7d600b01dbaf.webp', 'type': 'cover_mobile', 'original_url_field': None}, {'imageable_id': 861, 'imageable_type': 'title', 'filename': 'dc443093-e4cc-465b-8283-acf2d9005127.webp', 'type': 'cover_mobile', 'original_url_field': None}, {'imageable_id': 861, 'imageable_type': 'title', 'filename': '057c99f1-b2fb-455c-8ed1-9f33e19c7914.webp', 'type': 'poster', 'original_url_field': None}, {'imageable_id': 861, 'imageable_type': 'title', 'filename': '6598d047-1a82-4f73-adf5-49729a6f1f45.webp', 'type': 'cover', 'original_url_field': None}, {'imageable_id': 861, 'imageable_type': 'title', 'filename': '70368946-6199-41c2-af77-c5c0b698748d.webp', 'type': 'logo', 'original_url_field': None}, {'imageable_id': 861, 'imageable_type': 'title', 'filename': '55707415-c917-404f-a50a-fba1f0fe2df0.webp', 'type': 'background', 'original_url_field': None}]}


# Init class media search manager
search_ep = MediaManager()

search_ep.add_media(json_media_1)
search_ep.add_media(json_media_2)
search_ep.add_media(json_media_3)


print(search_ep)
print(search_ep.media_list[0])
print(search_ep.media_list[0].images[0])