# IAM Governance Architecture

## Overview
Design and implement a greenfield multi-cloud Identity and Access Management program for a large financial institution.

## Current State
- Multi-cloud environment: AWS, Azure/Entra, GCP.
- Tools in use: SailPoint, CyberArk, Terraform, ServiceNow.
- Compliance and audit requirements in place.

## Goals
- Implement scalable RBAC aligned with least privilege.
- Integrate SailPoint for group-based provisioning.
- Reduce group sprawl while maintaining auditable paths.
- Standardize naming conventions for access groups.
- Build PowerShell/Graph reports to map effective access.

## Constraints
- SailPoint cannot process nested groups.
- Regulators prefer 1:1 mapping between user and access in audits.
- Manual Azure portal assignment processes still in place for some workloads.

## Status
- Proposed “team role group” model documented.
- Awaiting leadership review for adoption.
