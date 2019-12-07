import requests
import time

#url = 'http://aweme.snssdk.com/aweme/v1/hotsearch/brand/billboard/?ac=WIFI&iid=94181137384&device_id=40150086087&os_api=18&app_name=aweme&channel=App%20Store&idfa=6B0409A5-465A-441D-B75D-7CE86B222981&device_platform=iphone&build_number=89017&vid=0036CC31-74BB-4386-8297-00C42DF26289&openudid=546a6312da9fb4460c4b3ea4055577507d2857df&device_type=iPhone8,1&app_version=8.9.0&js_sdk_version=1.32.1.0&version_code=8.9.0&os_version=13.1.2&screen_width=750&aid=1128&mcc_mnc=46011&category_id=1&request_tag_from=rn'
url = "http://lianmengapi.snssdk.com/ies/v2/discover/popular?ac=WIFI&iid=94181137384&device_id=40150086087&os_api=18&app_name=aweme&channel=App%20Store&idfa=6B0409A5-465A-441D-B75D-7CE86B222981&device_platform=iphone&build_number=89017&vid=0036CC31-74BB-4386-8297-00C42DF26289&openudid=546a6312da9fb4460c4b3ea4055577507d2857df&device_type=iPhone8,1&app_version=8.9.0&js_sdk_version=1.32.1.0&version_code=8.9.0&os_version=13.1.2&screen_width=750&aid=1128&mcc_mnc=46011&size=50&categoryId=0&user_id=487831582284760&request_tag_from=rn&page=0"


cookies = {
    'sessionid': '691114b38cd341bb8d549cba9905c483'
}

req = requests.get(
    url,
    verify=True,
    cookies=cookies
)

print(req.content.decode())
