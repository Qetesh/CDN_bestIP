import time

import CloudFlare


def cloudflare_update_dns_record(domain, record_name, new_ip, api_key, email):
    cf = CloudFlare.CloudFlare(email=email, token=api_key)

    # 获取域名的Zone ID
    zones = cf.zones.get(params={'name': domain})
    if len(zones) == 0:
        raise Exception("Domain not found in Cloudflare.")
    zone_id = zones[0]['id']

    # 获取A记录的Record ID
    records = cf.zones.dns_records.get(zone_id, params={'name': record_name + '.' + domain, 'type': 'A'})
    if len(records) == 0:
        raise Exception("A record not found.")
    record_id = records[0]['id']

    # 更新A记录的IP地址
    data = {
        'name': record_name + '.' + domain,
        'type': 'A',
        'content': new_ip,
        'proxied': False
    }
    cf.zones.dns_records.put(zone_id, record_id, data=data)

    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '更新 DNS 记录成功')
