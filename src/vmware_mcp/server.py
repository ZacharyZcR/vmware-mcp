"""VMware MCP Server - Core server implementation."""

import json
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import VMwareClient

server = Server("vmware-mcp")

def get_client() -> VMwareClient:
    return VMwareClient(
        host=os.getenv("VMWARE_HOST", "localhost"),
        port=int(os.getenv("VMWARE_PORT", "8697")),
        username=os.getenv("VMWARE_USERNAME", ""),
        password=os.getenv("VMWARE_PASSWORD", ""),
    )


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # VM Management
        Tool(name="vm_list", description="List all VMs", inputSchema={"type": "object", "properties": {}}),
        Tool(name="vm_get", description="Get VM settings", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="vm_create", description="Clone a VM", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "name": {"type": "string"}}, "required": ["vm_id", "name"]
        }),
        Tool(name="vm_delete", description="Delete a VM", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="vm_update", description="Update VM settings", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "cpu": {"type": "integer"}, "memory": {"type": "integer"}}, "required": ["vm_id"]
        }),
        # VM Power
        Tool(name="vm_power_get", description="Get VM power state", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="vm_power_set", description="Change VM power state (on/off/shutdown/suspend/pause/unpause)", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "state": {"type": "string", "enum": ["on", "off", "shutdown", "suspend", "pause", "unpause"]}}, "required": ["vm_id", "state"]
        }),
        # VM Network Adapters
        Tool(name="vm_nic_list", description="List VM network adapters", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="vm_nic_create", description="Create VM network adapter", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "type": {"type": "string", "enum": ["bridged", "nat", "hostonly", "custom"]}}, "required": ["vm_id", "type"]
        }),
        Tool(name="vm_nic_delete", description="Delete VM network adapter", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "index": {"type": "integer"}}, "required": ["vm_id", "index"]
        }),
        Tool(name="vm_ip_get", description="Get VM IP address", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        # VM Shared Folders
        Tool(name="vm_folder_list", description="List VM shared folders", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="vm_folder_create", description="Create VM shared folder", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "folder_id": {"type": "string"}, "host_path": {"type": "string"}, "flags": {"type": "integer"}}, "required": ["vm_id", "folder_id", "host_path"]
        }),
        Tool(name="vm_folder_delete", description="Delete VM shared folder", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "folder_id": {"type": "string"}}, "required": ["vm_id", "folder_id"]
        }),
        # Host Networks
        Tool(name="network_list", description="List host virtual networks", inputSchema={"type": "object", "properties": {}}),
        Tool(name="network_create", description="Create host virtual network", inputSchema={
            "type": "object", "properties": {"name": {"type": "string"}, "type": {"type": "string", "enum": ["bridged", "nat", "hostonly"]}}, "required": ["name", "type"]
        }),
        Tool(name="network_portforward_list", description="List port forwards for a network", inputSchema={
            "type": "object", "properties": {"vmnet": {"type": "string"}}, "required": ["vmnet"]
        }),
        Tool(name="network_portforward_set", description="Set port forward", inputSchema={
            "type": "object", "properties": {"vmnet": {"type": "string"}, "protocol": {"type": "string", "enum": ["tcp", "udp"]}, "port": {"type": "integer"}, "guest_ip": {"type": "string"}, "guest_port": {"type": "integer"}}, "required": ["vmnet", "protocol", "port", "guest_ip", "guest_port"]
        }),
        Tool(name="network_portforward_delete", description="Delete port forward", inputSchema={
            "type": "object", "properties": {"vmnet": {"type": "string"}, "protocol": {"type": "string"}, "port": {"type": "integer"}}, "required": ["vmnet", "protocol", "port"]
        }),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client = get_client()
    result = None

    # VM Management
    if name == "vm_list":
        result = await client.list_vms()
    elif name == "vm_get":
        result = await client.get_vm(arguments["vm_id"])
    elif name == "vm_create":
        result = await client.create_vm(arguments["vm_id"], arguments["name"])
    elif name == "vm_delete":
        await client.delete_vm(arguments["vm_id"])
        result = {"status": "deleted"}
    elif name == "vm_update":
        settings = {k: v for k, v in arguments.items() if k != "vm_id" and v is not None}
        result = await client.update_vm(arguments["vm_id"], settings)

    # VM Power
    elif name == "vm_power_get":
        result = await client.get_power_state(arguments["vm_id"])
    elif name == "vm_power_set":
        result = await client.change_power_state(arguments["vm_id"], arguments["state"])

    # VM Network Adapters
    elif name == "vm_nic_list":
        result = await client.list_nics(arguments["vm_id"])
    elif name == "vm_nic_create":
        result = await client.create_nic(arguments["vm_id"], {"type": arguments["type"]})
    elif name == "vm_nic_delete":
        await client.delete_nic(arguments["vm_id"], arguments["index"])
        result = {"status": "deleted"}
    elif name == "vm_ip_get":
        result = await client.get_vm_ip(arguments["vm_id"])

    # VM Shared Folders
    elif name == "vm_folder_list":
        result = await client.list_shared_folders(arguments["vm_id"])
    elif name == "vm_folder_create":
        config = {"folder_id": arguments["folder_id"], "host_path": arguments["host_path"], "flags": arguments.get("flags", 0)}
        result = await client.create_shared_folder(arguments["vm_id"], config)
    elif name == "vm_folder_delete":
        await client.delete_shared_folder(arguments["vm_id"], arguments["folder_id"])
        result = {"status": "deleted"}

    # Host Networks
    elif name == "network_list":
        result = await client.list_networks()
    elif name == "network_create":
        result = await client.create_network({"name": arguments["name"], "type": arguments["type"]})
    elif name == "network_portforward_list":
        result = await client.get_portforwards(arguments["vmnet"])
    elif name == "network_portforward_set":
        config = {"guestIp": arguments["guest_ip"], "guestPort": arguments["guest_port"]}
        result = await client.update_portforward(arguments["vmnet"], arguments["protocol"], arguments["port"], config)
    elif name == "network_portforward_delete":
        await client.delete_portforward(arguments["vmnet"], arguments["protocol"], arguments["port"])
        result = {"status": "deleted"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def main():
    """Entry point for the MCP server."""
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
