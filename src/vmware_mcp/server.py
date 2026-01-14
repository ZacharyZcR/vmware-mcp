"""VMware MCP Server - Core server implementation."""

import json
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import VMwareClient
from .vmcli import VMCli

server = Server("vmware-mcp")

# VM path cache: vm_id -> vmx_path
_vm_path_cache: dict[str, str] = {}


def get_client() -> VMwareClient:
    return VMwareClient(
        host=os.getenv("VMWARE_HOST", "localhost"),
        port=int(os.getenv("VMWARE_PORT", "8697")),
        username=os.getenv("VMWARE_USERNAME", ""),
        password=os.getenv("VMWARE_PASSWORD", ""),
    )


def get_vmcli() -> VMCli:
    return VMCli()


async def get_vmx_path(vm_id: str) -> str:
    """Get VMX path from VM ID, with caching."""
    if vm_id not in _vm_path_cache:
        client = get_client()
        vms = await client.list_vms()
        for vm in vms:
            _vm_path_cache[vm["id"]] = vm["path"]
    return _vm_path_cache.get(vm_id, "")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # === REST API Tools ===
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

        # === VMCLI Tools ===
        # Snapshot
        Tool(name="snapshot_list", description="List all snapshots of a VM", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="snapshot_take", description="Take a snapshot of a VM", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "name": {"type": "string"}}, "required": ["vm_id", "name"]
        }),
        Tool(name="snapshot_revert", description="Revert VM to a snapshot", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "name": {"type": "string"}}, "required": ["vm_id", "name"]
        }),
        Tool(name="snapshot_delete", description="Delete a snapshot", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "name": {"type": "string"}, "delete_children": {"type": "boolean"}}, "required": ["vm_id", "name"]
        }),
        Tool(name="snapshot_clone", description="Clone VM from a snapshot", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "snapshot_name": {"type": "string"}, "dest_path": {"type": "string"}, "clone_type": {"type": "string", "enum": ["linked", "full"]}}, "required": ["vm_id", "snapshot_name", "dest_path"]
        }),

        # Guest Operations
        Tool(name="guest_run", description="Run a program in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "program": {"type": "string"}, "args": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "program"]
        }),
        Tool(name="guest_ps", description="List processes in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="guest_kill", description="Kill a process in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "pid": {"type": "integer"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "pid"]
        }),
        Tool(name="guest_ls", description="List files in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "path"]
        }),
        Tool(name="guest_mkdir", description="Create directory in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "path"]
        }),
        Tool(name="guest_rm", description="Delete file in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "path"]
        }),
        Tool(name="guest_rmdir", description="Delete directory in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "path"]
        }),
        Tool(name="guest_copy_to", description="Copy file from host to guest", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "host_path": {"type": "string"}, "guest_path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "host_path", "guest_path"]
        }),
        Tool(name="guest_copy_from", description="Copy file from guest to host", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "guest_path": {"type": "string"}, "host_path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id", "guest_path", "host_path"]
        }),
        Tool(name="guest_env", description="Get environment variables in the guest OS", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, "required": ["vm_id"]
        }),

        # MKS (Screen/Keyboard)
        Tool(name="mks_screenshot", description="Capture screenshot of VM", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "output_path": {"type": "string"}}, "required": ["vm_id", "output_path"]
        }),
        Tool(name="mks_send_key", description="Send key sequence to VM", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "key_sequence": {"type": "string"}}, "required": ["vm_id", "key_sequence"]
        }),

        # Chipset (CPU/Memory)
        Tool(name="chipset_query", description="Query VM chipset configuration (CPU/Memory)", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="chipset_set_cpu", description="Set VM CPU count", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "count": {"type": "integer"}}, "required": ["vm_id", "count"]
        }),
        Tool(name="chipset_set_memory", description="Set VM memory size (MB)", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "size_mb": {"type": "integer"}}, "required": ["vm_id", "size_mb"]
        }),
        Tool(name="chipset_set_cores", description="Set cores per socket", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "cores": {"type": "integer"}}, "required": ["vm_id", "cores"]
        }),

        # VMware Tools
        Tool(name="tools_query", description="Query VMware Tools status", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="tools_install", description="Install VMware Tools", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="tools_upgrade", description="Upgrade VMware Tools", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),

        # VM Template
        Tool(name="template_create", description="Create VM template", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "template_path": {"type": "string"}, "name": {"type": "string"}}, "required": ["vm_id", "template_path", "name"]
        }),
        Tool(name="template_deploy", description="Deploy VM from template", inputSchema={
            "type": "object", "properties": {"template_path": {"type": "string"}, "dest_path": {"type": "string"}, "name": {"type": "string"}}, "required": ["template_path", "dest_path", "name"]
        }),

        # Disk
        Tool(name="disk_query", description="Query VM disk configuration", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="disk_create", description="Create a new disk for VM", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "size_gb": {"type": "integer"}, "disk_type": {"type": "string"}, "adapter": {"type": "integer"}, "device": {"type": "integer"}}, "required": ["vm_id", "size_gb"]
        }),
        Tool(name="disk_extend", description="Extend VM disk size", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "new_size_gb": {"type": "integer"}, "adapter": {"type": "integer"}, "device": {"type": "integer"}}, "required": ["vm_id", "new_size_gb"]
        }),

        # Config
        Tool(name="config_query", description="Query VM configuration parameters", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}}, "required": ["vm_id"]
        }),
        Tool(name="config_set", description="Set VM configuration parameter", inputSchema={
            "type": "object", "properties": {"vm_id": {"type": "string"}, "key": {"type": "string"}, "value": {"type": "string"}}, "required": ["vm_id", "key", "value"]
        }),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client = get_client()
    vmcli = get_vmcli()
    result = None

    # === REST API ===
    # VM Management
    if name == "vm_list":
        result = await client.list_vms()
        for vm in result:
            _vm_path_cache[vm["id"]] = vm["path"]
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

    # === VMCLI ===
    else:
        vmx_path = await get_vmx_path(arguments.get("vm_id", "")) if "vm_id" in arguments else ""

        # Snapshot
        if name == "snapshot_list":
            result = await vmcli.snapshot_list(vmx_path)
        elif name == "snapshot_take":
            result = await vmcli.snapshot_take(vmx_path, arguments["name"])
        elif name == "snapshot_revert":
            result = await vmcli.snapshot_revert(vmx_path, arguments["name"])
        elif name == "snapshot_delete":
            result = await vmcli.snapshot_delete(vmx_path, arguments["name"], arguments.get("delete_children", False))
        elif name == "snapshot_clone":
            result = await vmcli.snapshot_clone(vmx_path, arguments["snapshot_name"], arguments["dest_path"], arguments.get("clone_type", "linked"))

        # Guest Operations
        elif name == "guest_run":
            result = await vmcli.guest_run(vmx_path, arguments["program"], arguments.get("args", ""), arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_ps":
            result = await vmcli.guest_ps(vmx_path, arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_kill":
            result = await vmcli.guest_kill(vmx_path, arguments["pid"], arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_ls":
            result = await vmcli.guest_ls(vmx_path, arguments["path"], arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_mkdir":
            result = await vmcli.guest_mkdir(vmx_path, arguments["path"], arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_rm":
            result = await vmcli.guest_rm(vmx_path, arguments["path"], arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_rmdir":
            result = await vmcli.guest_rmdir(vmx_path, arguments["path"], arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_copy_to":
            result = await vmcli.guest_copy_to(vmx_path, arguments["host_path"], arguments["guest_path"], arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_copy_from":
            result = await vmcli.guest_copy_from(vmx_path, arguments["guest_path"], arguments["host_path"], arguments.get("user", ""), arguments.get("password", ""))
        elif name == "guest_env":
            result = await vmcli.guest_env(vmx_path, arguments.get("user", ""), arguments.get("password", ""))

        # MKS
        elif name == "mks_screenshot":
            result = await vmcli.mks_screenshot(vmx_path, arguments["output_path"])
        elif name == "mks_send_key":
            result = await vmcli.mks_send_key(vmx_path, arguments["key_sequence"])

        # Chipset
        elif name == "chipset_query":
            result = await vmcli.chipset_query(vmx_path)
        elif name == "chipset_set_cpu":
            result = await vmcli.chipset_set_cpu(vmx_path, arguments["count"])
        elif name == "chipset_set_memory":
            result = await vmcli.chipset_set_memory(vmx_path, arguments["size_mb"])
        elif name == "chipset_set_cores":
            result = await vmcli.chipset_set_cores_per_socket(vmx_path, arguments["cores"])

        # Tools
        elif name == "tools_query":
            result = await vmcli.tools_query(vmx_path)
        elif name == "tools_install":
            result = await vmcli.tools_install(vmx_path)
        elif name == "tools_upgrade":
            result = await vmcli.tools_upgrade(vmx_path)

        # Template
        elif name == "template_create":
            result = await vmcli.template_create(vmx_path, arguments["template_path"], arguments["name"])
        elif name == "template_deploy":
            result = await vmcli.template_deploy(arguments["template_path"], arguments["dest_path"], arguments["name"])

        # Disk
        elif name == "disk_query":
            result = await vmcli.disk_query(vmx_path)
        elif name == "disk_create":
            result = await vmcli.disk_create(vmx_path, arguments["size_gb"], arguments.get("disk_type", "scsi"), arguments.get("adapter", 0), arguments.get("device", 0))
        elif name == "disk_extend":
            result = await vmcli.disk_extend(vmx_path, arguments["new_size_gb"], arguments.get("adapter", 0), arguments.get("device", 0))

        # Config
        elif name == "config_query":
            result = await vmcli.config_query(vmx_path)
        elif name == "config_set":
            result = await vmcli.config_set(vmx_path, arguments["key"], arguments["value"])

    if isinstance(result, str):
        return [TextContent(type="text", text=result)]
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
