# Technical Notes — Environment & Projects

## Development Stack
- **Language:** Python (primary)
- **Backend:** FastAPI
- **Frontend:** Next.js
- **Database:** PostgreSQL
- **Styling:** TailwindCSS
- **Tooling:** ESLint, Black, Docker Compose, Pytest
- **AI Tools:** GitHub Copilot
- **Editor:** VS Code (devcontainer installs required extensions)

## Network & Infrastructure
- **Server Host:** Unraid
- **Networking:** Pi-hole + Unbound DNS (Raspberry Pi 3B+), Ubiquiti Dream Router
- **Reverse Proxy:** Nginx Proxy Manager (on Unraid)
- **Goals:** HTTPS and DNS resolution for all containers.

## IAM Architecture Context
- Multi-cloud: AWS, Azure/Entra, GCP.
- Tools: SailPoint, CyberArk, Terraform, ServiceNow.
- Regulatory alignment required; must be auditable and certifiable.
- Current pain: No nested groups in SailPoint; balancing RBAC clarity and group sprawl.
