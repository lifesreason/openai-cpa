---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'f67a0372-a3b9-42a6-b333-d777425860ab'
  PropagateID: 'f67a0372-a3b9-42a6-b333-d777425860ab'
  ReservedCode1: '73c96ac7-f99f-423e-9d0b-b313a3c88dc5'
  ReservedCode2: '73c96ac7-f99f-423e-9d0b-b313a3c88dc5'
---

# Wenfxl Codex Manager 自构建部署教程

镜像通过 GitHub Actions 自动构建，产物存放在 GitHub Container Registry（ghcr.io），无需注册 Docker Hub。

---

## 一、触发构建

代码推送到 `main` 分支时自动构建，也可以手动触发：

1. 打开 https://github.com/lifesreason/openai-cpa/actions
2. 左侧选 **Build and Push Docker Image**
3. 点 **Run workflow** → 选 `main` 分支 → **Run workflow**

构建约 5-10 分钟，产出 `linux/amd64` + `linux/arm64` 双平台镜像。

构建完成后镜像地址：

```
ghcr.io/lifesreason/openai-cpa:latest
```

可在 GitHub 查看：https://github.com/lifesreason/openai-cpa/pkgs/container/openai-cpa

---

## 二、在任意服务器上部署

### 1. 登录 GitHub Container Registry

ghcr.io 镜像默认是 private，需要先登录才能拉取：

```bash
echo "你的GitHub_PAT" | docker login ghcr.io -u lifesreason --password-stdin
```

PAT（Personal Access Token）获取方式：
1. 打开 https://github.com/settings/tokens?type=beta
2. **Generate new token** → 名称随意
3. 权限勾选 **Packages: Read**（只需读取）
4. 复制生成的 token

> 如果你的仓库是 public 且在 Packages 设置中将镜像设为 public，则无需登录即可拉取。

### 2. docker compose 启动（推荐）

```bash
mkdir -p /opt/codex && cd /opt/codex

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  codex-web:
    image: ghcr.io/lifesreason/openai-cpa:latest
    container_name: wenfxl_codex_manager
    ports:
      - "8000:8000"
    restart: always
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/app/data
EOF

docker compose up -d
```

### 3. docker run 启动

```bash
docker run -d \
  --name wenfxl_codex_manager \
  --restart always \
  -p 8000:8000 \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/data:/app/data \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/lifesreason/openai-cpa:latest
```

### 4. 访问

浏览器打开 `http://服务器IP:8000`，初始密码 `admin`

---

## 三、连接宿主机代理

如果服务器上运行了代理（如 Clash），在前端配置中将代理地址写为：

- HTTP 代理：`http://host.docker.internal:7890`
- SOCKS5 代理：`socks5h://host.docker.internal:7891`

端口号替换为你实际代理端口。

---

## 四、连接云端 MySQL（可选）

默认使用本地 SQLite。如需 MySQL：

```yaml
version: '3.8'

services:
  codex-web:
    image: ghcr.io/lifesreason/openai-cpa:latest
    container_name: wenfxl_codex_manager
    ports:
      - "8000:8000"
    restart: always
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - TZ=Asia/Shanghai
      - DB_TYPE=mysql
      - DB_HOST=你的MySQL地址
      - DB_PORT=3306
      - DB_USER=root
      - DB_PASS=你的数据库密码
      - DB_NAME=wenfxl_manager
    volumes:
      - ./data:/app/data
```

---

## 五、更新镜像

```bash
cd /opt/codex
docker compose pull
docker compose up -d
```

---

## 六、将镜像设为公开（可选）

设为 public 后任何人都可直接 `docker pull`，无需 PAT 登录：

1. 打开 https://github.com/lifesreason/openai-cpa/pkgs/container/openai-cpa/settings
2. **Danger Zone → Change visibility → Public**

---

## 七、常见问题

| 问题 | 解决方案 |
|------|----------|
| pull 报 unauthorized | 先 `docker login ghcr.io`，或把镜像设为 public |
| 端口无法访问 | 检查服务器防火墙是否放行 8000 |
| 容器内无法访问宿主机代理 | 确认 `extra_hosts` 已配置，代理用 `host.docker.internal` |
| GitHub Actions 构建失败 | 检查 workflow 中 `permissions: packages: write` 是否配置 |

> AI生成