import argparse
import os
from fabric_cicd import FabricWorkspace, publish_all_items

def main():
    parser = argparse.ArgumentParser(description="Deploy Fabric Items (Lakehouse, Notebook, Semantic Model)")
    parser.add_argument("--workspace_id", required=True, help="Target Workspace ID")
    parser.add_argument("--environment", required=True, choices=["PPE", "PROD"], help="Environment Context (PPE or PROD)")
    parser.add_argument("--repo_path", default="./src", help="Path to the source repository")
    
    args = parser.parse_args()

    print(f"\n=== Fabric CI/CD Deployment ===")
    print(f"Target:      {args.workspace_id}")
    print(f"Environment: {args.environment}")
    print(f"Scope:       Lakehouse, Notebook")

    # 1. Initialize Workspace
    # We explicitly define item_type_in_scope to strictly maintain only your design items.
    # The 'environment' arg triggers the parameter.yml processing.
    workspace = FabricWorkspace(
        workspace_id=args.workspace_id,
        repository_directory=args.repo_path,
        environment=args.environment,
        item_type_in_scope=["Lakehouse", "Notebook"]
    )

    # 2. Publish Items
    # The library will:
    #   1. Deploy the Lakehouse first (dependency resolution).
    #   2. Get the new Lakehouse ID.
    #   3. Update the Notebook's "default_lakehouse" ID using the parameter.yml rule.
    #   4. Deploy the Notebook and Semantic Model.
    publish_all_items(workspace)

    print("\n=== Deployment Successful ===")

if __name__ == "__main__":
    main()