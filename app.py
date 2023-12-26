from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
app.run(debug=True, port=5001)


# Spotify API kimlik bilgilerini çevresel değişkenlerden al
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

#ayth
sp_oauth = SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=redirect_uri,
                        scope='user-library-read playlist-modify-public')

# api bağlantisi
sp = None


def get_uri_from_link(link):
    parsed_url = urlparse(link)
    path_components = parsed_url.path.split('/')
    song_uri = path_components[-1]
    return song_uri



@app.route('/', methods=['GET', 'POST'])
def index():
    global sp
    if request.method == 'POST':
        song_link = request.form['song_link']
        target_speechiness = request.form.get('target_speechiness', None)
        target_popularity = request.form.get('target_popularity', None)
        target_valence = request.form.get('target_valence', None)
        max_acousticness = request.form.get('max_acousticness', None)
        target_acousticness = request.form.get('target_acousticness', None)
        instrumentalness = request.form.get('instrumentalness', None)
        target_loudness = request.form.get('target_loudness', None)
        target_danceability = request.form.get('target_danceability', None)
        target_energy = request.form.get('target_energy', None)
        target_liveness = request.form.get('target_liveness', None)


        num_recommendations = request.form.get('num_recommendations', 10)
        # if num_recommendations:
        #     request.form.get(None)
        #     num_recommendations = 10

        song_uri = get_uri_from_link(song_link)

        if not sp:
            sp = spotipy.Spotify(auth_manager=sp_oauth)

        recommended_tracks = get_song_recommendations(song_uri, target_speechiness, target_popularity,
                                                      target_valence, max_acousticness, target_acousticness,
                                                      instrumentalness, target_loudness, target_danceability,
                                                      target_energy, target_liveness, num_recommendations)

        return render_template('index.html', recommended_tracks=recommended_tracks)

    return render_template('index.html', recommended_tracks=None)




def get_song_recommendations(song_uri, target_speechiness=None, target_popularity=None, target_valence=None,
                             max_acousticness=None, target_acousticness=None, instrumentalness=None,
                             target_loudness=None, target_danceability=None, target_energy=None, target_liveness=None,
                             num_recommendations=10):


    song_features = sp.audio_features(song_uri)
    song_features = song_features[0] if song_features else None


    # Varsayılan değerleri şarkının özelliklerine eşitle
    if song_features:
        target_speechiness = target_speechiness or song_features['speechiness']
        # target_popularity = target_popularity or song_features['popularity']
        target_valence = target_valence or song_features['valence']
        max_acousticness = max_acousticness or 1.0
        target_acousticness = target_acousticness or song_features['acousticness']
        instrumentalness = instrumentalness or 0.0
        target_loudness = target_loudness or song_features['loudness']
        target_danceability = target_danceability or song_features['danceability']
        target_energy = target_energy or song_features['energy']
        target_liveness = target_liveness or song_features['liveness']


    recommendations = sp.recommendations(
        seed_tracks=[song_uri],
        limit=int(num_recommendations or "10"),
        target_speechiness=target_speechiness,
        # target_popularity=target_popularity,
        target_valence=target_valence,
        max_acousticness=max_acousticness,
        target_acousticness=target_acousticness,
        instrumentalness=instrumentalness,
        target_loudness=target_loudness,
        target_danceability=target_danceability,
        target_energy=target_energy,
        target_liveness=target_liveness
    )

    recommended_tracks = []
    for track in recommendations['tracks']:
        recommended_tracks.append({
            'name': track['name'],
            'artist': track['artists'][0]['name']
        })

    return recommended_tracks


def get_user_input(prompt, default=None):
    user_input = input(f"{prompt} [{default}]: ")
    return user_input if user_input.strip() else default



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
