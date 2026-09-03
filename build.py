#!/usr/bin/env python3
"""タツユキ産後ケア ビルドスクリプト

src/page.html（サイト本体）と assets/*.jpg から2つの成果物を作る。

  index.html        GitHub Pages 用。本文と写真を丸ごと AES-256-GCM で暗号化し、
                    src/shell.html（解錠ゲート）に埋め込む。公開リポジトリに
                    置かれるのは暗号文だけで、平文の写真は含まれない。
  dist/artifact.html Artifact 用。アクセス制御は Artifact 側が持つので平文のまま。

使い方:  python3 build.py
"""
import base64, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

PASSWORD   = 'erinalove'
ITERATIONS = 250_000
ROOT       = os.path.dirname(os.path.abspath(__file__))

def path(*p):
    return os.path.join(ROOT, *p)

def inline_images(html):
    """assets/*.jpg を data URI として埋め込む（外部ファイルを残さないため）"""
    def sub(m):
        name = m.group(1)
        with open(path('assets', name), 'rb') as fh:
            b64 = base64.b64encode(fh.read()).decode()
        return 'src="data:image/jpeg;base64,%s"' % b64
    html = re.sub(r'src="assets/([^"]+)"', sub, html)
    assert 'assets/' not in html, '埋め込めていない画像がある'
    return html

def encrypt(plaintext):
    """salt(16) || iv(12) || 暗号文+タグ を base64 で返す"""
    salt, iv = os.urandom(16), os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    key = kdf.derive(PASSWORD.encode())
    blob = salt + iv + AESGCM(key).encrypt(iv, plaintext.encode(), None)
    return base64.b64encode(blob).decode()

def strip_wrapper(html):
    """Artifact は doctype/html/head/body を自前で用意するので中身だけ渡す"""
    head = html.split('<head>', 1)[1].split('</head>', 1)[0]
    body = html.split('<body>', 1)[1].rsplit('</body>', 1)[0]
    head = re.sub(r'\s*<meta (charset|name="viewport"|name="robots")[^>]*>', '', head)
    return head.strip() + '\n' + body.strip() + '\n'

def main():
    page = inline_images(open(path('src', 'page.html'), encoding='utf-8').read())

    shell = open(path('src', 'shell.html'), encoding='utf-8').read()
    shell = shell.replace('__ITER__', str(ITERATIONS)).replace('__PAYLOAD__', encrypt(page))
    open(path('index.html'), 'w', encoding='utf-8').write(shell)

    os.makedirs(path('dist'), exist_ok=True)
    open(path('dist', 'artifact.html'), 'w', encoding='utf-8').write(strip_wrapper(page))

    for f in ('index.html', 'dist/artifact.html'):
        print('%-20s %8d bytes' % (f, os.path.getsize(path(f))))

if __name__ == '__main__':
    sys.exit(main())
