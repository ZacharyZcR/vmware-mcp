# VMware Workstation Pro MCP Server

MCP server for controlling VMware Workstation Pro virtual machines.

## Setup

```bash
pip install -e .
```

## Configuration

Set environment variables:
- `VMWARE_USERNAME` - vmrest username
- `VMWARE_PASSWORD` - vmrest password
- `VMWARE_HOST` - API host (default: localhost)
- `VMWARE_PORT` - API port (default: 8697)

## Usage with Claude Code

```bash
claude mcp add vmware-mcp -e VMWARE_USERNAME=xxx -e VMWARE_PASSWORD=xxx -- vmware-mcp
```
