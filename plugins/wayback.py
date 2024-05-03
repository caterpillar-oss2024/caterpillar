#!/usr/bin/python3
#
# wayback.py
# Cached previous page (e.g. Wayback Machine) integration plugin for Caterpillar Proxy
#
# Caterpillar Proxy - The simple and parasitic web proxy with SPAM filter
# Namyheon Go (Catswords Research) <gnh1201@gmail.com>
# https://github.com/gnh1201/caterpillar
# Created at: 2024-03-13
# Updated at: 2024-03-13
#

# 필요한 라이브러리와 모듈을 임포트합니다.
import requests
from server import Extension
from decouple import config

# 클라이언트 인코딩 설정을 로드합니다. 설정이 잘못된 경우 예외를 처리합니다.
try:
    client_encoding = config('CLIENT_ENCODING')
except Exception as e:
    print ("[*] Invalid configuration: %s" % (str(e)))

# Google 캐시에서 주어진 URL의 페이지를 검색하는 함수입니다.
def get_cached_page_from_google(url):
    status_code, text = (0, '')  # 초기 상태 코드와 텍스트를 설정합니다.

    # Google Cache URL 구성
    google_cache_url = "https://webcache.googleusercontent.com/search?q=cache:" + url

    # Google Cache URL로 GET 요청을 보냅니다.
    response = requests.get(google_cache_url)

    # 요청이 성공적인지 확인합니다 (상태 코드 200).
    if response.status_code == 200:
        text = response.text    # 응답에서 내용을 추출합니다.
    else:
        status_code = response.status_code

    return status_code, text

# 웨이백 머신 API를 사용하여 주어진 URL의 페이지를 검색하는 함수입니다.
def get_cached_page_from_wayback(url):
    status_code, text = (0, '')

    # 웨이백 머신 API URL 구성
    wayback_api_url = "http://archive.org/wayback/available?url=" + url

    # 웨이백 머신 API로 GET 요청을 보냅니다.
    response = requests.get(wayback_api_url)

    # 요청이 성공적인지 확인합니다 (상태 코드 200).
    if response.status_code == 200:
        try:
            # JSON 응답 파싱
            data = response.json()
            archived_snapshots = data.get("archived_snapshots", {})
            closest_snapshot = archived_snapshots.get("closest", {})
            
            # 아카이브에서 URL이 사용 가능한지 확인합니다.
            if closest_snapshot:
                archived_url = closest_snapshot.get("url", "")

                # URL이 사용 가능하면 아카이브된 페이지의 내용을 가져옵니다.
                if archived_url:
                    archived_page_response = requests.get(archived_url)
                    status_code = archived_page_response.status_code
                    if status_code == 200:
                        text = archived_page_response.text
                else:
                    status_code = 404
            else:
                status_code = 404
        except:
            status_code = 502
    else:
        status_code = response.status_code

    return status_code, text

# Wayback 클래스 정의, Extension을 상속받습니다.
class Wayback(Extension):
    def __init__(self):
        self.type = "connector"   # 커넥터 유형 설정
        self.connection_type = "wayback"  # 연결 유형 설정

    # 연결 메소드 정의
    def connect(self, conn, data, webserver, port, scheme, method, url):
        connected = False

        # URL을 클라이언트 인코딩을 사용하여 디코드합니다.
        target_url = url.decode(client_encoding)

        # Google 캐시에서 페이지를 검색하고 연결을 시도합니다.
        if not connected:
            status_code, text = get_cached_page_from_google(target_url)
            if status_code == 200:
                conn.send(text.encode(client_encoding))
                connected = True

        # 웨이백 머신에서 페이지를 검색하고 연결을 시도합니다.
        if not connected:
            status_code, text = get_cached_page_from_wayback(target_url)
            if status_code == 200:
                conn.send(text.encode(client_encoding))
                connected = True

        return connected
