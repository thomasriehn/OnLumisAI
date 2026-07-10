#!/usr/bin/env bash
# =============================================================================
# OnLumis – Komplett-Setup für die NVIDIA DGX Spark
# =============================================================================
# Richtet eine frische Spark bis zum laufenden, befragbaren System ein:
# Vorprüfungen -> .env-Erzeugung -> NVFP4-Modelle laden -> Stack starten ->
# Beispielquelle indexieren -> goldene Fragen -> Smoke-Test -> (systemd).
#
# Chat-Modelle: von NVIDIA veröffentlichte NVFP4-Checkpoints (Blackwell-nativ).
#
#   ./deploy/setup-spark.sh --domain onlumis.firma.local --install-systemd
#   ./deploy/setup-spark.sh --model qualitaet --with-monitoring
#   ./deploy/setup-spark.sh --check-only          # nur Vorprüfungen
#
# Optionen:
#   --domain <name>       Interner DNS-Name (Default: $(hostname -f))
#   --model <preset|hf-id>  Chat-Modell, Presets siehe unten (Default: standard)
#   --auth-mode dev|oidc  Erstbetrieb dev, Produktion oidc (Default: dev)
#   --with-monitoring     Prometheus/Grafana mitstarten
#   --with-ocr            Ingestion-Image mit Tesseract-OCR bauen
#   --install-systemd     Autostart + täglichen Backup-Timer einrichten (sudo)
#   --skip-models         Modell-Downloads überspringen (bereits im Cache)
#   --skip-beispiel       Beispielkorpus/goldene Fragen nicht einspielen
#   --check-only          Nur Vorprüfungen ausführen, nichts ändern
#   --yes                 Keine Rückfragen (unattended)
#
# NVFP4-Presets (NVIDIA auf Hugging Face, Stand Juli 2026 – aktuelle Liste:
# https://huggingface.co/nvidia -> Suche "NVFP4"):
#   standard   nvidia/Qwen3.6-35B-A3B-NVFP4            MoE, 3B aktiv -> schnell,
#                                                      bester Allrounder auf der Spark
#   qualitaet  nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4  groß, höchste Qualität
#   klassisch  nvidia/Qwen3-32B-NVFP4                  dicht, konservative Wahl
#   kompakt    nvidia/Llama-3.1-8B-Instruct-NVFP4      klein/schnell (Tests, kleine Teams)
# Embeddings/Reranker/Whisper bleiben Standard-Checkpoints (BGE-M3 u. a.) –
# dafür veröffentlicht NVIDIA keine NVFP4-Varianten; sie sind klein genug.
# =============================================================================
set -euo pipefail

PLATFORM_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLATFORM_DIR"

# ---------------------------------------------------------------- Parameter
DOMAIN="$(hostname -f 2>/dev/null || echo localhost)"
MODEL="standard"
AUTH_MODE="dev"
PROFILES=(--profile models)
WITH_OCR=0
INSTALL_SYSTEMD=0
SKIP_MODELS=0
SKIP_BEISPIEL=0
CHECK_ONLY=0
ASSUME_YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --domain) DOMAIN="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --auth-mode) AUTH_MODE="$2"; shift 2 ;;
    --with-monitoring) PROFILES+=(--profile monitoring); shift ;;
    --with-ocr) WITH_OCR=1; shift ;;
    --install-systemd) INSTALL_SYSTEMD=1; shift ;;
    --skip-models) SKIP_MODELS=1; shift ;;
    --skip-beispiel) SKIP_BEISPIEL=1; shift ;;
    --check-only) CHECK_ONLY=1; shift ;;
    --yes) ASSUME_YES=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unbekannte Option: $1 (siehe --help)"; exit 2 ;;
  esac
done

