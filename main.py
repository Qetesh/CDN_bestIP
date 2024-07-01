import csv
import ipaddress
import os
import platform
import shlex
import subprocess
import time

import geoip2.database
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

from utils.cloudflare import cloudflare_update_dns_record
from utils.dnspod import dnspod_update_dns_record

cdn = os.getenv('cdn_provider')
dnsProvider = os.getenv('dns_provider')
cdnProvider = os.getenv('cdn_provider')
domain = os.getenv('domain')
record_name = os.getenv('record_name')
api_key = os.getenv('dns_api_key')
email = os.getenv('email')
stUrl = os.getenv('stUrl')
countryList = ['JP', 'KR', 'SG', 'US', 'HK', None]

system = platform.system()
if system == 'Darwin':  # macOS
    CloudflareSTDir = '/app/CloudflareST_darwin_amd64'
elif system == 'Linux' and platform.machine() == 'x86_64':
    CloudflareSTDir = '/app/CloudflareST_linux_amd64'
else:
    raise Exception('系统不支持')


def get_ips():
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '获取' + cdn + '最新IP')
    aws_online_url = 'https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips'
    cf_online_url = 'https://api.cloudflare.com/client/v4/ips'
    if cdn == 'cloudfront':
        response = requests.get(aws_online_url)
        ips_json_ip = response.json()['CLOUDFRONT_GLOBAL_IP_LIST'] + response.json()['CLOUDFRONT_REGIONAL_EDGE_IP_LIST']
    elif cdn == 'cloudflare':
        response = requests.get(cf_online_url, headers={'Content-Type': 'application/json'})
        ips_json_ip = response.json()['result']['ipv4_cidrs']
    else:
        raise Exception('cdn 未设置或设置错误')

    ip_list = []
    # pathPWD = ''
    # os.chdir(pathPWD)
    try:
        os.remove(CloudflareSTDir + '/ip.txt')
        os.remove(CloudflareSTDir + '/result.csv')
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)

    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
          '过滤' + '、'.join(str(x) for x in countryList) + '国家地区IP')
    with geoip2.database.Reader('utils/GeoLite2-Country.mmdb') as reader:
        for ips in ips_json_ip:
            ip = ipaddress.ip_network(ips)[0]
            response = reader.country(ip)
            # print(ip, '-', response.country.iso_code)
            if response.country.iso_code in countryList:
                ip_list = ip_list + [ips]

    # 更新IP列表至文件
    with open(CloudflareSTDir + '/ip.txt', 'w') as f:
        for ip in ip_list:
            f.write(ip + '\r\n')


def get_fastest_ip():
    # 执行文件添加执行权限
    os.chmod(CloudflareSTDir + '/CloudflareST', 0o755)
    # 执行CloudflareST，进行测速优选
    # ./CloudflareST -httping -f ip.txt -tl 150 -p 0 -url https://d20c1iz4b4gn9p.cloudfront.net/100m.test -o result.csv

    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '进行', cdnProvider, ' IP优选')
    sturl_none_shell = shlex.split('./CloudflareST -f ip.txt -tl 150 -p 0 -dd -o result.csv')
    sturl_shell = shlex.split('./CloudflareST -f ip.txt -tl 150 -p 0 -url ' + stUrl + ' -o result.csv')

    if (stUrl is None) or (stUrl == ''):
        st = subprocess.Popen(sturl_none_shell, cwd=CloudflareSTDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        st = subprocess.Popen(sturl_shell, cwd=CloudflareSTDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = st.communicate()
    st.wait()
    # print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '测速完成，获取最优IP\n', output.decode('utf-8'),
    #       error.decode('utf-8'))


def update_dns_record():
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '更新DNS-' + record_name + ' 记录')
    # IP 地址,已发送,已接收,丢包率,平均延迟,下载速度 (MB/s)
    # 99.86.219.4,4,4,0.00,46.19,50.93
    with open(CloudflareSTDir + '/result.csv', 'r') as f:
        csv_list = csv.DictReader(f)
        for record in record_name.split(','):
            best_ip = next(csv_list)
            print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '优选IP为:', best_ip['IP 地址'], '延迟：',
                  best_ip['平均延迟'], '下载速度(MB/s)：', best_ip['下载速度 (MB/s)'])

            # 更新 DNS 记录
            if dnsProvider == 'cloudflare':
                cloudflare_update_dns_record(domain, record, best_ip['IP 地址'], api_key, email)
            elif dnsProvider == 'dnspod':
                dnspod_update_dns_record(api_key, domain, record, best_ip['IP 地址'])
            else:
                raise Exception('dns_provider 未设置或设置错误')


def main():
    # 获取当前CDN最新地址库
    get_ips()
    # 获取当前CDN最快IP
    get_fastest_ip()
    # 更新DNS
    update_dns_record()


if __name__ == '__main__':
    main()
    jobs = BlockingScheduler()
    jobs.add_job(main, 'cron', hour=1, minute=00, day='*/2')
    jobs.start()
