# Developer Stack Profile

> This is a snapshot of my current development preferences, tools, language stack, deployment setup, and coding philosophy. It will evolve with experience, AI integration, and personal breakthroughs.

---

## 🖥️ Primary Language & Frameworks

### 🐍 Backend:
- **Language**: Python 3.12+
- **Framework**: FastAPI (preferred for performance + async)
- **ORM**: SQLAlchemy + Pydantic for models and validation
- **Task Queuing**: Celery (optional, exploring Redis streams)

### ⚛️ Frontend:
- **Framework**: Next.js (React-based)
- **Styling**: TailwindCSS (modular, fast)
- **Animation / UI**: Framer Motion, shadcn/ui, lucide-react

### 🗄️ Database:
- **PostgreSQL** – preferred for flexibility, indexing, JSONB support
- Exploring Prisma and Supabase for edge-stack projects

---

## ⚙️ Tooling & Workflow

### Development Environment:
- **Editor**: VS Code with devcontainers (Docker-based)
- **Linting / Formatters**:
  - Python: `black`, `isort`, `flake8`
  - JS/TS: `eslint`, `prettier`

### Version Control:
- **Git** with GitHub
- Uses semantic commit messages (feat:, fix:, chore:)

### AI Integration:
- **GitHub Copilot** (in VS Code)
- Potential expansion into Claude and custom OpenAI agents

### Virtualization:
- **Docker Compose** for all services
- Nginx Proxy Manager for container access
- Devcontainer definitions for consistent setup

### DNS & Network:
- **Pi-hole + Unbound** (on Raspberry Pi 3B+)
- **Ubiquiti Dream Router** with VLAN segmentation

---

## 🧰 Dev Philosophy & Habits

- **System-first mindset**: Focus on building workflows, not just endpoints
- **Test locally, think modularly**: One container per concern
- **Fail loudly**: Add logging and intentional error throwing
- **Use scripts as scaffolds**: Automate repetitive setup and teardown
- **Respect clean code principles**: Short functions, named parameters, clear flows

---

## 📌 TODOs / Ongoing Refinement

- Expand secrets management strategy for Docker deploys
- Consider combining or separating backend/frontend containers per use case
- Harden devcontainer onboarding (automatic extension installs, aliases)
- Evaluate Supabase vs traditional Postgres stack for next-gen apps
- Integrate OpenTelemetry for observability

> My stack isn’t static—it’s a reflection of how I learn, build, and refine in pursuit of clarity and creative flow.