case "$MODEL" in
  standard)  CHAT_MODEL_ID="nvidia/Qwen3.6-35B-A3B-NVFP4";                 CHAT_MEM=0.55 ;;
  qualitaet) CHAT_MODEL_ID="nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4"; CHAT_MEM=0.75 ;;
  klassisch) CHAT_MODEL_ID="nvidia/Qwen3-32B-NVFP4";                       CHAT_MEM=0.50 ;;
  kompakt)   CHAT_MODEL_ID="nvidia/Llama-3.1-8B-Instruct-NVFP4";           CHAT_MEM=0.35 ;;
  */*)       CHAT_MODEL_ID="$MODEL";                                       CHAT_MEM=0.55 ;;
  *) echo "FEHLER: unbekanntes Modell-Preset '$MODEL'"; exit 2 ;;
esac

EMBED_MODEL_ID="BAAI/bge-m3"
RERANK_MODEL_ID="BAAI/bge-reranker-v2-m3"
WHISPER_MODEL_ID="openai/whisper-large-v3-turbo"

ok()   { printf '  \033[32m✔\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m⚠\033[0m %s\n' "$1"; }
fail() { printf '  \033[31m✘\033[0m %s\n' "$1"; FAILED=1; }
step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

confirm() {
  [ "$ASSUME_YES" = 1 ] && return 0
  read -r -p "$1 [j/N] " answer
  [ "$answer" = "j" ] || [ "$answer" = "J" ] || [ "$answer" = "y" ]
}

# --------------------------------------------------------------- Vorprüfung
step "Vorprüfungen (DGX Spark)"
FAILED=0

ARCH="$(uname -m)"
if [ "$ARCH" = "aarch64" ]; then ok "Architektur: aarch64 (GB10)"; else fail "Architektur ist $ARCH, erwartet aarch64 (DGX Spark)"; fi

if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
  ok "Docker läuft ($(docker --version | cut -d, -f1))"
else
  fail "Docker fehlt oder Daemon läuft nicht"
fi

if docker info --format '{{json .Runtimes}}' 2>/dev/null | grep -q nvidia; then
  ok "NVIDIA Container Runtime registriert"
else
  fail "NVIDIA Container Toolkit fehlt (auf DGX OS vorinstalliert – prüfen!)"
fi

if command -v nvidia-smi >/dev/null && nvidia-smi -L >/dev/null 2>&1; then
  ok "GPU sichtbar: $(nvidia-smi -L | head -1)"
else
  fail "nvidia-smi meldet keine GPU"
fi

AVAIL_GB=$(df -B1G --output=avail /var/lib/docker 2>/dev/null | tail -1 | tr -d ' ' || echo 0)
if [ "${AVAIL_GB:-0}" -ge 150 ]; then
  ok "Freier Speicher für Docker: ${AVAIL_GB} GB"
else
  fail "Nur ${AVAIL_GB:-?} GB frei unter /var/lib/docker (>=150 GB empfohlen: Images + Modelle)"
fi

if grep -qs "nvcr.io" "${DOCKER_CONFIG:-$HOME/.docker}/config.json" 2>/dev/null; then
  ok "NGC-Registry-Login vorhanden (nvcr.io)"
else
  warn "Kein nvcr.io-Login gefunden – vorher: docker login nvcr.io (API-Key: ngc.nvidia.com)"
fi

if [ "${HF_HUB_OFFLINE:-0}" = "1" ]; then
  warn "HF_HUB_OFFLINE=1 – Modellprüfung/-download übersprungen (Air-Gap?)"
elif curl -sf --max-time 10 "https://huggingface.co/api/models/${CHAT_MODEL_ID}" -o /dev/null; then
  ok "Chat-Modell existiert auf Hugging Face: ${CHAT_MODEL_ID}"
else
  fail "Chat-Modell '${CHAT_MODEL_ID}' nicht erreichbar/gefunden (Netz? Tippfehler? NVFP4-Liste: huggingface.co/nvidia)"
fi

echo
echo "Geplante Konfiguration:"
echo "  Domain        : $DOMAIN"
echo "  Chat-Modell   : $CHAT_MODEL_ID (NVFP4, GPU-Mem ${CHAT_MEM})"
echo "  Embeddings    : $EMBED_MODEL_ID | Reranker: $RERANK_MODEL_ID | Whisper: $WHISPER_MODEL_ID"
echo "  Auth-Modus    : $AUTH_MODE $( [ "$AUTH_MODE" = dev ] && echo '(nur Erstbetrieb! Produktion: oidc)' )"
echo "  Profile       : ${PROFILES[*]} | OCR-Image: $WITH_OCR | systemd: $INSTALL_SYSTEMD"

if [ "$CHECK_ONLY" = 1 ]; then
  [ "$FAILED" = 1 ] && { echo; echo "Vorprüfung: FEHLGESCHLAGEN (siehe ✘)"; exit 1; }
  echo; echo "Vorprüfung: OK – Start mit demselben Aufruf ohne --check-only."; exit 0
fi
[ "$FAILED" = 1 ] && { echo; echo "Abbruch: Vorprüfungen beheben (oder --check-only zum erneuten Testen)."; exit 1; }
confirm "Fortfahren?" || exit 0

# ------------------------------------------------------------- .env erzeugen
step ".env konfigurieren"
gen_secret() { openssl rand -base64 24 | tr -d '/+=' | cut -c1-24; }
set_env() { # set_env KEY VALUE  (ersetzt oder ergänzt)
  local key="$1" value="$2"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${value}|" .env
  else
    echo "${key}=${value}" >> .env
  fi
}

if [ ! -f .env ]; then
  cp .env.example .env
  set_env POSTGRES_PASSWORD "$(gen_secret)"
  set_env KEYCLOAK_DB_PASSWORD "$(gen_secret)"
  KC_ADMIN_PW="$(gen_secret)"
  set_env KEYCLOAK_ADMIN_PASSWORD "$KC_ADMIN_PW"
  set_env GRAFANA_ADMIN_PASSWORD "$(gen_secret)"
  ok ".env erzeugt (Zugangsdaten generiert)"
  echo "  Keycloak-Admin: Benutzer 'admin', Passwort: $KC_ADMIN_PW"
  echo "  (steht in .env – sicher verwahren, Datei bleibt außerhalb von Git)"
else
  warn ".env existiert – Zugangsdaten bleiben unverändert, Modell/Domain werden gesetzt"
fi
set_env ONLUMIS_DOMAIN "$DOMAIN"
set_env AUTH_MODE "$AUTH_MODE"
set_env CHAT_MODEL_ID "$CHAT_MODEL_ID"
set_env CHAT_GPU_MEM_FRACTION "$CHAT_MEM"
set_env WHISPER_MODEL_ID "$WHISPER_MODEL_ID"
[ "$WITH_OCR" = 1 ] && set_env WITH_OCR 1
ok "Konfiguration geschrieben (Domain, Modell, Auth)"

# ------------------------------------------------------ Images bauen/ziehen
step "Docker-Images bauen und ziehen"
docker compose "${PROFILES[@]}" build
docker compose "${PROFILES[@]}" pull --ignore-buildable
ok "Images bereit"

# --------------------------------------------------------- Modelle vorladen
if [ "$SKIP_MODELS" = 1 ] || [ "${HF_HUB_OFFLINE:-0}" = "1" ]; then
  step "Modell-Downloads übersprungen"
else
  step "Modelle in den Cache laden (einmalig, je nach Leitung einige Zeit)"
  ./models/download.sh "$CHAT_MODEL_ID"
  ./models/download.sh "$EMBED_MODEL_ID"
  ./models/download.sh "$RERANK_MODEL_ID"
  ./models/download.sh "$WHISPER_MODEL_ID"
  ok "Alle Modelle im Volume onlumis_hf-cache"
fi

# --------------------------------------------------------------- Stack-Start
step "Stack starten"
docker compose "${PROFILES[@]}" up -d
ok "Container gestartet – warte auf Dienste"

wait_for() { # wait_for BESCHREIBUNG TIMEOUT_S CMD...
  local desc="$1" timeout="$2"; shift 2
  local waited=0
  until "$@" >/dev/null 2>&1; do
    sleep 5; waited=$((waited + 5))
    if [ "$waited" -ge "$timeout" ]; then fail "$desc nicht bereit nach ${timeout}s"; return 1; fi
  done
  ok "$desc bereit (${waited}s)"
}

wait_for "PostgreSQL" 120 docker compose exec -T postgres pg_isready -U onlumis -d onlumis
wait_for "RAG-API" 180 docker compose exec -T api python -c \
  "import httpx; assert httpx.get('http://localhost:8000/readyz', timeout=4).status_code == 200"
# Modell-Load beim Erststart dauert etliche Minuten (Gewichte -> unified memory)
wait_for "vLLM Chat-Modell (Erststart lädt Gewichte, bitte Geduld)" 1800 \
  docker compose exec -T api python -c \
  "import httpx; assert httpx.get('http://vllm-chat:8001/v1/models', timeout=5).status_code == 200"
wait_for "Embeddings" 600 docker compose exec -T api python -c \
  "import httpx; assert httpx.get('http://vllm-embed:8002/v1/models', timeout=5).status_code == 200"

# ------------------------------------------------- Beispielkorpus + Fragen
if [ "$SKIP_BEISPIEL" = 0 ]; then
  step "Beispielkorpus und goldene Fragen"
  SOURCES=$(docker compose exec -T postgres psql -U onlumis -d onlumis -Atc \
    "SELECT count(*) FROM knowledge.sources" 2>/dev/null || echo 0)
  if [ "${SOURCES:-0}" = "0" ]; then
    docker compose exec -T ingestion python -m worker.main add-source \
      --name beispiel --root /data/sources/beispiel --acl all-users
    docker compose exec -T ingestion python -m worker.main once
    ok "Beispielquelle indexiert"
  else
    warn "Quellen existieren bereits (${SOURCES}) – überspringe Beispielquelle"
  fi
  docker compose exec -T postgres psql -q -U onlumis -d onlumis < db/seed/eval-beispiel.sql
  ok "Goldene Starterfragen eingespielt (idempotent)"
fi

# -------------------------------------------------------------- Smoke-Test
step "Smoke-Test"
READY=$(curl -sk --resolve "${DOMAIN}:443:127.0.0.1" "https://${DOMAIN}/api/readyz" || true)
case "$READY" in *'"ok"'*) ok "HTTPS-Route über Caddy: /api/readyz ok" ;; *) warn "readyz über Caddy nicht ok ($READY) – DNS/Zertifikat prüfen" ;; esac

if [ "$AUTH_MODE" = "dev" ]; then
  ANSWER=$(curl -sk --max-time 300 --resolve "${DOMAIN}:443:127.0.0.1" \
    "https://${DOMAIN}/api/v1/answers" \
    -H 'content-type: application/json' -H 'X-Dev-User: setup' -H 'X-Dev-Groups: all-users' \
    -d '{"question":"Wie viel Sonderurlaub gibt es bei einer Hochzeit?"}' || true)
  case "$ANSWER" in
    *citations*) ok "Ende-zu-Ende-Antwort mit Quellen erhalten:"; \
      echo "$ANSWER" | python3 -c 'import json,sys;d=json.load(sys.stdin);print("    »"+d["answer"][:120]+"«");print("    Quellen:",len([c for c in d["citations"] if c["used"]]))' 2>/dev/null || true ;;
    *) warn "Keine Antwort erhalten – docker compose logs api vllm-chat prüfen" ;;
  esac
else
  warn "AUTH_MODE=oidc: Antwort-Smoke-Test übersprungen (Token nötig) – im Browser testen"
fi

# ----------------------------------------------------------------- systemd
if [ "$INSTALL_SYSTEMD" = 1 ]; then
  step "systemd: Autostart + Backup-Timer (sudo)"
  sudo install -m 644 deploy/systemd/onlumis-platform.service /etc/systemd/system/
  sudo install -m 644 deploy/systemd/onlumis-backup.service /etc/systemd/system/
  sudo install -m 644 deploy/systemd/onlumis-backup.timer /etc/systemd/system/
  sudo sed -i "s|/opt/onlumis/platform|$PLATFORM_DIR|g" \
    /etc/systemd/system/onlumis-platform.service /etc/systemd/system/onlumis-backup.service
  sudo systemctl daemon-reload
  sudo systemctl enable onlumis-platform.service
  sudo systemctl enable --now onlumis-backup.timer
  ok "Autostart aktiviert, Backup täglich 02:00 (BACKUP_DIR in der Unit anpassen: NAS!)"
fi

# ---------------------------------------------------------------- Abschluss
step "Fertig – OnLumis läuft"
cat <<EOF
  Chat & Suche : https://${DOMAIN}/          Verwaltung: https://${DOMAIN}/admin
  API-Doku     : https://${DOMAIN}/api/docs  MCP: https://${DOMAIN}/api/mcp
  Keycloak     : https://${DOMAIN}/auth      (admin / Passwort siehe .env)

Nächste Schritte:
  1) Produktion: AUTH_MODE=oidc in .env, AD/LDAP-Federation im Realm 'onlumis'
     einrichten und den Demo-Nutzer 'demo' löschen (RUNBOOK §1.6).
  2) Echte Wissensquellen anbinden (Admin-Handbuch §3) und ACLs setzen.
  3) PoC-Messung für die Modellwahl:
     .venv/bin/python deploy/bench/loadtest.py --base-url https://${DOMAIN}/api \\
       --insecure --users 10 --duration 120
     Alternativ-Presets: --model qualitaet|klassisch|kompakt (Skript erneut ausführen)
  4) BACKUP_DIR auf ein NAS legen und Restore einmal üben (RUNBOOK §5).
EOF
