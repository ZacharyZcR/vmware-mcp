"""VMware MCP Server - Complete implementation with REST API, vmcli, and vmrun."""

import json
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import VMwareClient
from .vmcli import VMCli
from .vmrun import VMRun

server = Server("vmware-mcp")
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


def get_vmrun() -> VMRun:
    return VMRun()


async def get_vmx_path(vm_id: str) -> str:
    if vm_id not in _vm_path_cache:
        client = get_client()
        vms = await client.list_vms()
        for vm in vms:
            _vm_path_cache[vm["id"]] = vm["path"]
    return _vm_path_cache.get(vm_id, "")


def T(name: str, desc: str, props: dict, required: list | None = None) -> Tool:
    """Helper to create Tool definitions."""
    schema = {"type": "object", "properties": props}
    if required:
        schema["required"] = required
    return Tool(name=name, description=desc, inputSchema=schema)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ==================== REST API ====================
        # VM Management
        T("vm_list", "List all VMs", {}),
        T("vm_get", "Get VM settings", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vm_create", "Clone a VM (REST)", {"vm_id": {"type": "string"}, "name": {"type": "string"}}, ["vm_id", "name"]),
        T("vm_delete", "Delete a VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vm_update", "Update VM settings", {"vm_id": {"type": "string"}, "cpu": {"type": "integer"}, "memory": {"type": "integer"}}, ["vm_id"]),
        # VM Power (REST)
        T("vm_power_get", "Get VM power state", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vm_power_set", "Change VM power state", {"vm_id": {"type": "string"}, "state": {"type": "string", "enum": ["on", "off", "shutdown", "suspend", "pause", "unpause"]}}, ["vm_id", "state"]),
        # VM Network Adapters
        T("vm_nic_list", "List VM network adapters", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vm_nic_create", "Create VM network adapter", {"vm_id": {"type": "string"}, "type": {"type": "string", "enum": ["bridged", "nat", "hostonly", "custom"]}}, ["vm_id", "type"]),
        T("vm_nic_delete", "Delete VM network adapter", {"vm_id": {"type": "string"}, "index": {"type": "integer"}}, ["vm_id", "index"]),
        T("vm_ip_get", "Get VM IP address (REST)", {"vm_id": {"type": "string"}}, ["vm_id"]),
        # VM Shared Folders
        T("vm_folder_list", "List VM shared folders", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vm_folder_create", "Create VM shared folder", {"vm_id": {"type": "string"}, "folder_id": {"type": "string"}, "host_path": {"type": "string"}, "flags": {"type": "integer"}}, ["vm_id", "folder_id", "host_path"]),
        T("vm_folder_delete", "Delete VM shared folder", {"vm_id": {"type": "string"}, "folder_id": {"type": "string"}}, ["vm_id", "folder_id"]),
        # Host Networks
        T("network_list", "List host virtual networks", {}),
        T("network_create", "Create host virtual network", {"name": {"type": "string"}, "type": {"type": "string", "enum": ["bridged", "nat", "hostonly"]}}, ["name", "type"]),
        T("network_portforward_list", "List port forwards", {"vmnet": {"type": "string"}}, ["vmnet"]),
        T("network_portforward_set", "Set port forward", {"vmnet": {"type": "string"}, "protocol": {"type": "string", "enum": ["tcp", "udp"]}, "port": {"type": "integer"}, "guest_ip": {"type": "string"}, "guest_port": {"type": "integer"}}, ["vmnet", "protocol", "port", "guest_ip", "guest_port"]),
        T("network_portforward_delete", "Delete port forward", {"vmnet": {"type": "string"}, "protocol": {"type": "string"}, "port": {"type": "integer"}}, ["vmnet", "protocol", "port"]),

        # ==================== VMRUN ====================
        # General
        T("vmrun_list", "List all running VMs", {}),
        T("vmrun_clone", "Clone VM (full/linked)", {"vm_id": {"type": "string"}, "dest_path": {"type": "string"}, "clone_type": {"type": "string", "enum": ["full", "linked"]}, "snapshot": {"type": "string"}, "clone_name": {"type": "string"}}, ["vm_id", "dest_path"]),
        T("vmrun_upgrade", "Upgrade VM format", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vmrun_delete", "Delete VM (vmrun)", {"vm_id": {"type": "string"}}, ["vm_id"]),
        # Power (vmrun)
        T("vmrun_start", "Start VM", {"vm_id": {"type": "string"}, "gui": {"type": "boolean"}}, ["vm_id"]),
        T("vmrun_stop", "Stop VM", {"vm_id": {"type": "string"}, "hard": {"type": "boolean"}}, ["vm_id"]),
        T("vmrun_reset", "Reset VM", {"vm_id": {"type": "string"}, "hard": {"type": "boolean"}}, ["vm_id"]),
        T("vmrun_suspend", "Suspend VM", {"vm_id": {"type": "string"}, "hard": {"type": "boolean"}}, ["vm_id"]),
        T("vmrun_pause", "Pause VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vmrun_unpause", "Unpause VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        # Snapshot (vmrun)
        T("vmrun_snapshot_list", "List snapshots (tree)", {"vm_id": {"type": "string"}, "show_tree": {"type": "boolean"}}, ["vm_id"]),
        T("vmrun_snapshot_take", "Take snapshot", {"vm_id": {"type": "string"}, "name": {"type": "string"}}, ["vm_id", "name"]),
        T("vmrun_snapshot_delete", "Delete snapshot", {"vm_id": {"type": "string"}, "name": {"type": "string"}, "delete_children": {"type": "boolean"}}, ["vm_id", "name"]),
        T("vmrun_snapshot_revert", "Revert to snapshot", {"vm_id": {"type": "string"}, "name": {"type": "string"}}, ["vm_id", "name"]),
        # Guest File Operations
        T("vmrun_file_exists", "Check if file exists in guest", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("vmrun_dir_exists", "Check if directory exists in guest", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("vmrun_ls", "List directory in guest", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("vmrun_mkdir", "Create directory in guest", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("vmrun_rmdir", "Delete directory in guest", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("vmrun_rm", "Delete file in guest", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("vmrun_rename", "Rename file in guest", {"vm_id": {"type": "string"}, "old_path": {"type": "string"}, "new_path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "old_path", "new_path"]),
        T("vmrun_copy_to", "Copy file from host to guest", {"vm_id": {"type": "string"}, "host_path": {"type": "string"}, "guest_path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "host_path", "guest_path"]),
        T("vmrun_copy_from", "Copy file from guest to host", {"vm_id": {"type": "string"}, "guest_path": {"type": "string"}, "host_path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "guest_path", "host_path"]),
        T("vmrun_temp_file", "Create temp file in guest", {"vm_id": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id"]),
        # Guest Process
        T("vmrun_run", "Run program in guest", {"vm_id": {"type": "string"}, "program": {"type": "string"}, "args": {"type": "string"}, "no_wait": {"type": "boolean"}, "interactive": {"type": "boolean"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "program"]),
        T("vmrun_script", "Run script in guest", {"vm_id": {"type": "string"}, "interpreter": {"type": "string"}, "script": {"type": "string"}, "no_wait": {"type": "boolean"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "interpreter", "script"]),
        T("vmrun_ps", "List processes in guest", {"vm_id": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id"]),
        T("vmrun_kill", "Kill process in guest", {"vm_id": {"type": "string"}, "pid": {"type": "integer"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "pid"]),
        # Shared Folders (vmrun)
        T("vmrun_shared_enable", "Enable shared folders", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vmrun_shared_disable", "Disable shared folders", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vmrun_shared_add", "Add shared folder", {"vm_id": {"type": "string"}, "name": {"type": "string"}, "host_path": {"type": "string"}}, ["vm_id", "name", "host_path"]),
        T("vmrun_shared_remove", "Remove shared folder", {"vm_id": {"type": "string"}, "name": {"type": "string"}}, ["vm_id", "name"]),
        T("vmrun_shared_set", "Set shared folder state", {"vm_id": {"type": "string"}, "name": {"type": "string"}, "host_path": {"type": "string"}, "writable": {"type": "boolean"}}, ["vm_id", "name", "host_path"]),
        # Device
        T("vmrun_device_connect", "Connect device", {"vm_id": {"type": "string"}, "device": {"type": "string"}}, ["vm_id", "device"]),
        T("vmrun_device_disconnect", "Disconnect device", {"vm_id": {"type": "string"}, "device": {"type": "string"}}, ["vm_id", "device"]),
        # Variables
        T("vmrun_var_read", "Read VM variable", {"vm_id": {"type": "string"}, "var_type": {"type": "string", "enum": ["runtimeConfig", "guestEnv", "guestVar"]}, "name": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "var_type", "name"]),
        T("vmrun_var_write", "Write VM variable", {"vm_id": {"type": "string"}, "var_type": {"type": "string", "enum": ["runtimeConfig", "guestEnv", "guestVar"]}, "name": {"type": "string"}, "value": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "var_type", "name", "value"]),
        # Screen/Input
        T("vmrun_screenshot", "Capture VM screenshot", {"vm_id": {"type": "string"}, "output_path": {"type": "string"}}, ["vm_id", "output_path"]),
        T("vmrun_keystrokes", "Type keystrokes in guest", {"vm_id": {"type": "string"}, "keystrokes": {"type": "string"}}, ["vm_id", "keystrokes"]),
        # Tools/Network
        T("vmrun_tools_install", "Install VMware Tools", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vmrun_tools_state", "Check VMware Tools state", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vmrun_guest_ip", "Get guest IP address", {"vm_id": {"type": "string"}, "wait": {"type": "boolean"}}, ["vm_id"]),
        T("vmrun_host_networks", "List host networks", {}),
        T("vmrun_portforward_list", "List port forwardings", {"network": {"type": "string"}}, ["network"]),
        T("vmrun_portforward_set", "Set port forwarding", {"network": {"type": "string"}, "protocol": {"type": "string"}, "host_port": {"type": "integer"}, "guest_ip": {"type": "string"}, "guest_port": {"type": "integer"}, "description": {"type": "string"}}, ["network", "protocol", "host_port", "guest_ip", "guest_port"]),
        T("vmrun_portforward_delete", "Delete port forwarding", {"network": {"type": "string"}, "protocol": {"type": "string"}, "host_port": {"type": "integer"}}, ["network", "protocol", "host_port"]),

        # ==================== VMCLI ====================
        # Snapshot
        T("snapshot_list", "List snapshots (vmcli)", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("snapshot_take", "Take snapshot (vmcli)", {"vm_id": {"type": "string"}, "name": {"type": "string"}}, ["vm_id", "name"]),
        T("snapshot_revert", "Revert to snapshot (vmcli)", {"vm_id": {"type": "string"}, "name": {"type": "string"}}, ["vm_id", "name"]),
        T("snapshot_delete", "Delete snapshot (vmcli)", {"vm_id": {"type": "string"}, "name": {"type": "string"}, "delete_children": {"type": "boolean"}}, ["vm_id", "name"]),
        T("snapshot_clone", "Clone from snapshot", {"vm_id": {"type": "string"}, "snapshot_name": {"type": "string"}, "dest_path": {"type": "string"}, "clone_type": {"type": "string", "enum": ["linked", "full"]}}, ["vm_id", "snapshot_name", "dest_path"]),
        # Guest
        T("guest_run", "Run program in guest", {"vm_id": {"type": "string"}, "program": {"type": "string"}, "args": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "program"]),
        T("guest_ps", "List processes", {"vm_id": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id"]),
        T("guest_kill", "Kill process", {"vm_id": {"type": "string"}, "pid": {"type": "integer"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "pid"]),
        T("guest_ls", "List files", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("guest_mkdir", "Create directory", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("guest_rm", "Delete file", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("guest_rmdir", "Delete directory", {"vm_id": {"type": "string"}, "path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "path"]),
        T("guest_copy_to", "Copy to guest", {"vm_id": {"type": "string"}, "host_path": {"type": "string"}, "guest_path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "host_path", "guest_path"]),
        T("guest_copy_from", "Copy from guest", {"vm_id": {"type": "string"}, "guest_path": {"type": "string"}, "host_path": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id", "guest_path", "host_path"]),
        T("guest_env", "Get environment", {"vm_id": {"type": "string"}, "user": {"type": "string"}, "password": {"type": "string"}}, ["vm_id"]),
        # MKS
        T("mks_screenshot", "Capture screenshot", {"vm_id": {"type": "string"}, "output_path": {"type": "string"}}, ["vm_id", "output_path"]),
        T("mks_send_key", "Send key sequence", {"vm_id": {"type": "string"}, "key_sequence": {"type": "string"}}, ["vm_id", "key_sequence"]),
        T("mks_query", "Query MKS state", {"vm_id": {"type": "string"}}, ["vm_id"]),
        # Chipset
        T("chipset_query", "Query chipset config", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("chipset_set_cpu", "Set CPU count", {"vm_id": {"type": "string"}, "count": {"type": "integer"}}, ["vm_id", "count"]),
        T("chipset_set_memory", "Set memory (MB)", {"vm_id": {"type": "string"}, "size_mb": {"type": "integer"}}, ["vm_id", "size_mb"]),
        T("chipset_set_cores", "Set cores per socket", {"vm_id": {"type": "string"}, "cores": {"type": "integer"}}, ["vm_id", "cores"]),
        # Tools
        T("tools_query", "Query Tools status", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("tools_install", "Install Tools", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("tools_upgrade", "Upgrade Tools", {"vm_id": {"type": "string"}}, ["vm_id"]),
        # Template
        T("template_create", "Create template", {"vm_id": {"type": "string"}, "template_path": {"type": "string"}, "name": {"type": "string"}}, ["vm_id", "template_path", "name"]),
        T("template_deploy", "Deploy template", {"template_path": {"type": "string"}, "dest_path": {"type": "string"}, "name": {"type": "string"}}, ["template_path", "dest_path", "name"]),
        # Disk
        T("disk_query", "Query disk config", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("disk_create", "Create disk", {"vm_id": {"type": "string"}, "size_gb": {"type": "integer"}, "disk_type": {"type": "string"}, "adapter": {"type": "integer"}, "device": {"type": "integer"}}, ["vm_id", "size_gb"]),
        T("disk_extend", "Extend disk", {"vm_id": {"type": "string"}, "new_size_gb": {"type": "integer"}, "adapter": {"type": "integer"}, "device": {"type": "integer"}}, ["vm_id", "new_size_gb"]),
        # Config
        T("config_query", "Query config params", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("config_set", "Set config param", {"vm_id": {"type": "string"}, "key": {"type": "string"}, "value": {"type": "string"}}, ["vm_id", "key", "value"]),
        # Power (vmcli)
        T("power_query", "Query power state", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("power_start", "Start VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("power_stop", "Stop VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("power_pause", "Pause VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("power_unpause", "Unpause VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("power_reset", "Reset VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("power_suspend", "Suspend VM", {"vm_id": {"type": "string"}}, ["vm_id"]),
        # Ethernet
        T("ethernet_query", "Query ethernet config", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("ethernet_set_type", "Set connection type", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "type": {"type": "string", "enum": ["bridged", "nat", "hostonly", "custom"]}}, ["vm_id", "index", "type"]),
        T("ethernet_set_present", "Set ethernet present", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "present": {"type": "boolean"}}, ["vm_id", "index", "present"]),
        T("ethernet_set_connected", "Set start connected", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "connected": {"type": "boolean"}}, ["vm_id", "index", "connected"]),
        T("ethernet_set_device", "Set virtual device", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "device": {"type": "string"}}, ["vm_id", "index", "device"]),
        T("ethernet_set_network", "Set network name", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "name": {"type": "string"}}, ["vm_id", "index", "name"]),
        T("ethernet_purge", "Remove ethernet adapter", {"vm_id": {"type": "string"}, "index": {"type": "integer"}}, ["vm_id", "index"]),
        # HGFS
        T("hgfs_query", "Query shared folders", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("hgfs_set_enabled", "Enable/disable share", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "enabled": {"type": "boolean"}}, ["vm_id", "index", "enabled"]),
        T("hgfs_set_path", "Set host path", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "path": {"type": "string"}}, ["vm_id", "index", "path"]),
        T("hgfs_set_name", "Set guest name", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "name": {"type": "string"}}, ["vm_id", "index", "name"]),
        T("hgfs_set_read", "Set read access", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "read": {"type": "boolean"}}, ["vm_id", "index", "read"]),
        T("hgfs_set_write", "Set write access", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "write": {"type": "boolean"}}, ["vm_id", "index", "write"]),
        # Serial
        T("serial_query", "Query serial ports", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("serial_set_present", "Set serial present", {"vm_id": {"type": "string"}, "index": {"type": "integer"}, "present": {"type": "boolean"}}, ["vm_id", "index", "present"]),
        T("serial_purge", "Remove serial port", {"vm_id": {"type": "string"}, "index": {"type": "integer"}}, ["vm_id", "index"]),
        # Sata
        T("sata_query", "Query SATA config", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("sata_set_present", "Set SATA present", {"vm_id": {"type": "string"}, "adapter": {"type": "integer"}, "present": {"type": "boolean"}}, ["vm_id", "adapter", "present"]),
        T("sata_purge", "Remove SATA adapter", {"vm_id": {"type": "string"}, "adapter": {"type": "integer"}}, ["vm_id", "adapter"]),
        # Nvme
        T("nvme_query", "Query NVMe config", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("nvme_set_present", "Set NVMe present", {"vm_id": {"type": "string"}, "adapter": {"type": "integer"}, "present": {"type": "boolean"}}, ["vm_id", "adapter", "present"]),
        T("nvme_purge", "Remove NVMe adapter", {"vm_id": {"type": "string"}, "adapter": {"type": "integer"}}, ["vm_id", "adapter"]),
        # VProbes
        T("vprobes_query", "Query VProbes", {"vm_id": {"type": "string"}}, ["vm_id"]),
        T("vprobes_enable", "Enable VProbes", {"vm_id": {"type": "string"}, "enabled": {"type": "boolean"}}, ["vm_id", "enabled"]),
        T("vprobes_load", "Load VProbes script", {"vm_id": {"type": "string"}, "script_path": {"type": "string"}}, ["vm_id", "script_path"]),
        T("vprobes_reset", "Reset VProbes", {"vm_id": {"type": "string"}}, ["vm_id"]),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client = get_client()
    vmcli = get_vmcli()
    vmrun = get_vmrun()
    result = None
    a = arguments

    # Helper
    async def vmx(vm_id: str) -> str:
        return await get_vmx_path(vm_id)

    # ==================== REST API ====================
    if name == "vm_list":
        result = await client.list_vms()
        for vm in result:
            _vm_path_cache[vm["id"]] = vm["path"]
    elif name == "vm_get":
        result = await client.get_vm(a["vm_id"])
    elif name == "vm_create":
        result = await client.create_vm(a["vm_id"], a["name"])
    elif name == "vm_delete":
        await client.delete_vm(a["vm_id"])
        result = {"status": "deleted"}
    elif name == "vm_update":
        settings = {k: v for k, v in a.items() if k != "vm_id" and v is not None}
        result = await client.update_vm(a["vm_id"], settings)
    elif name == "vm_power_get":
        result = await client.get_power_state(a["vm_id"])
    elif name == "vm_power_set":
        result = await client.change_power_state(a["vm_id"], a["state"])
    elif name == "vm_nic_list":
        result = await client.list_nics(a["vm_id"])
    elif name == "vm_nic_create":
        result = await client.create_nic(a["vm_id"], {"type": a["type"]})
    elif name == "vm_nic_delete":
        await client.delete_nic(a["vm_id"], a["index"])
        result = {"status": "deleted"}
    elif name == "vm_ip_get":
        result = await client.get_vm_ip(a["vm_id"])
    elif name == "vm_folder_list":
        result = await client.list_shared_folders(a["vm_id"])
    elif name == "vm_folder_create":
        result = await client.create_shared_folder(a["vm_id"], {"folder_id": a["folder_id"], "host_path": a["host_path"], "flags": a.get("flags", 0)})
    elif name == "vm_folder_delete":
        await client.delete_shared_folder(a["vm_id"], a["folder_id"])
        result = {"status": "deleted"}
    elif name == "network_list":
        result = await client.list_networks()
    elif name == "network_create":
        result = await client.create_network({"name": a["name"], "type": a["type"]})
    elif name == "network_portforward_list":
        result = await client.get_portforwards(a["vmnet"])
    elif name == "network_portforward_set":
        result = await client.update_portforward(a["vmnet"], a["protocol"], a["port"], {"guestIp": a["guest_ip"], "guestPort": a["guest_port"]})
    elif name == "network_portforward_delete":
        await client.delete_portforward(a["vmnet"], a["protocol"], a["port"])
        result = {"status": "deleted"}

    # ==================== VMRUN ====================
    elif name == "vmrun_list":
        result = await vmrun.list_running()
    elif name == "vmrun_clone":
        result = await vmrun.clone(await vmx(a["vm_id"]), a["dest_path"], a.get("clone_type", "linked"), a.get("snapshot", ""), a.get("clone_name", ""))
    elif name == "vmrun_upgrade":
        result = await vmrun.upgrade_vm(await vmx(a["vm_id"]))
    elif name == "vmrun_delete":
        result = await vmrun.delete_vm(await vmx(a["vm_id"]))
    elif name == "vmrun_start":
        result = await vmrun.start(await vmx(a["vm_id"]), a.get("gui", True))
    elif name == "vmrun_stop":
        result = await vmrun.stop(await vmx(a["vm_id"]), a.get("hard", False))
    elif name == "vmrun_reset":
        result = await vmrun.reset(await vmx(a["vm_id"]), a.get("hard", False))
    elif name == "vmrun_suspend":
        result = await vmrun.suspend(await vmx(a["vm_id"]), a.get("hard", False))
    elif name == "vmrun_pause":
        result = await vmrun.pause(await vmx(a["vm_id"]))
    elif name == "vmrun_unpause":
        result = await vmrun.unpause(await vmx(a["vm_id"]))
    elif name == "vmrun_snapshot_list":
        result = await vmrun.list_snapshots(await vmx(a["vm_id"]), a.get("show_tree", False))
    elif name == "vmrun_snapshot_take":
        result = await vmrun.snapshot(await vmx(a["vm_id"]), a["name"])
    elif name == "vmrun_snapshot_delete":
        result = await vmrun.delete_snapshot(await vmx(a["vm_id"]), a["name"], a.get("delete_children", False))
    elif name == "vmrun_snapshot_revert":
        result = await vmrun.revert_to_snapshot(await vmx(a["vm_id"]), a["name"])
    elif name == "vmrun_file_exists":
        result = await vmrun.file_exists(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_dir_exists":
        result = await vmrun.directory_exists(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_ls":
        result = await vmrun.list_directory(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_mkdir":
        result = await vmrun.create_directory(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_rmdir":
        result = await vmrun.delete_directory(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_rm":
        result = await vmrun.delete_file(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_rename":
        result = await vmrun.rename_file(await vmx(a["vm_id"]), a["old_path"], a["new_path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_copy_to":
        result = await vmrun.copy_to_guest(await vmx(a["vm_id"]), a["host_path"], a["guest_path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_copy_from":
        result = await vmrun.copy_from_guest(await vmx(a["vm_id"]), a["guest_path"], a["host_path"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_temp_file":
        result = await vmrun.create_temp_file(await vmx(a["vm_id"]), a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_run":
        result = await vmrun.run_program(await vmx(a["vm_id"]), a["program"], a.get("args", ""), a.get("no_wait", False), False, a.get("interactive", False), a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_script":
        result = await vmrun.run_script(await vmx(a["vm_id"]), a["interpreter"], a["script"], a.get("no_wait", False), False, False, a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_ps":
        result = await vmrun.list_processes(await vmx(a["vm_id"]), a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_kill":
        result = await vmrun.kill_process(await vmx(a["vm_id"]), a["pid"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_shared_enable":
        result = await vmrun.enable_shared_folders(await vmx(a["vm_id"]))
    elif name == "vmrun_shared_disable":
        result = await vmrun.disable_shared_folders(await vmx(a["vm_id"]))
    elif name == "vmrun_shared_add":
        result = await vmrun.add_shared_folder(await vmx(a["vm_id"]), a["name"], a["host_path"])
    elif name == "vmrun_shared_remove":
        result = await vmrun.remove_shared_folder(await vmx(a["vm_id"]), a["name"])
    elif name == "vmrun_shared_set":
        result = await vmrun.set_shared_folder_state(await vmx(a["vm_id"]), a["name"], a["host_path"], a.get("writable", True))
    elif name == "vmrun_device_connect":
        result = await vmrun.connect_device(await vmx(a["vm_id"]), a["device"])
    elif name == "vmrun_device_disconnect":
        result = await vmrun.disconnect_device(await vmx(a["vm_id"]), a["device"])
    elif name == "vmrun_var_read":
        result = await vmrun.read_variable(await vmx(a["vm_id"]), a["var_type"], a["name"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_var_write":
        result = await vmrun.write_variable(await vmx(a["vm_id"]), a["var_type"], a["name"], a["value"], a.get("user", ""), a.get("password", ""))
    elif name == "vmrun_screenshot":
        result = await vmrun.capture_screen(await vmx(a["vm_id"]), a["output_path"])
    elif name == "vmrun_keystrokes":
        result = await vmrun.type_keystrokes(await vmx(a["vm_id"]), a["keystrokes"])
    elif name == "vmrun_tools_install":
        result = await vmrun.install_tools(await vmx(a["vm_id"]))
    elif name == "vmrun_tools_state":
        result = await vmrun.check_tools_state(await vmx(a["vm_id"]))
    elif name == "vmrun_guest_ip":
        result = await vmrun.get_guest_ip(await vmx(a["vm_id"]), a.get("wait", False))
    elif name == "vmrun_host_networks":
        result = await vmrun.list_host_networks()
    elif name == "vmrun_portforward_list":
        result = await vmrun.list_port_forwardings(a["network"])
    elif name == "vmrun_portforward_set":
        result = await vmrun.set_port_forwarding(a["network"], a["protocol"], a["host_port"], a["guest_ip"], a["guest_port"], a.get("description", ""))
    elif name == "vmrun_portforward_delete":
        result = await vmrun.delete_port_forwarding(a["network"], a["protocol"], a["host_port"])

    # ==================== VMCLI ====================
    elif name == "snapshot_list":
        result = await vmcli.snapshot_list(await vmx(a["vm_id"]))
    elif name == "snapshot_take":
        result = await vmcli.snapshot_take(await vmx(a["vm_id"]), a["name"])
    elif name == "snapshot_revert":
        result = await vmcli.snapshot_revert(await vmx(a["vm_id"]), a["name"])
    elif name == "snapshot_delete":
        result = await vmcli.snapshot_delete(await vmx(a["vm_id"]), a["name"], a.get("delete_children", False))
    elif name == "snapshot_clone":
        result = await vmcli.snapshot_clone(await vmx(a["vm_id"]), a["snapshot_name"], a["dest_path"], a.get("clone_type", "linked"))
    elif name == "guest_run":
        result = await vmcli.guest_run(await vmx(a["vm_id"]), a["program"], a.get("args", ""), a.get("user", ""), a.get("password", ""))
    elif name == "guest_ps":
        result = await vmcli.guest_ps(await vmx(a["vm_id"]), a.get("user", ""), a.get("password", ""))
    elif name == "guest_kill":
        result = await vmcli.guest_kill(await vmx(a["vm_id"]), a["pid"], a.get("user", ""), a.get("password", ""))
    elif name == "guest_ls":
        result = await vmcli.guest_ls(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "guest_mkdir":
        result = await vmcli.guest_mkdir(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "guest_rm":
        result = await vmcli.guest_rm(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "guest_rmdir":
        result = await vmcli.guest_rmdir(await vmx(a["vm_id"]), a["path"], a.get("user", ""), a.get("password", ""))
    elif name == "guest_copy_to":
        result = await vmcli.guest_copy_to(await vmx(a["vm_id"]), a["host_path"], a["guest_path"], a.get("user", ""), a.get("password", ""))
    elif name == "guest_copy_from":
        result = await vmcli.guest_copy_from(await vmx(a["vm_id"]), a["guest_path"], a["host_path"], a.get("user", ""), a.get("password", ""))
    elif name == "guest_env":
        result = await vmcli.guest_env(await vmx(a["vm_id"]), a.get("user", ""), a.get("password", ""))
    elif name == "mks_screenshot":
        result = await vmcli.mks_screenshot(await vmx(a["vm_id"]), a["output_path"])
    elif name == "mks_send_key":
        result = await vmcli.mks_send_key(await vmx(a["vm_id"]), a["key_sequence"])
    elif name == "mks_query":
        result = await vmcli.mks_query(await vmx(a["vm_id"]))
    elif name == "chipset_query":
        result = await vmcli.chipset_query(await vmx(a["vm_id"]))
    elif name == "chipset_set_cpu":
        result = await vmcli.chipset_set_cpu(await vmx(a["vm_id"]), a["count"])
    elif name == "chipset_set_memory":
        result = await vmcli.chipset_set_memory(await vmx(a["vm_id"]), a["size_mb"])
    elif name == "chipset_set_cores":
        result = await vmcli.chipset_set_cores_per_socket(await vmx(a["vm_id"]), a["cores"])
    elif name == "tools_query":
        result = await vmcli.tools_query(await vmx(a["vm_id"]))
    elif name == "tools_install":
        result = await vmcli.tools_install(await vmx(a["vm_id"]))
    elif name == "tools_upgrade":
        result = await vmcli.tools_upgrade(await vmx(a["vm_id"]))
    elif name == "template_create":
        result = await vmcli.template_create(await vmx(a["vm_id"]), a["template_path"], a["name"])
    elif name == "template_deploy":
        result = await vmcli.template_deploy(a["template_path"], a["dest_path"], a["name"])
    elif name == "disk_query":
        result = await vmcli.disk_query(await vmx(a["vm_id"]))
    elif name == "disk_create":
        result = await vmcli.disk_create(await vmx(a["vm_id"]), a["size_gb"], a.get("disk_type", "scsi"), a.get("adapter", 0), a.get("device", 0))
    elif name == "disk_extend":
        result = await vmcli.disk_extend(await vmx(a["vm_id"]), a["new_size_gb"], a.get("adapter", 0), a.get("device", 0))
    elif name == "config_query":
        result = await vmcli.config_query(await vmx(a["vm_id"]))
    elif name == "config_set":
        result = await vmcli.config_set(await vmx(a["vm_id"]), a["key"], a["value"])
    elif name == "power_query":
        result = await vmcli.power_query(await vmx(a["vm_id"]))
    elif name == "power_start":
        result = await vmcli.power_start(await vmx(a["vm_id"]))
    elif name == "power_stop":
        result = await vmcli.power_stop(await vmx(a["vm_id"]))
    elif name == "power_pause":
        result = await vmcli.power_pause(await vmx(a["vm_id"]))
    elif name == "power_unpause":
        result = await vmcli.power_unpause(await vmx(a["vm_id"]))
    elif name == "power_reset":
        result = await vmcli.power_reset(await vmx(a["vm_id"]))
    elif name == "power_suspend":
        result = await vmcli.power_suspend(await vmx(a["vm_id"]))
    elif name == "ethernet_query":
        result = await vmcli.ethernet_query(await vmx(a["vm_id"]))
    elif name == "ethernet_set_type":
        result = await vmcli.ethernet_set_connection_type(await vmx(a["vm_id"]), a["index"], a["type"])
    elif name == "ethernet_set_present":
        result = await vmcli.ethernet_set_present(await vmx(a["vm_id"]), a["index"], a["present"])
    elif name == "ethernet_set_connected":
        result = await vmcli.ethernet_set_start_connected(await vmx(a["vm_id"]), a["index"], a["connected"])
    elif name == "ethernet_set_device":
        result = await vmcli.ethernet_set_virtual_device(await vmx(a["vm_id"]), a["index"], a["device"])
    elif name == "ethernet_set_network":
        result = await vmcli.ethernet_set_network_name(await vmx(a["vm_id"]), a["index"], a["name"])
    elif name == "ethernet_purge":
        result = await vmcli.ethernet_purge(await vmx(a["vm_id"]), a["index"])
    elif name == "hgfs_query":
        result = await vmcli.hgfs_query(await vmx(a["vm_id"]))
    elif name == "hgfs_set_enabled":
        result = await vmcli.hgfs_set_enabled(await vmx(a["vm_id"]), a["index"], a["enabled"])
    elif name == "hgfs_set_path":
        result = await vmcli.hgfs_set_host_path(await vmx(a["vm_id"]), a["index"], a["path"])
    elif name == "hgfs_set_name":
        result = await vmcli.hgfs_set_guest_name(await vmx(a["vm_id"]), a["index"], a["name"])
    elif name == "hgfs_set_read":
        result = await vmcli.hgfs_set_read_access(await vmx(a["vm_id"]), a["index"], a["read"])
    elif name == "hgfs_set_write":
        result = await vmcli.hgfs_set_write_access(await vmx(a["vm_id"]), a["index"], a["write"])
    elif name == "serial_query":
        result = await vmcli.serial_query(await vmx(a["vm_id"]))
    elif name == "serial_set_present":
        result = await vmcli.serial_set_present(await vmx(a["vm_id"]), a["index"], a["present"])
    elif name == "serial_purge":
        result = await vmcli.serial_purge(await vmx(a["vm_id"]), a["index"])
    elif name == "sata_query":
        result = await vmcli.sata_query(await vmx(a["vm_id"]))
    elif name == "sata_set_present":
        result = await vmcli.sata_set_present(await vmx(a["vm_id"]), a["adapter"], a["present"])
    elif name == "sata_purge":
        result = await vmcli.sata_purge(await vmx(a["vm_id"]), a["adapter"])
    elif name == "nvme_query":
        result = await vmcli.nvme_query(await vmx(a["vm_id"]))
    elif name == "nvme_set_present":
        result = await vmcli.nvme_set_present(await vmx(a["vm_id"]), a["adapter"], a["present"])
    elif name == "nvme_purge":
        result = await vmcli.nvme_purge(await vmx(a["vm_id"]), a["adapter"])
    elif name == "vprobes_query":
        result = await vmcli.vprobes_query(await vmx(a["vm_id"]))
    elif name == "vprobes_enable":
        result = await vmcli.vprobes_set_enabled(await vmx(a["vm_id"]), a["enabled"])
    elif name == "vprobes_load":
        result = await vmcli.vprobes_load(await vmx(a["vm_id"]), a["script_path"])
    elif name == "vprobes_reset":
        result = await vmcli.vprobes_reset(await vmx(a["vm_id"]))

    if isinstance(result, str):
        return [TextContent(type="text", text=result if result else "OK")]
    return [TextContent(type="text", text=json.dumps(result, indent=2) if result else "OK")]


def main():
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
