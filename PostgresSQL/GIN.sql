CREATE TABLE IF NOT EXISTS songslist (
    track_id VARCHAR(255) PRIMARY KEY,
    track_name VARCHAR(255),
    track_artist VARCHAR(255),
    lyrics TEXT,
    track_popularity INTEGER,
    track_album_id VARCHAR(255),
    track_album_name VARCHAR(255),
    track_album_release_date VARCHAR(255),
    playlist_name VARCHAR(255),
    playlist_id VARCHAR(255),
    playlist_genre VARCHAR(255),
    playlist_subgenre VARCHAR(255),
    danceability NUMERIC,
    energy NUMERIC,
    key INTEGER,
    loudness NUMERIC,
    mode INTEGER,
    speechiness NUMERIC,
    acousticness NUMERIC,
    instrumentalness NUMERIC,
    liveness NUMERIC,
    valence NUMERIC,
    tempo NUMERIC,
    duration_ms INTEGER,
    language VARCHAR(5)
);

COPY songslist(track_id, track_name, track_artist, lyrics, track_popularity, track_album_id, track_album_name, track_album_release_date, playlist_name, playlist_id, playlist_genre, playlist_subgenre, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, duration_ms, language)
FROM 'C:\spotify_songs.csv' DELIMITER ',' CSV HEADER;

ALTER TABLE songslist ADD COLUMN combined_text TEXT;

UPDATE songslist
SET combined_text = 
    COALESCE(track_id, '') || ' ' ||
    COALESCE(track_name, '') || ' ' ||
    COALESCE(track_artist, '') || ' ' ||
    COALESCE(lyrics, '') || ' ' ||
    COALESCE(track_popularity::TEXT, '') || ' ' ||
    COALESCE(track_album_id, '') || ' ' ||
    COALESCE(track_album_name, '') || ' ' ||
    COALESCE(track_album_release_date, '') || ' ' ||
    COALESCE(playlist_name, '') || ' ' ||
    COALESCE(playlist_id, '') || ' ' ||
    COALESCE(playlist_genre, '') || ' ' ||
    COALESCE(playlist_subgenre, '') || ' ' ||
    COALESCE(danceability::TEXT, '') || ' ' ||
    COALESCE(energy::TEXT, '') || ' ' ||
    COALESCE(key::TEXT, '') || ' ' ||
    COALESCE(loudness::TEXT, '') || ' ' ||
    COALESCE(mode::TEXT, '') || ' ' ||
    COALESCE(speechiness::TEXT, '') || ' ' ||
    COALESCE(acousticness::TEXT, '') || ' ' ||
    COALESCE(instrumentalness::TEXT, '') || ' ' ||
    COALESCE(liveness::TEXT, '') || ' ' ||
    COALESCE(valence::TEXT, '') || ' ' ||
    COALESCE(tempo::TEXT, '') || ' ' ||
    COALESCE(duration_ms::TEXT, '') || ' ' ||
    COALESCE(language, '');

UPDATE songslist
SET combined_text = TRIM(BOTH ' ' FROM combined_text);

ALTER TABLE songslist ADD COLUMN full_text tsvector;

UPDATE songslist SET full_text = T.full_text
FROM (
    SELECT track_id, setweight(to_tsvector('english', combined_text), 'A') AS full_text
    FROM songslist
) T
WHERE T.track_id = songslist.track_id;

CREATE INDEX text_search_idx ON songslist USING gin(combined_text gin_trgm_ops);

SELECT track_id, track_artist, lyrics, ts_rank_cd(full_text, query) AS rank
FROM songslist, to_tsquery('english', 'Don|Omar') query
WHERE query @@ full_text
ORDER BY rank ASC
LIMIT 100;