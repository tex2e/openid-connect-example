
# Google OpenID Connect Example (For Study Purpose Only)

参考文献：
- https://developers.google.com/identity/protocols/oauth2/openid-connect
- Auth屋『OAuth、OAuth認証、OpenID Connectの違いを整理して理解できる本』

### 流れ：

`**********` には与えられたIDやシークレットや通信内容に応じて設定します。

#### (1) ブラウザで以下のページにアクセスする（認可エンドポイントへのアクセス）
ブラウザでアクセス：
```
https://accounts.google.com/o/oauth2/v2/auth?client_id=929**********bro.apps.googleusercontent.com&response_type=code&scope=openid%20profile&&redirect_uri=https://127.0.0.1/callback&state=0123&nonce=4567
```

![](./imgs/flow1.png)

「Login with Google」を押下する。

![](./imgs/flow2.png)

#### (2) Googleアカウントでログインすると以下URLにリダイレクトする
Googleでログイン後のリダイレクト先：
```
https://127.0.0.1/callback?code=4%2F0A**********ALg&scope=profile+openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile&authuser=1&prompt=consent
```

#### (3) トークンエンドポイントへのアクセス
Webサーバ側でGoogleのトークンエンドポイントと通信します。

リクエスト：
```
curl -v -X POST \
-d "client_id=929**********bro.apps.googleusercontent.com" \
-d "client_secret=***********************************" \
-d "redirect_uri=https://127.0.0.1/callback" \
-d "grant_type=authorization_code" \
-d "code=4%2F0A**********ALg" \
https://www.googleapis.com/oauth2/v4/token
```
レスポンス：
```
{
  "access_token": "ya29.A0**********63",
  "expires_in": 3599,
  "scope": "https://www.googleapis.com/auth/userinfo.profile openid",
  "token_type": "Bearer",
  "id_token": "eyJ**********ifQ.eyJ**********DF9.bui**********7Hg"
}
```

#### (4) JWT解析
トークンエンドポイントのレスポンスのid_tokenの内容を検証します。
```
{
  "alg": "RS256",
  "kid": "fda1066453dc9dc3dd933a41ea57da3ef242b0f7",
  "typ": "JWT"
}
{
  "iss": "https://accounts.google.com",
  "azp": "929**********bro.apps.googleusercontent.com",
  "aud": "929**********bro.apps.googleusercontent.com",
  "sub": "104650147220769694403",
  "at_hash": "nw7QKWVVCnkxWvhgYnpi8A",
  "nonce": "4567",
  "name": "tex2e",
  "picture": "https://lh3.googleusercontent.com/a-/AFdZucpyZ9viFBC0DmLcdDYiXj78GpmnTwSRLKKjrb2_=s96-c",
  "given_name": "tex2e",
  "locale": "ja",
  "iat": 1660020881,
  "exp": 1660024481
}
```

#### (5) UserInfoエンドポイントへのアクセス
取得したアクセストークンを利用して、ユーザ情報を取得します。
```
curl \
-H 'Authorization: Bearer ya29.A0**********63' \
https://openidconnect.googleapis.com/v1/userinfo
```
レスポンス：
```
{
  "sub": "104650147220769694403",
  "name": "tex2e",
  "given_name": "tex2e",
  "picture": "https://lh3.googleusercontent.com/a-/AFdZucpyZ9viFBC0DmLcdDYiXj78GpmnTwSRLKKjrb2_\u003ds96-c",
  "locale": "ja"
} 
```
pictureのURLは一定時間経過すると400エラーになる点に注意が必要です。

![](./imgs/flow3.png)
