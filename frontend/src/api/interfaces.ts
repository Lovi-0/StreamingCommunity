interface Image {
    imageable_id: number;
    imageable_type: string;
    filename: string;
    type: string;
    original_url_field: string;
}

export interface MediaItem {
    id: number;
    slug: string;
    name: string;
    type: string;
    score: string;
    sub_ita: number;
    last_air_date: string;
    seasons_count: number;
    images: Image[];
    comment: string;
    plot: string;
}

export interface MediaItemResponse {
    media: MediaItem[];
}

export interface Episode {
  id: number;
  anime_id: number;
  user_id: number | null;
  number: string;
  created_at: string;
  link: string;
  visite: number;
  hidden: number;
  public: number;
  scws_id: number;
  file_name: string;
  tg_post: number;
  episode_id: number;
  episode_total: number;
  name: string; // TV Show exclusive
  plot: string; // TV Show exclusive
  duration: number; // TV Show exclusive
  season_id: number; // TV Show exclusive
  created_by: any; // TV Show exclusive
  updated_at: string; // TV Show exclusive
}

export interface Season {
  [key: string]: {
    [key: string]: Episode;
  };
}

export interface SeasonResponse {
  episodes: Season;
}

export interface DownloadResponse {
    error: string;
    message: string;
}