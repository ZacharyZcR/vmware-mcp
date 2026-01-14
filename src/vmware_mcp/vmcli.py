"""VMware vmcli command line wrapper."""

import asyncio
import os
import json
from typing import Any


class VMCli:
    """Wrapper for vmcli command line tool."""

    def __init__(self, vmcli_path: str | None = None):
        self.vmcli_path = vmcli_path or os.getenv(
            "VMCLI_PATH",
            r"C:\Program Files (x86)\VMware\VMware Workstation\vmcli.exe"
        )

    async def _run(self, vmx_path: str | None, module: str, command: str, *args: str) -> str:
        cmd = [self.vmcli_path]
        if vmx_path:
            cmd.append(vmx_path)
        cmd.extend([module, command])
        cmd.extend(args)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"vmcli failed: {error_msg}")

        return stdout.decode("utf-8", errors="replace").strip()

    # === Snapshot ===
    async def snapshot_list(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Snapshot", "query")

    async def snapshot_take(self, vmx_path: str, name: str) -> str:
        return await self._run(vmx_path, "Snapshot", "Take", "-n", name)

    async def snapshot_revert(self, vmx_path: str, name: str) -> str:
        return await self._run(vmx_path, "Snapshot", "Revert", "-n", name)

    async def snapshot_delete(self, vmx_path: str, name: str, delete_children: bool = False) -> str:
        args = ["-n", name]
        if delete_children:
            args.append("--andDeleteChildren")
        return await self._run(vmx_path, "Snapshot", "Delete", *args)

    async def snapshot_clone(self, vmx_path: str, snapshot_name: str, dest_path: str, clone_type: str = "linked") -> str:
        return await self._run(vmx_path, "Snapshot", "Clone", "-n", snapshot_name, "-p", dest_path, "-t", clone_type)

    # === Guest Operations ===
    async def guest_run(self, vmx_path: str, program: str, args: str = "", user: str = "", password: str = "") -> str:
        cmd_args = ["-p", program]
        if args:
            cmd_args.extend(["-a", args])
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "run", *cmd_args)

    async def guest_ps(self, vmx_path: str, user: str = "", password: str = "") -> str:
        cmd_args = []
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "ps", *cmd_args)

    async def guest_kill(self, vmx_path: str, pid: int, user: str = "", password: str = "") -> str:
        cmd_args = ["--pid", str(pid)]
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "kill", *cmd_args)

    async def guest_ls(self, vmx_path: str, path: str, user: str = "", password: str = "") -> str:
        cmd_args = ["-d", path]
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "ls", *cmd_args)

    async def guest_mkdir(self, vmx_path: str, path: str, user: str = "", password: str = "") -> str:
        cmd_args = ["-d", path]
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "mkdir", *cmd_args)

    async def guest_rm(self, vmx_path: str, path: str, user: str = "", password: str = "") -> str:
        cmd_args = ["-f", path]
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "rm", *cmd_args)

    async def guest_rmdir(self, vmx_path: str, path: str, user: str = "", password: str = "") -> str:
        cmd_args = ["-d", path]
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "rmdir", *cmd_args)

    async def guest_copy_to(self, vmx_path: str, host_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        cmd_args = ["-l", host_path, "-r", guest_path]
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "copyTo", *cmd_args)

    async def guest_copy_from(self, vmx_path: str, guest_path: str, host_path: str, user: str = "", password: str = "") -> str:
        cmd_args = ["-r", guest_path, "-l", host_path]
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "copyFrom", *cmd_args)

    async def guest_env(self, vmx_path: str, user: str = "", password: str = "") -> str:
        cmd_args = []
        if user:
            cmd_args.extend(["-u", user])
        if password:
            cmd_args.extend(["-P", password])
        return await self._run(vmx_path, "Guest", "env", *cmd_args)

    # === MKS (Mouse, Keyboard, Screen) ===
    async def mks_screenshot(self, vmx_path: str, output_path: str) -> str:
        return await self._run(vmx_path, "MKS", "captureScreenshot", "-o", output_path)

    async def mks_send_key(self, vmx_path: str, key_sequence: str) -> str:
        return await self._run(vmx_path, "MKS", "sendKeySequence", "-s", key_sequence)

    async def mks_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "MKS", "query")

    # === Chipset (CPU/Memory) ===
    async def chipset_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Chipset", "query")

    async def chipset_set_cpu(self, vmx_path: str, count: int) -> str:
        return await self._run(vmx_path, "Chipset", "SetVCpuCount", "-c", str(count))

    async def chipset_set_memory(self, vmx_path: str, size_mb: int) -> str:
        return await self._run(vmx_path, "Chipset", "SetMemSize", "-s", str(size_mb))

    async def chipset_set_cores_per_socket(self, vmx_path: str, cores: int) -> str:
        return await self._run(vmx_path, "Chipset", "SetCoresPerSocket", "-c", str(cores))

    # === Tools ===
    async def tools_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Tools", "Query")

    async def tools_install(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Tools", "Install")

    async def tools_upgrade(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Tools", "Upgrade")

    # === VMTemplate ===
    async def template_create(self, vmx_path: str, template_path: str, name: str) -> str:
        return await self._run(vmx_path, "VMTemplate", "Create", "-p", template_path, "-n", name)

    async def template_deploy(self, template_path: str, dest_path: str, name: str) -> str:
        return await self._run(None, "VMTemplate", "Deploy", "-p", template_path, "-d", dest_path, "-n", name)

    # === Disk ===
    async def disk_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Disk", "query")

    async def disk_create(self, vmx_path: str, size_gb: int, disk_type: str = "scsi", adapter: int = 0, device: int = 0) -> str:
        return await self._run(vmx_path, "Disk", "Create", "-s", str(size_gb), "-t", disk_type, "-a", str(adapter), "-d", str(device))

    async def disk_extend(self, vmx_path: str, new_size_gb: int, adapter: int = 0, device: int = 0) -> str:
        return await self._run(vmx_path, "Disk", "Extend", "-s", str(new_size_gb), "-a", str(adapter), "-d", str(device))

    # === VM ===
    async def vm_create(self, name: str, dest_dir: str, guest_os: str) -> str:
        return await self._run(None, "VM", "Create", "-n", name, "-d", dest_dir, "-g", guest_os)

    # === ConfigParams ===
    async def config_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "ConfigParams", "query")

    async def config_set(self, vmx_path: str, key: str, value: str) -> str:
        return await self._run(vmx_path, "ConfigParams", "SetEntry", "-k", key, "-v", value)

    # === Power ===
    async def power_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Power", "query")

    async def power_start(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Power", "Start")

    async def power_stop(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Power", "Stop")

    async def power_pause(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Power", "Pause")

    async def power_unpause(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Power", "Unpause")

    async def power_reset(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Power", "Reset")

    async def power_suspend(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Power", "Suspend")

    # === Ethernet ===
    async def ethernet_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Ethernet", "query")

    async def ethernet_set_connection_type(self, vmx_path: str, index: int, conn_type: str) -> str:
        return await self._run(vmx_path, "Ethernet", "SetConnectionType", "-i", str(index), "-t", conn_type)

    async def ethernet_set_present(self, vmx_path: str, index: int, present: bool) -> str:
        return await self._run(vmx_path, "Ethernet", "SetPresent", "-i", str(index), "-e", "true" if present else "false")

    async def ethernet_set_start_connected(self, vmx_path: str, index: int, connected: bool) -> str:
        return await self._run(vmx_path, "Ethernet", "SetStartConnected", "-i", str(index), "-e", "true" if connected else "false")

    async def ethernet_set_virtual_device(self, vmx_path: str, index: int, device: str) -> str:
        return await self._run(vmx_path, "Ethernet", "SetVirtualDevice", "-i", str(index), "-d", device)

    async def ethernet_set_network_name(self, vmx_path: str, index: int, name: str) -> str:
        return await self._run(vmx_path, "Ethernet", "SetNetworkName", "-i", str(index), "-n", name)

    async def ethernet_purge(self, vmx_path: str, index: int) -> str:
        return await self._run(vmx_path, "Ethernet", "Purge", "-i", str(index))

    # === HGFS (Shared Folders) ===
    async def hgfs_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "HGFS", "query")

    async def hgfs_set_enabled(self, vmx_path: str, index: int, enabled: bool) -> str:
        return await self._run(vmx_path, "HGFS", "SetEnabled", "-i", str(index), "-e", "true" if enabled else "false")

    async def hgfs_set_host_path(self, vmx_path: str, index: int, path: str) -> str:
        return await self._run(vmx_path, "HGFS", "SetHostPath", "-i", str(index), "-p", path)

    async def hgfs_set_guest_name(self, vmx_path: str, index: int, name: str) -> str:
        return await self._run(vmx_path, "HGFS", "SetGuestName", "-i", str(index), "-n", name)

    async def hgfs_set_present(self, vmx_path: str, index: int, present: bool) -> str:
        return await self._run(vmx_path, "HGFS", "SetPresent", "-i", str(index), "-e", "true" if present else "false")

    async def hgfs_set_read_access(self, vmx_path: str, index: int, read: bool) -> str:
        return await self._run(vmx_path, "HGFS", "SetReadAccess", "-i", str(index), "-e", "true" if read else "false")

    async def hgfs_set_write_access(self, vmx_path: str, index: int, write: bool) -> str:
        return await self._run(vmx_path, "HGFS", "SetWriteAccess", "-i", str(index), "-e", "true" if write else "false")

    # === Serial ===
    async def serial_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Serial", "Query")

    async def serial_set_present(self, vmx_path: str, index: int, present: bool) -> str:
        return await self._run(vmx_path, "Serial", "SetPresent", "-i", str(index), "-e", "true" if present else "false")

    async def serial_purge(self, vmx_path: str, index: int) -> str:
        return await self._run(vmx_path, "Serial", "Purge", "-i", str(index))

    # === Sata ===
    async def sata_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Sata", "query")

    async def sata_set_present(self, vmx_path: str, adapter: int, present: bool) -> str:
        return await self._run(vmx_path, "Sata", "SetPresent", "-a", str(adapter), "-e", "true" if present else "false")

    async def sata_purge(self, vmx_path: str, adapter: int) -> str:
        return await self._run(vmx_path, "Sata", "Purge", "-a", str(adapter))

    # === Nvme ===
    async def nvme_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "Nvme", "query")

    async def nvme_set_present(self, vmx_path: str, adapter: int, present: bool) -> str:
        return await self._run(vmx_path, "Nvme", "SetPresent", "-a", str(adapter), "-e", "true" if present else "false")

    async def nvme_purge(self, vmx_path: str, adapter: int) -> str:
        return await self._run(vmx_path, "Nvme", "Purge", "-a", str(adapter))

    # === VProbes ===
    async def vprobes_query(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "VProbes", "Query")

    async def vprobes_set_enabled(self, vmx_path: str, enabled: bool) -> str:
        return await self._run(vmx_path, "VProbes", "SetEnabled", "-e", "true" if enabled else "false")

    async def vprobes_load(self, vmx_path: str, script_path: str) -> str:
        return await self._run(vmx_path, "VProbes", "Load", "-s", script_path)

    async def vprobes_reset(self, vmx_path: str) -> str:
        return await self._run(vmx_path, "VProbes", "Reset")
