## ざっくりとしたメモ
- Seleniumを使ってTUATアカウントでログインする
- GmailAPIを使いメール本文からSSOのコードを取得

#### GmailAPIについて
- [クイックスタート](https://developers.google.com/gmail/api/quickstart/python)を参考に，GmailAPIの有効化と認証情報の発行が必要です
- メールは特定のラベルを基に取得しているため，SSOのメールに対してフィルター機能でラベルを付与する必要があります

## とりあえず必要そうなpipコマンド

```bash
pip install selenium
pip install python-dateutil
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
## バージョン
- GoogleChrome 107.0.5304.88
- ChromeDriver 107.0.5304.62

## 参考
めんどくさいからURL直貼りで
- https://developers.google.com/gmail/api/quickstart/python
- https://note.com/utatsu/n/nfae2befddce0
- https://pythonmemo.com/scraping/using_selenium_login