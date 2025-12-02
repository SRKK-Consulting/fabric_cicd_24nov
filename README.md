# Microsoft Fabric CI/CD Pipeline

This repository contains a complete Continuous Deployment (CD) solution
for Microsoft Fabric using the **fabric-cicd** Python library and
**GitHub Actions**.\
It supports deployment of **Lakehouses**, **Notebooks**, and **Semantic
Models** across **PPE** and **PROD** environments and automatically
performs **Rebinding** (swapping IDs and connection strings for each
environment).

## 1. Project Structure

### Initial Setup

    my-fabric-repo/
    │
    ├── .github/
    │   └── workflows/
    │       └── fabric_deploy.yml
    │
    ├── src/
    │   ├── parameter.yml
    │
    ├── deploy_with_fabric.py
    ├── requirements.txt
    └── README.md

### Final Structure (After Git Sync)
In order to have this structure, we need to link github repo, src folder to the fabric workspace. The items when created in the workspace, will be populated in the src folder as the corresponding format. 

    my-fabric-repo/
    │
    ├── .github/
    │   └── workflows/
    │       └── fabric_deploy.yml
    │
    ├── src/
    │   ├── parameter.yml
    │   ├── Sales_Lakehouse.Lakehouse/
    │   ├── Sales_Notebook.Notebook/
    │   └── Sales_Model.SemanticModel/
    │
    ├── deploy_with_fabric.py
    ├── requirements.txt
    └── README.md

## 2. Configuration Files

### requirements.txt

    fabric-cicd>=0.1.25
    azure-identity

### deploy_with_fabric.py

``` python
import argparse
from fabric_cicd import FabricWorkspace, publish_all_items

def main():
    parser = argparse.ArgumentParser(description="Deploy Fabric Items")
    parser.add_argument("--workspace_id", required=True, help="Target Workspace ID")
    parser.add_argument("--environment", required=True, choices=["PPE", "PROD"], help="Context")
    parser.add_argument("--repo_path", default="./src", help="Path to source items")

    args = parser.parse_args()

    print(f"=== Fabric Deployment: {args.environment} ===")
    print(f"Target Workspace: {args.workspace_id}")

    workspace = FabricWorkspace(
        workspace_id=args.workspace_id,
        repository_directory=args.repo_path,
        environment=args.environment,
        item_type_in_scope=["Lakehouse", "Notebook", "SemanticModel"]
    )

    publish_all_items(workspace)

if __name__ == "__main__":
    main()
```

### parameter.yml

``` yaml
find_replace:
  - find_value: \#\s*META\s+"default_lakehouse":\s*"([0-9a-fA-F-]{36})"
    is_regex: "true"
    item_type: "Notebook"
    replace_value:
      PPE: "$items.Lakehouse.Sales_Lakehouse.$id"
      PROD: "$items.Lakehouse.Sales_Lakehouse.$id"

  - find_value: \#\s*META\s+"default_lakehouse_workspace_id":\s*"([0-9a-fA-F-]{36})"
    is_regex: "true"
    item_type: "Notebook"
    replace_value:
      PPE: "$workspace.$id"
      PROD: "$workspace.$id"

  - find_value: "x5k3-dev-string.datawarehouse.fabric.microsoft.com"
    item_type: "SemanticModel"
    replace_value:
      PPE: "ppesql-string.datawarehouse.fabric.microsoft.com"
      PROD: "prodsql-string.datawarehouse.fabric.microsoft.com"

  - find_value: "Sales_Lakehouse"
    item_type: "SemanticModel"
    replace_value:
      PPE: "Sales_Lakehouse"
      PROD: "Sales_Lakehouse"
```

### .github/workflows/fabric_deploy.yml

``` yaml
name: Deploy Fabric Items

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

env:
  AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}

jobs:
  deploy-ppe:
    runs-on: ubuntu-latest
    environment: PPE
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - name: Deploy to PPE
        run: |
          python deploy_with_fabric.py             --workspace_id "${{ vars.FABRIC_WORKSPACE_ID_PPE }}"             --environment "PPE"             --repo_path "./src"

  deploy-prod:
    needs: deploy-ppe
    runs-on: ubuntu-latest
    environment: PROD
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - name: Deploy to PROD
        run: |
          python deploy_with_fabric.py             --workspace_id "${{ vars.FABRIC_WORKSPACE_ID_PROD }}"             --environment "PROD"             --repo_path "./src"
```

## 3. Azure & Fabric Setup

-   Create Service Principal\
-   Enable "Service principals can use Fabric APIs"\
-   Grant workspace access in PPE & PROD

## 4. GitHub Configuration

Add repo secrets:\
- AZURE_CLIENT_ID\
- AZURE_TENANT_ID\
- AZURE_CLIENT_SECRET

Add environment variables:\
- FABRIC_WORKSPACE_ID_PPE\
- FABRIC_WORKSPACE_ID_PROD

## 5. Deployment

### Automated

Push to `main`.

### Manual

    az login
    python deploy_with_fabric.py --workspace_id "ppe-guid" --environment "PPE"
