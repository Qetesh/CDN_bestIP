# CDN_bestIP
[![CDN_bestIP docker image](https://github.com/Qetesh/CDN_bestIP/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Qetesh/CDN_bestIP/actions/workflows/docker-image.yml)

[中文版本](README.md) | [English Version](README_EN.md)

CDN_bestIP 是一个使用 Python 编写的项目，通过[官方链接](https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips)实现自动获取 AWS CloudFront 的所有 IP 地址，并根据当前网络对其进行CloudFront优选，排除大陆IP，获取最快IP。后通过 Cloudflare 更新域名解析，优化当前网络下CloudFront的网络质量。

该项目使用 [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest) 项目来进行IP测速。

## 功能
![img.png](images/img1.png)
- 自动获取所有 AWS CloudFront IP 地址（使用maxmind地址库排除大陆备案IP地址段，测速IP包含'JP', 'KR', 'SG', 'US'）。
- 基于当前网络对 IP 地址进行速度测试。
- 更新 Cloudflare 域名解析为最快的 IP 地址。
- 通过 python cron 定期自动更新记录，默认为一天运行一次
- **可使用自建服务器，指定测速链接，`stURL` 变量设置自定义 url 测速**
设置系统环境变量

> stUrl（可选，可通过`dd if=/dev/zero of=100MB.test bs=1M count=100`在网站根目录生成测试文件）
> 
> 测试Url连接为:`https://xxxxxxx.cloudfront.net/100MB.test`
> 
> 如服务测速信息与cloudflare配置如下：
> 
> 域名为:`cdn.example.com`
> 
> cloudflare邮箱地址为:`admin@exmple.com`
> 
> Global API Key:`ccccccccccccccccccccccccccccccc`

CloudflareSpeedTest构建方式：`export GOOS=linux && export GOARCH=amd64 && go build -o ..
/CloudflareST_linux_amd64/CloudflareST -ldflags "-s -w"`
---

## 使用方法- Docker 环境
> docker安装  https://docs.docker.com/engine/install/
> 
> docker compose安装 https://docs.docker.com/compose/install/
```
docker run -d --name ghcr.io/qetesh/cdn_bestip:latest \
  --restart always \
  -e domain='example.com' \
  -e record_name='cdn' \
  -e api_key='ccccccccccccccccccccccccccccccc' \
  -e email='admin@exmple.com' \
  -e stUrl='https://xxxxxxx.cloudfront.net/100MB.test' \
  cdn_bestip
```

使用 Docker Compose 运行，可参考[docker-compose.yml](docker-compose.yml)。需先设置`.env`文件：
.env
```shell
domain = 'example.com'
record_name = 'cdn'
api_key = 'ccccccccccccccccccccccccccccccc'
email = 'admin@exmple.com'
stUrl = 'https://xxxxxxx.cloudfront.net/100MB.test'
```

```shell
docker compose up -d
```

<details>
  <summary>Docker 本地构建运行</summary>
该项目可以在 Docker 环境中运行。你可以使用提供的 Dockerfile 构建镜像，并通过 Docker 或 Docker Compose 运行。

首先，使用以下命令构建 Docker 镜像：

```shell
docker build -t cdn_bestip .
```

然后，运行容器（stUrl参数可选）：

```shell
docker run -d --name cdn_bestip \
  --restart always \
  -e domain='example.com' \
  -e record_name='cdn' \
  -e api_key='ccccccccccccccccccccccccccccccc' \
  -e email='admin@exmple.com' \
  -e stUrl='https://xxxxxxx.cloudfront.net/100MB.test' \
  cdn_bestip
```

或者，使用 Docker Compose 运行，需先设置`.env`文件：
![img.png](images/img1.png)
.env
```shell
domain = 'example.com'
record_name = 'cdn'
api_key = 'ccccccccccccccccccccccccccccccc'
email = 'admin@exmple.com'
stUrl = 'https://xxxxxxx.cloudfront.net/100MB.test'
```

```shell
docker compose build
docker compose up -d
```
</details>

<details>
  <summary>使用方法-本地运行</summary>
## 使用方法-本地运行

### 1. 克隆项目

使用以下命令克隆项目到本地：

```shell
git clone https://github.com/qetesh/CDN_bestIP.git
```
### 2. 安装依赖

安装python3、pip3：
```shell
apt install python3 python3-pip
```
进入项目目录，并安装所需的 Python 依赖：

```shell
cd CDN_bestIP
pip3 install -r requirements.txt
```

### 3. 配置 Cloudflare API

环境变量设置的值对应如下：
```plaintext
export domain='example.com' record_name='cdn' api_key='ccccccccccccccccccccccccccccccc' email='admin@exmple.com' stUrl='https://xxxxxxx.cloudfront.net/100MB.test'
```

确保替换上述值为你自己的 Cloudflare 域名、A记录域名、Global API Key 、邮箱地址、测速URL（可选）。

### 4. 运行项目

运行以下命令启动项目（默认将一直保持前台运行，可使用`nohup python3 main.py &`保持后台运行）：

```shell
python3 main.py
```
</details>

---

## 感谢项目

- https://github.com/XIU2/CloudflareSpeedTest
- https://www.maxmind.com

## Todo
### CDN
- [x] aws CloudFront
- [ ] CloudFlare
### DNS服务商
- [x] CloudFlare
- [ ] DNSPod

## 贡献

欢迎贡献代码、报告问题或提出改进建议。请在 GitHub 上提交 Issue 或 Pull Request。

## 许可证

本项目基于 MIT 许可证。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

## 免责声明

本项目仅供学习和参考，使用本项目所产生的一切后果由使用者自行承担。请谨慎使用，并遵守相关法律法规和服务提供商的条款。

