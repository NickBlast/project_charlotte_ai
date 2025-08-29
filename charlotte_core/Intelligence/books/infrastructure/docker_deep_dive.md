perfect — here’s the full entry as a single markdown file you can paste directly.
# Soul Codex — Docker Deep Dive (2025) — Nigel Poulton
**Codex Key:** `codex/docker_deep_dive_2025`  
**Scope:** Modern Docker for development & small-scale production; AI-ready patterns; Compose-first workflow; Buildx/BuildKit; Debug; Networking; Volumes; Security; Swarm/Wasm primers.  
**Last refreshed:** 2025-08-09

---

## 0 TL;DR (for Nick, career platform → micro-SaaS)
- **Use Docker Desktop (or Linux Engine) + Compose v2** as the daily driver. Treat `compose.yaml` like source code.
- **Run Ollama in Docker** to share one local LLM endpoint across projects: expose `11434`, persist `/root/.ollama` via a **named volume**, optional NVIDIA GPU via `device_requests`.
- **Builds:** `buildx` (client) → `buildkit` (server). Prefer multi-stage Dockerfiles; pin versions; keep final images small. Use cache mounts; add multi-arch only when needed.
- **Debugging:** Docker **Debug** plugin = ephemeral toolbox shell (attach to container or image sandbox). Great for one-off diagnostics without bloating images.
- **Persistence:** named volumes for data (databases, models); bind mounts only for hot code during dev.
- **Networking:** user-defined **bridge** for single host; **overlay** for multi-host (Swarm/other orchestrator).
- **Security:** drop capabilities, run as non-root, read-only filesystems where possible, Secrets for sensitive values, scan SBOMs with Docker Scout.
- **Scale path:** Local Compose → (optional) Swarm for tiny HA → managed K8s later. OCI standards keep images portable.

---

## 1 Mental Model & Architecture
- **Client/Server:** `docker` CLI → **Engine** → **containerd** → **runc**. A shim keeps containers alive if the daemon dies.  
- **OCI specs:** image-spec, runtime-spec, distribution-spec ensure portability across registries/runtimes.

**Heuristic:** If your Docker daemon restarts, containers don’t necessarily die — thanks to shims.

---

## 2 Images & Builds (Buildx / BuildKit / Cloud)
**Principles**
- Images are **layered** and read-only; containers add a writable layer.
- Favor **multi-stage** Dockerfiles. Keep the runtime image minimal (distroless, non-root).
- **Buildx** is the default frontend (since Docker 23/Desktop 4.19). **BuildKit** performs the build (local or remote).
- Multi-arch (`--platform`) only when you actually need cross-arch artifacts.  
- Performance: target stages, `--mount=type=cache`, and optionally **Docker Build Cloud** for shared caches/remote builders.

**Handy incantations**
- `docker buildx ls | create | use | inspect`
- `docker buildx build -t your/app:tag --push --platform linux/amd64,linux/arm64 .`

**Minimal multi-stage template**
```Dockerfile
# Builder
FROM node:22 AS build
WORKDIR /src
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime (distroless)
FROM gcr.io/distroless/nodejs22-debian12
WORKDIR /app
COPY --from=build /src/dist ./
USER 10001
EXPOSE 8080
CMD ["server.js"]
````

---

## 3 Containers, Observability & Docker Debug

* Lifecycle: `run`, `logs -f`, `exec -it`, `restart`, healthchecks, and restart policies.
* **Docker Debug** (CLI plugin, requires login):

  * `docker debug <container>` → attach an ephemeral toolbox; changes are visible while attached.
  * `docker debug <image>` → sandbox shell for exploration; changes discarded.
  * `install <pkg>` inside the toolbox brings Nix packages (e.g., `install bind` → `nslookup`).

**Use case:** Debug a running app without baking diagnostic tools into your production image.

---

## 4 Compose (multi-container apps) + AI Example

**Compose is code**

* Version and review it. One application per Compose file; name volumes and networks intentionally.

**AI Chatbot pattern (frontend + FastAPI + model)**

* Model service: `ollama/ollama` (port **11434**), **named volume** for `/root/.ollama`. Healthcheck `/api/tags`.
* App services talk to the model over a user-defined network by service name (`http://model:11434`).
* CPU baseline; **NVIDIA GPU** via `device_requests` when available.

