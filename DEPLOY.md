# Deployment Workflow

This project uses a **semi-automated** deployment workflow. You initiate the deployment manually from your local machine, and the script handles the rest (Git Push -> Server Pull -> Server Rebuild).

## How to Deploy

To deploy your latest changes to the production server:

1.  **Commit your changes** locally.
2.  Run the deployment script from the project root:

    ```bash
    python deploy.py
    ```

3.  **Follow the prompts**:
    - The script will warn you if there are uncommitted changes.
    - It automates the `git push`.
    - It connects to the server via SSH (alias `forex`).
    - It pulls the changes on the server.
    - It performs a **full rebuild** (`docker compose up -d --build`) to ensure code changes are applied.
    - It runs a brief health check.

## Prerequisites

- SSH alias `forex` configured in `~/.ssh/config`.
- SSH Key authorized on the server.
- Python dependencies installed locally.

## Troubleshooting

If deployment fails:
- Run `python execution/tools/troubleshoot_server.py` for a deep health check.
- Run `python execution/tools/remote_ops.py logs` to check container logs.
