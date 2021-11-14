import numpy as np
import pandas as pd
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from tqdm import tqdm

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="be87c10e9ba74308855494bd12af7a65", client_secret="4d154d800d83417f8570a92e6774c876"))
data_df = pd.read_csv('tracks.csv')


class Spotify_Recommendation_euclidean():
    def __init__(self, dataset):
        self.dataset = dataset

    def get_recommend(self, song_inp, amount=1):
        distance = []
        feature_seq = [5, 2, 4, 6, 9, 11, 12, 17, 18]
        #song = self.dataset[(self.dataset.name.str.lower() == song_inp.lower())].head(1).values[0]
        rec = self.dataset
        song_features = song_inp.mean()
        for songs in tqdm(rec.values):
            d = 0
            i = 0
            for col in feature_seq:
                d = d + \
                    np.square(np.absolute(
                        (float(song_features[i]) - float(songs[col]))))
                if i == 0:
                    i = i+2
                else:
                    i = i+1
            distance.append(np.sqrt(d))
        rec['distance'] = distance
        rec = rec.sort_values('distance')
        columns = ['artists', 'name']
        return rec[:amount]


def get_user_playlist(user_id, playlist_id):
    ids = []
    fav_tracks = []
    usr_playlist = sp.user_playlist(user_id, playlist_id)
    for item in usr_playlist['tracks']['items']:
        track = item['track']
        ids.append(track['id'])
    for i in range(len(ids)):
        time.sleep(.5)
        track = get_track_features(ids[i])
        fav_tracks.append(track)
    fav_df = pd.DataFrame(fav_tracks, columns=['name', 'album', 'artist', 'release_date', 'length', 'popularity', 'acousticness',
                                               'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature'])
    return fav_df


def get_track_features(id):
    meta = sp.track(id)
    features = sp.audio_features(id)
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    release_date = meta['album']['release_date']
    length = meta['duration_ms']
    popularity = meta['popularity']
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    tempo = features[0]['tempo']
    time_signature = features[0]['time_signature']
    track = [name, album, artist, release_date, length, popularity, acousticness, danceability,
             energy, instrumentalness, liveness, loudness, speechiness, tempo, time_signature]
    return track


def main():
    st.title('Spotify Recommendation based on user playlist')

    with st.form(key='searchform'):
        nav1, nav2, nav3 = st.columns([3, 2, 1])

        with nav1:
            search_term_user = st.text_input('Enter your Profile URL')
        with nav2:
            search_term_playlist = st.text_input('Enter your Playlist URL')
        with nav3:
            st.text('Search')
            submit_search = st.form_submit_button(label='Get Tracks')
    st.text('Note: Both these links can be found on spotify app.')
    st.success('Your link id is:{}'.format(search_term_playlist))

    if submit_search:
        list = search_term_playlist.split('playlist/')
        final = list[1].split('?')
        pid = final[0]
        usr_id = search_term_user.split('user/')
        final1 = list[1].split('?')
        uid = final1[0]
        user_df = get_user_playlist(
            uid, pid)
        st.write(user_df[['name', 'album', 'artist', 'release_date']].head(10))

        st.subheader('Top 10 Recommendations')
        recommen = Spotify_Recommendation_euclidean(data_df)
        recommen_data = recommen.get_recommend(user_df, 10)
        recommen_data.reset_index(inplace=True)
        st.write(
            recommen_data[['name', 'artists', 'release_date']].head(10))


if __name__ == '__main__':
    main()
