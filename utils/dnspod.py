import time

import requests


def dnspod_update_dns_record(api_key, domain, record_name, new_ip):
    record_id_result = requests.post(
        "https://dnsapi.cn/Record.List",
        data={
            'login_token': api_key,
            'format': 'json',
            'domain': domain,
            'record_type': 'A',
            'keyword': record_name
        }
    )
    record_id = record_id_result.json()['records'][0]['id']

    result = requests.post(
        "https://dnsapi.cn/Record.Modify",
        data={
            'login_token': api_key,
            'format': 'json',
            'domain': domain,
            'record_id': record_id,
            'sub_domain': record_name,
            'record_line': '默认',
            'record_type': 'A',
            'value': new_ip
        }
    )
    if result.json()['status']['code'] != '1':
        raise Exception(result.json()['status']['message'])
    else:
        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '更新DNS-' + record_name + ' 记录成功')
