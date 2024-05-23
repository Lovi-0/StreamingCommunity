# 15.05.24

# Fix import
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Import
from Src.Api.Streamingcommunity.Core.Class.SeriesType import TitleManager


# Test data
title_data_1 =  {'id': 1809, 'number': 1, 'name': None, 'plot': None, 'release_date': None, 'title_id': 4006, 'created_at': '2023-05-18T14:58:39.000000Z', 'updated_at': '2023-05-18T14:58:39.000000Z', 'episodes_count': 23}
title_data_2 =  {'id': 1810, 'number': 2, 'name': None, 'plot': None, 'release_date': None, 'title_id': 4006, 'created_at': '2023-05-18T14:58:40.000000Z', 'updated_at': '2023-05-18T14:58:40.000000Z', 'episodes_count': 22}
title_data_3 =  {'id': 1811, 'number': 3, 'name': None, 'plot': None, 'release_date': None, 'title_id': 4006, 'created_at': '2023-05-18T14:58:40.000000Z', 'updated_at': '2023-05-18T14:58:40.000000Z', 'episodes_count': 23}
title_data_4 =  {'id': 1812, 'number': 4, 'name': None, 'plot': None, 'release_date': None, 'title_id': 4006, 'created_at': '2023-05-18T14:58:41.000000Z', 'updated_at': '2023-05-18T14:58:41.000000Z', 'episodes_count': 22}
title_data_5 =  {'id': 1813, 'number': 5, 'name': None, 'plot': None, 'release_date': None, 'title_id': 4006, 'created_at': '2023-05-18T14:58:41.000000Z', 'updated_at': '2023-05-18T14:58:41.000000Z', 'episodes_count': 13}


# Init class series manager
title_man = TitleManager()

title_man.add_title(title_data_1)
title_man.add_title(title_data_2)
title_man.add_title(title_data_3)
title_man.add_title(title_data_4)
title_man.add_title(title_data_5)


print(title_man)
print(title_man.titles[0])