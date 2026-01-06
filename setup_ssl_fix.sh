#!/bin/bash
# SSL证书修复脚本 - 永久解决SSL验证问题
# 使用方法: source setup_ssl_fix.sh

# 获取certifi的证书路径（Python包管理的最新证书）
CERTIFI_PATH=$(python -c "import certifi; print(certifi.where())" 2>/dev/null)

if [ -n "$CERTIFI_PATH" ] && [ -f "$CERTIFI_PATH" ]; then
    echo "✓ 找到certifi证书: $CERTIFI_PATH"
    
    # 设置所有SSL相关的环境变量
    export SSL_CERT_FILE="$CERTIFI_PATH"
    export REQUESTS_CA_BUNDLE="$CERTIFI_PATH"
    export CURL_CA_BUNDLE="$CERTIFI_PATH"
    export PIP_CERT="$CERTIFI_PATH"
    
    # 对于某些工具，也设置这个
    export SSL_CERT_DIR="$(dirname $CERTIFI_PATH)"
    
    echo "✓ SSL环境变量已设置:"
    echo "  SSL_CERT_FILE=$SSL_CERT_FILE"
    echo "  REQUESTS_CA_BUNDLE=$REQUESTS_CA_BUNDLE"
    echo "  CURL_CA_BUNDLE=$CURL_CA_BUNDLE"
    echo "  PIP_CERT=$PIP_CERT"
    echo ""
    echo "现在可以运行需要SSL的命令了"
    
else
    echo "✗ 找不到certifi证书文件"
    echo "正在尝试使用系统证书..."
    
    # 回退到系统证书
    if [ -f "/etc/pki/tls/certs/ca-bundle.crt" ]; then
        export SSL_CERT_FILE="/etc/pki/tls/certs/ca-bundle.crt"
        export REQUESTS_CA_BUNDLE="/etc/pki/tls/certs/ca-bundle.crt"
        export CURL_CA_BUNDLE="/etc/pki/tls/certs/ca-bundle.crt"
        export PIP_CERT="/etc/pki/tls/certs/ca-bundle.crt"
        echo "✓ 使用系统证书: /etc/pki/tls/certs/ca-bundle.crt"
    else
        echo "✗ 也找不到系统证书文件"
        echo "将禁用SSL验证（不安全，但可以工作）"
        export PYTHONHTTPSVERIFY=0
        export CURL_SSL_VERIFYPEER=false
        echo "⚠ 警告: SSL验证已禁用"
    fi
fi

# 验证设置是否有效
echo ""
echo "测试SSL连接..."
python -c "import urllib.request; urllib.request.urlopen('https://pypi.org', timeout=5); print('✓ SSL连接测试成功！')" 2>/dev/null || echo "✗ SSL连接仍有问题"
