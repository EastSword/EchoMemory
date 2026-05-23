#!/bin/bash
# EchoMemory Client — 供 Agent 使用的快捷脚本
# 用法: source echomem-client.sh && em_search "关键词"

ECHOMEM_SERVER="${ECHOMEM_SERVER:-http://localhost:9090}"
ECHOMEM_AGENT_ID="${ECHOMEM_AGENT_ID:-agent_2593c909}"
ECHOMEM_SECRET="${ECHOMEM_SECRET:--wmGp5iVBJU8m0g9tw2nIPORP4GvCjGk}"
ECHOMEM_TOKEN=""

# 登录获取 token
em_login() {
    ECHOMEM_TOKEN=$(curl -s -X POST "$ECHOMEM_SERVER/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"agent_id\":\"$ECHOMEM_AGENT_ID\",\"secret\":\"$ECHOMEM_SECRET\"}" \
        | python3 -c "import json,sys;print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
    if [ -z "$ECHOMEM_TOKEN" ]; then
        echo "Login failed" >&2
        return 1
    fi
    echo "Logged in as $ECHOMEM_AGENT_ID"
}

# 搜索知识
em_search() {
    [ -z "$ECHOMEM_TOKEN" ] && em_login
    curl -s -H "Authorization: Bearer $ECHOMEM_TOKEN" \
        "$ECHOMEM_SERVER/api/search?q=$(python3 -c "import urllib.parse;print(urllib.parse.quote('$1'))")"
}

# 获取上下文
em_context() {
    [ -z "$ECHOMEM_TOKEN" ] && em_login
    curl -s -H "Authorization: Bearer $ECHOMEM_TOKEN" \
        "$ECHOMEM_SERVER/api/context?q=$(python3 -c "import urllib.parse;print(urllib.parse.quote('$1'))")"
}

# 添加知识
em_add() {
    [ -z "$ECHOMEM_TOKEN" ] && em_login
    local type="${1:-insight}"
    local title="$2"
    local content="$3"
    local tags="$4"
    curl -s -X POST -H "Authorization: Bearer $ECHOMEM_TOKEN" \
        -H "Content-Type: application/json" \
        "$ECHOMEM_SERVER/api/knowledge" \
        -d "{\"type\":\"$type\",\"title\":\"$title\",\"content\":\"$content\",\"tags\":[$(echo $tags | sed 's/,/","/g' | sed 's/^/"/;s/$/"/')]}"
}

# 列出知识
em_list() {
    [ -z "$ECHOMEM_TOKEN" ] && em_login
    curl -s -H "Authorization: Bearer $ECHOMEM_TOKEN" \
        "$ECHOMEM_SERVER/api/knowledge?limit=${1:-10}"
}

# 统计
em_stats() {
    [ -z "$ECHOMEM_TOKEN" ] && em_login
    curl -s -H "Authorization: Bearer $ECHOMEM_TOKEN" "$ECHOMEM_SERVER/api/stats"
}

# 自动登录
em_login
