from flask import Flask, render_template, redirect, url_for, session, request
import requests
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

GOOGLE_CLIENT_ID = '399325390927-07ksnk6lelrm8i6td4njdnqqvo5jnj75.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/login/authorized'
GOOGLE_API_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    google_auth_url = (
        f'https://accounts.google.com/o/oauth2/auth?'
        f'client_id={GOOGLE_CLIENT_ID}&'
        f'redirect_uri={GOOGLE_REDIRECT_URI}&'
        f'scope=email&'
        f'response_type=code'
    )
    return redirect(google_auth_url)

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home'))

@app.route('/login/authorized')
def authorized():
    error = request.args.get('error')
    if error:
        return f'Authorization failed. Error: {error}'

    auth_code = request.args.get('code')
    
    if auth_code is None:
        return 'Authorization failed.'

    token_url = 'https://accounts.google.com/o/oauth2/token'
    token_data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    token_response = requests.post(token_url, data=token_data)
    token_info = token_response.json()

    if 'access_token' not in token_info:
        return 'Access token not received.'

    session['google_token'] = token_info['access_token']
    time = datetime.datetime.now()
    formatted_date_time = time.strftime("%Y-%m-%d %H:%M:%S")
    user_info_response = requests.get(GOOGLE_API_URL, params={'access_token': session['google_token']})
    print(user_info_response)
    user_info = user_info_response.json()
    print(user_info)
    profile_picture = user_info.get('photos', [{}])[0].get('url', '')

    return render_template('home.html', user_info=user_info, profile_picture=profile_picture, time=formatted_date_time)

if __name__ == '__main__':
    app.run(debug=True)
