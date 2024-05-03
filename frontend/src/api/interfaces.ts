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