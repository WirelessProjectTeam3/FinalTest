import time
import datetime
import uuid
import hmac
import hashlib

# 현재 시간과 호스트 ID 기반으로 UUID 생성 후 반환
def get_uuid():
    return str(uuid.uuid1().hex)

# 현재 시간을 ISO 8601 형식의 문자열로 반환
# (예: 2024-11-18T16:41:32.807578+09:00)
def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


# SMS_API_SECRET키와 msg(data)를 이용한 HMAC-SHA256 signature를 생성 후 반환
def get_signature(key='', msg=''):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def get_headers(api_key='', api_secret_key=''):
    date = get_iso_datetime()
    salt = get_uuid()
    data = date + salt
    signature = get_signature(api_secret_key, data)
    return {
        'Authorization': 'HMAC-SHA256 ApiKey=' + api_key + ', Date=' + date + ', salt=' + salt + ', signature=' + signature,
        'Content-Type': 'application/json; charset=utf-8'
    }
    
