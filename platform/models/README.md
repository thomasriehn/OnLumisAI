# Modellregistry

Jedes produktiv eingesetzte Modell hat hier ein Manifest (`manifests/*.yaml`) mit
Herkunft, Lizenz und vLLM-Startparametern. Die Compose-Services lesen die
Modell-IDs aus `.env` – ein Modellwechsel ist damit: Manifest ergänzen, `.env`
anpassen, Eval-Gate laufen lassen, Wartungsfenster.

## Modelle vorab laden (empfohlen, Pflicht bei Air-Gap)

Modelle landen im Docker-Volume `onlumis_hf-cache`, das alle vLLM-Services teilen:

```bash
./download.sh Qwen/Qwen3-32B-FP8
./download.sh BAAI/bge-m3
./download.sh BAAI/bge-reranker-v2-m3
```

Für Air-Gap-Installationen das Volume auf der Online-Maschine füllen, per
`docker run --rm -v onlumis_hf-cache:/cache -v $PWD:/out alpine tar czf /out/hf-cache.tgz -C /cache .`
exportieren und auf der Zielmaschine in das Volume entpacken; danach
`HF_HUB_OFFLINE=1` in `.env` setzen.
