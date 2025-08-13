<h1 align="center"><b>MediaJanitor</b></h1>

<p align="center">
一个用于在 <b>Plex</b> 删除媒体后，自动清理 <b>MoviePilot</b> 和 <b>qBittorrent</b> 中对应任务 / 资源的轻量工具。<br/>
</p>

---

## 简介
MediaJanitor 监听 Plex 媒体目录的删除事件，识别被删除的剧集 / 电影对应的下载任务，并在 MoviePilot 与 qBittorrent 中执行关联清理（移除任务 / 种子，可选同时删除文件），帮助你保持存储与下载任务列表的整洁。

> 自用项目，不保证通用性与绝对稳定

## 快速开始

拉取镜像：

```bash
docker pull hidka/mediajanitor:1.0.0
```

示例 docker-compose.yml：

```yaml
services:
  mediajanitor:
    image: hidka/mediajanitor:1.0.0
    container_name: mediajanitor
    hostname: mediajanitor
    volumes:
      - /home/mediajanitor/Config/docker/mediajanitor/config:/config  # 配置 & 缓存
      - /home/mediajanitor/Media:/media                               # 媒体目录根
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
      - PLEX_MEDIA_DIR=/media/plex
      - MOVIEPILOT_BASE_URL=http://localhost:3000
      - MOVIEPILOT_USER=admin
      - MOVIEPILOT_PASSWORD=admin
      - MOVIEPILOT_DELETE_SRC=true
      - MOVIEPILOT_DELETE_DEST=true
      - QBITTORRENT_BASE_URL=http://localhost:8080
      - QBITTORRENT_USER=admin
      - QBITTORRENT_PASSWORD=admin
    network_mode: host
    restart: always
```

启动：
```bash
docker compose up -d
```

查看日志：
```bash
docker logs -f mediajanitor
```

## 环境变量
| 变量 | 说明 | 必填 | 默认 |
| ---- | ---- | ---- | ---- |
| PUID / PGID | 运行用户/用户组 ID | 否 | 1000 |
| TZ | 时区 | 否 | Asia/Shanghai |
| PLEX_MEDIA_DIR | Plex 媒体根目录（容器内路径） | 是 | - |
| MOVIEPILOT_BASE_URL | MoviePilot 地址 | 否 | http://localhost:3000 |
| MOVIEPILOT_USER / MOVIEPILOT_PASSWORD | MoviePilot 登录信息 | 否 | admin / admin |
| MOVIEPILOT_DELETE_SRC | 是否删除源任务 | 否 | true |
| MOVIEPILOT_DELETE_DEST | 是否删除目标（可能的转存路径） | 否 | true |
| QBITTORRENT_BASE_URL | qBittorrent WebUI 地址 | 否 | http://localhost:8080 |
| QBITTORRENT_USER / QBITTORRENT_PASSWORD | qBittorrent 登录 | 否 | admin / admin |


## 常见问题
1. 没有触发删除？
   - 确认 PLEX_MEDIA_DIR 挂载正确且与 Plex 实际使用路径一致。
   - 检查容器用户是否有 inotify 权限 / 读权限。
2. MoviePilot 未删除？
   - 检查账号密码 / 是否需要 Token（后续可扩展）。
3. qBittorrent 未找到对应种子？
   - 文件命名不一致；可考虑后续加入哈希映射策略。

---