gen_secret() { openssl rand -base64 24 | tr -d '/+=' | cut -c1-24; }
set_env() { # set_env KEY VALUE  (ersetzt oder ergänzt)
set_env() { # set_env KEY VALUE  (ersetzt oder ergänzt)
  local key="$1" value="$2"
  local key="$1" value="$2"
  if grep -q "^${key}=" .env; then
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${value}|" .env
    sed -i "s|^${key}=.*|${key}=${value}|" .env
  else
  else
    echo "${key}=${value}" >> .env
    echo "${key}=${value}" >> .env
  fi
  fi
}
}
