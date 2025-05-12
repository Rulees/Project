SOPS_LATEST_VERSION=$(curl -s "https://api.github.com/repos/getsops/sops/releases/latest" | grep -Po '"tag_name": "v\K[0-9.]+')
curl -Lo sops.deb "https://github.com/getsops/sops/releases/download/v${SOPS_LATEST_VERSION}/sops_${SOPS_LATEST_VERSION}_amd64.deb"
sudo apt install -y ./sops.deb
rm -rf sops.deb && sops --version

# Сбор нужных ключей из SOPS_KEYS
KEYS=""
for name in $SOPS_KEYS; do
  VAR_NAME="SOPS_$(echo "$name" | tr '[:lower:]' '[:upper:]')_KEY"
  KEYS="${KEYS}${!VAR_NAME}"$'\n'
done

# Расшифровка всех допустимых файлов в secrets/ (in-place)
SOPS_AGE_KEY="$KEYS" find secrets/ -type f \
  ! -name "*.gitkeep" \
  ! -name "README.md" \
  -exec sops --decrypt --in-place {} \;