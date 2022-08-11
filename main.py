
import os
import flask
from flask import session, redirect
import requests
import base64
import json
import my_secrets

app = flask.Flask(__name__)
app.secret_key = os.urandom(32).hex()

oauth_client_id = my_secrets.oauth_client_id
oauth_client_secret = my_secrets.oauth_client_secret
redirect_uri = 'http://127.0.0.1:8000/callback'

def oauth_auth_endpoint(csrf_token, nonce):
    oauth_auth_endpoint = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={oauth_client_id}&response_type=code&scope=openid%20profile%20email&&redirect_uri={redirect_uri}&state={csrf_token}&nonce={nonce}"
    return oauth_auth_endpoint

# トップページ（認可エンドポイントへのリンク付き）
@app.route('/')
def top():
    session['csrf'] = os.urandom(32).hex()
    session['nonce'] = os.urandom(32).hex()
    return f"""
    <a href="{oauth_auth_endpoint(session["csrf"], session['nonce'])}">Login with Google</a>
    """

# 認可エンドポイントからのリダイレクトURL
@app.route('/callback')
def callback():
    state = flask.request.args.get('state')
    code = flask.request.args.get('code')

    if (session.get('csrf') is None) or (session['csrf'] != state):
        print(f'[-] CSRF Error: state={state}')
        return "404 Not Found!"

    # トークンエンドポイントへのリクエスト
    params = {
        'client_id': oauth_client_id,
        'client_secret': oauth_client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'code': code,
    }
    print('[*] req params:', params)
    response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=params)
    print(f'[*] res status_code: {response.status_code}')
    data = response.json()
    access_token = data['access_token']
    id_token = data['id_token']

    # JWT解析
    tmp = id_token.split('.')
    header  = json.loads(base64.b64decode(tmp[0] + '=' * (-len(tmp[0]) % 4)).decode())
    payload = json.loads(base64.b64decode(tmp[1] + '=' * (-len(tmp[0]) % 4)).decode())
    print(header)
    print(payload)
    # トークンの検証
    if payload['nonce'] != session['nonce']:
        print(f"[-] Invalid Nonce: nonce={payload['nonce']}")
        return "404 Not Found!"
        # TODO: exp(トークンの有効期限)が過ぎていないか確認する

    # 取得したトークンはセッションに保存する
    session['access_token'] = access_token

    return redirect('/mypage')

# マイページ
@app.route('/mypage')
def mypage():
    # トークンを持っていない場合はトップページにリダイレクトする
    if session.get('access_token') is None:
        return redirect('/')
    access_token = session.get('access_token')

    # UserInfoエンドポイントへのアクセス
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    print('[*] req headers:', headers)
    response = requests.get('https://openidconnect.googleapis.com/v1/userinfo', headers=headers)
    print(f'[*] res status_code: {response.status_code}')
    data = response.json()
    print(data)

    # ユーザ情報の出力
    return f"""
    mypage!
    <ul>
      <li>sub: {data.get('sub')}</li>
      <li>name: {data.get('name')}</li>
      <li>email: {data.get('email')}</li>
      <li>email_verified: {data.get('email_verified')}</li>
      <li>locale: {data.get('locale')}</li>
      <li>picture:</li>
      <img src="{data.get('picture')}"></img>
    </ul>
    """

app.run(debug=True, host='0.0.0.0', port=8000)