**Skeleton snippet**

```yaml
services:
  model:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    volumes:
      - model_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 5s
      retries: 5
    device_requests:
      - driver: nvidia
        count: all
        capabilities: ["gpu"]

  backend:
    build: ./backend
    environment:
      - OLLAMA_BASE_URL=http://model:11434
    depends_on: [model]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]

volumes:
  model_data:
```

---

## 5 Networking

* **Bridge** (default, single host): service-name DNS on user networks; host access via `-p host:container`.
* **Overlay** (multi-host): requires an orchestrator; Swarm is the easy on-ramp.
* For local dev, prefer a dedicated user network per app; keep names obvious.

---

## 6 Volumes & Persistence

* Use **named volumes** for container-owned data (databases, vector stores, LLM weights).
* **Bind mounts** for live code in dev; avoid for persistent data.
* Quick backup:

```bash
docker run --rm -v volname:/data -v $PWD:/backup busybox \
  tar czf /backup/volname-$(date +%F).tar.gz /data
```

---

## 7 Security Quick-Sheet

* **Least privilege:** `USER` non-root, drop Linux capabilities, read-only FS when feasible.
* **Secrets:** Docker Secrets or env injection at runtime; never bake secrets into images.
* **Supply chain:** generate SBOMs, scan images (Docker Scout); sign images (Content Trust/Sigstore).
* **Surface area:** minimize base images, avoid shell in runtime layers unless essential.
* **Kernel policy:** keep seccomp/AppArmor/SELinux defaults or stricter profiles.

---

## 8 Swarm & Wasm (primers)

* **Swarm:** simple HA and rolling updates via stacks; a gentler step between Compose and K8s for tiny micro-SaaS.
* **Wasm:** early but promising; Docker can run Wasm workloads alongside containers via compatible runtimes.

---

## 9 Command Reference (curated)

* Compose lifecycle: `docker compose up -d | down | ps | logs -f | exec -it`
* Buildx/BuildKit: `buildx ls | use | create | inspect`, `buildx build --platform ...`
* Debug: `docker debug <image|container>`; in session, `install <pkg>`
* Scout: `docker scout cves <image>`, `docker scout recommendations <image>`

---

## 10 Patterns for AI Development

* Keep the **LLM runtime** (Ollama) isolated in its own Compose/app, shared by multiple projects via `localhost:11434`.
* Provide a **CPU fallback**; toggle GPU with `device_requests` only when present.
* **Healthcheck** the model (`/api/tags`) and make app services **depends\_on** the model service.
* Never store API keys/PII in images; pass via secrets or runtime env. Audit logs for prompts/output where appropriate.

---

## 11 Migration / Cleanup Helpers (high level)

* **Windows native Ollama:** uninstall via Apps/`winget`; remove `%LOCALAPPDATA%\Programs\Ollama` and `%USERPROFILE%\.ollama` (if you accept re-pulling models).
* **WSL native Ollama:** remove the package/binary and `~/.ollama`.
* **Dockerized Ollama:** `docker compose down -v` (for that app) then `docker volume rm <vol>` to reclaim space.

---

## Index / Cross-Refs

* **OCI:** image/runtime/distribution specs
* **Engine internals:** daemon, containerd, runc, shim
* **Build:** Buildx, BuildKit, multi-arch, Docker Build Cloud
* **Debug:** Docker Debug plugin
* **Compose:** AI pattern; healthchecks; device requests
* **Networking:** bridge vs overlay; service DNS
* **Persistence:** named volumes vs bind mounts
* **Security:** capabilities, seccomp, MAC, Secrets, SBOMs, Scout
* **AI:** Ollama service patterns; GPU toggles; CPU fallback

---

## Notes

Treat this codex as living. Re-validate GPU flags, Compose schema keys, and Debug/Buildx features against official docs if Docker Desktop/Engine versions change.