# Hallmark Technical Response — Charlotte

## Context
Commander requested a governance-aligned RBAC pattern for Azure/Entra with SailPoint provisioning, avoiding nested groups.

---

**Proposed Model:**

**Structure:**
User → SailPoint → Team AD Group
Team AD Group → Assigned directly to Azure Role (scope: MG, subscription, or RG)


**Naming Convention:**
role-azure-<teamname>


**Rationale:**
- Eliminates Azure nested group inheritance risks.
- Clear certification path: SailPoint certifies team group membership; Azure portal shows direct role assignment.
- Minimizes group sprawl — one group per team, reused across scopes.
- Maintains regulator-friendly 1:1 user-to-access mapping.

**Governance Enhancements:**
- Build mapping catalog: `role-azure-<team>` → scopes & roles.
- Automate mapping reports via PowerShell/MS Graph.
- Educate group owners on their group’s active scope assignments.

**Risks & Mitigations:**
- Risk: More manual Azure assignments per team.
- Mitigation: Script onboarding for new groups.
- Risk: Auditors request flat user-role export.
- Mitigation: Generate report joining SailPoint group membership + Azure role assignments.

**Example PowerShell Report Extract:**
```powershell
Get-AzRoleAssignment | Where-Object { $_.RoleDefinitionName -eq "Contributor" } |
Select-Object DisplayName, RoleDefinitionName, Scope
