import csv
import os
import subprocess
import platform
import time

import requests
import geoip2.database
import ipaddress
from update_dns import update_dns_record
from apscheduler.schedulers.blocking import BlockingScheduler

domain = os.getenv('domain')
record_name = os.getenv('record_name')
api_key = os.getenv('api_key')
email = os.getenv('email')
stUrl = os.getenv('stUrl')
countryList = ['JP', 'KR', 'SG', 'US']

system = platform.system()
if system == 'Darwin':  # macOS
    CloudflareSTDir = 'CloudflareST_darwin_amd64'
elif system == 'Linux' and platform.machine() == 'x86_64':
    CloudflareSTDir = 'CloudflareST_linux_amd64'
else:
    CloudflareSTDir = 'CloudflareST_linux_amd64'


def update():
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '获取cloudfront最新IP')
    awsOnlineUrl = 'https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips'
    response = requests.get(awsOnlineUrl)
    ipsJson = response.json()

    ipList = []
    # pathPWD = ''
    # os.chdir(pathPWD)
    try:
        os.remove(CloudflareSTDir + '/ip.txt')
        os.remove(CloudflareSTDir + '/result.csv')
    except Exception as e:
        print(e)

    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
          '筛选出' + '、'.join(str(x) for x in countryList) + '国家地区IP')
    with geoip2.database.Reader('GeoLite2-Country.mmdb') as reader:
        for ips in ipsJson['CLOUDFRONT_GLOBAL_IP_LIST'] + ipsJson['CLOUDFRONT_REGIONAL_EDGE_IP_LIST']:
            ip = ipaddress.ip_network(ips)[0]
            response = reader.country(ip)
            # print(ip, '-', response.country.iso_code)
            if response.country.iso_code in countryList:
                ipList = ipList + [ips]

    # 更新IP列表至文件
    with open(CloudflareSTDir + '/ip.txt', 'w') as f:
        for ip in ipList:
            f.write(ip + '\r\n')

    # 执行文件添加执行权限
    os.chmod(CloudflareSTDir + '/CloudflareST', 0o755)
    # 执行CloudflareST，进行测速优选
    # ./CloudflareST -httping -f ip.txt -tl 150 -p 0 -url https://d20c1iz4b4gn9p.cloudfront.net/100m.test -o result.csv
    print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '进行cloudfront IP优选')
    if (stUrl is None) or (stUrl == ''):
        st = subprocess.Popen(['./CloudflareST', '-f', 'ip.txt',
                               '-tl', '150',
                               '-p', '0',
                               '-dd',
                               '-o', 'result.csv'],
                              cwd=CloudflareSTDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        st = subprocess.Popen(['./CloudflareST', '-httping', '-f', 'ip.txt',
                               '-tl', '150',
                               '-p', '0',
                               '-url', stUrl,
                               '-o', 'result.csv'],
                              cwd=CloudflareSTDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = st.communicate()
    st.wait()

    # IP 地址,已发送,已接收,丢包率,平均延迟,下载速度 (MB/s)
    # 99.86.219.4,4,4,0.00,46.19,50.93
    with open(CloudflareSTDir + '/result.csv', 'r') as f:
        csvList = csv.DictReader(f)
        bestCDNIP = next(csvList)
        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), '优选IP为:', bestCDNIP['IP 地址'], '延迟：',
              bestCDNIP['平均延迟'], '下载速度(MB/s)：', bestCDNIP['下载速度 (MB/s)'])

    # 调用 CloudFlora API，更新 DNS 记录
    update_dns_record(domain, record_name, bestCDNIP['IP 地址'], api_key, email)


update()
jobs = BlockingScheduler()
jobs.add_job(update, 'cron', hour=1, minute=00, day='*/3')
jobs.start()
