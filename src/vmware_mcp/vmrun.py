"""VMware vmrun command line wrapper."""

import asyncio
import os


class VMRun:
    """Wrapper for vmrun command line tool."""

    def __init__(self, vmrun_path: str | None = None):
        self.vmrun_path = vmrun_path or os.getenv(
            "VMRUN_PATH",
            r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
        )

    async def _run(self, command: str, *args: str, guest_user: str = "", guest_pass: str = "") -> str:
        cmd = [self.vmrun_path, "-T", "ws"]
        if guest_user:
            cmd.extend(["-gu", guest_user])
        if guest_pass:
            cmd.extend(["-gp", guest_pass])
        cmd.append(command)
        cmd.extend(args)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            if not error_msg:
                error_msg = stdout.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"vmrun failed: {error_msg}")

        return stdout.decode("utf-8", errors="replace").strip()

    # === Power ===
    async def start(self, vmx_path: str, gui: bool = True) -> str:
        return await self._run("start", vmx_path, "gui" if gui else "nogui")

    async def stop(self, vmx_path: str, hard: bool = False) -> str:
        return await self._run("stop", vmx_path, "hard" if hard else "soft")

    async def reset(self, vmx_path: str, hard: bool = False) -> str:
        return await self._run("reset", vmx_path, "hard" if hard else "soft")

    async def suspend(self, vmx_path: str, hard: bool = False) -> str:
        return await self._run("suspend", vmx_path, "hard" if hard else "soft")

    async def pause(self, vmx_path: str) -> str:
        return await self._run("pause", vmx_path)

    async def unpause(self, vmx_path: str) -> str:
        return await self._run("unpause", vmx_path)

    # === General ===
    async def list_running(self) -> str:
        return await self._run("list")

    async def upgrade_vm(self, vmx_path: str) -> str:
        return await self._run("upgradevm", vmx_path)

    async def delete_vm(self, vmx_path: str) -> str:
        return await self._run("deleteVM", vmx_path)

    async def clone(self, vmx_path: str, dest_path: str, clone_type: str = "linked", snapshot: str = "", clone_name: str = "") -> str:
        args = [vmx_path, dest_path, clone_type]
        if snapshot:
            args.append(f"-snapshot={snapshot}")
        if clone_name:
            args.append(f"-cloneName={clone_name}")
        return await self._run("clone", *args)

    # === Snapshot ===
    async def list_snapshots(self, vmx_path: str, show_tree: bool = False) -> str:
        args = [vmx_path]
        if show_tree:
            args.append("showTree")
        return await self._run("listSnapshots", *args)

    async def snapshot(self, vmx_path: str, name: str) -> str:
        return await self._run("snapshot", vmx_path, name)

    async def delete_snapshot(self, vmx_path: str, name: str, delete_children: bool = False) -> str:
        args = [vmx_path, name]
        if delete_children:
            args.append("andDeleteChildren")
        return await self._run("deleteSnapshot", *args)

    async def revert_to_snapshot(self, vmx_path: str, name: str) -> str:
        return await self._run("revertToSnapshot", vmx_path, name)

    # === Guest File Operations ===
    async def file_exists(self, vmx_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        return await self._run("fileExistsInGuest", vmx_path, guest_path, guest_user=user, guest_pass=password)

    async def directory_exists(self, vmx_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        return await self._run("directoryExistsInGuest", vmx_path, guest_path, guest_user=user, guest_pass=password)

    async def rename_file(self, vmx_path: str, old_path: str, new_path: str, user: str = "", password: str = "") -> str:
        return await self._run("renameFileInGuest", vmx_path, old_path, new_path, guest_user=user, guest_pass=password)

    async def create_temp_file(self, vmx_path: str, user: str = "", password: str = "") -> str:
        return await self._run("CreateTempfileInGuest", vmx_path, guest_user=user, guest_pass=password)

    async def list_directory(self, vmx_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        return await self._run("listDirectoryInGuest", vmx_path, guest_path, guest_user=user, guest_pass=password)

    async def create_directory(self, vmx_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        return await self._run("createDirectoryInGuest", vmx_path, guest_path, guest_user=user, guest_pass=password)

    async def delete_directory(self, vmx_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        return await self._run("deleteDirectoryInGuest", vmx_path, guest_path, guest_user=user, guest_pass=password)

    async def delete_file(self, vmx_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        return await self._run("deleteFileInGuest", vmx_path, guest_path, guest_user=user, guest_pass=password)

    async def copy_to_guest(self, vmx_path: str, host_path: str, guest_path: str, user: str = "", password: str = "") -> str:
        return await self._run("CopyFileFromHostToGuest", vmx_path, host_path, guest_path, guest_user=user, guest_pass=password)

    async def copy_from_guest(self, vmx_path: str, guest_path: str, host_path: str, user: str = "", password: str = "") -> str:
        return await self._run("CopyFileFromGuestToHost", vmx_path, guest_path, host_path, guest_user=user, guest_pass=password)

    # === Guest Process Operations ===
    async def run_program(self, vmx_path: str, program: str, args: str = "", no_wait: bool = False, active_window: bool = False, interactive: bool = False, user: str = "", password: str = "") -> str:
        cmd_args = [vmx_path]
        if no_wait:
            cmd_args.append("-noWait")
        if active_window:
            cmd_args.append("-activeWindow")
        if interactive:
            cmd_args.append("-interactive")
        cmd_args.append(program)
        if args:
            cmd_args.extend(args.split())
        return await self._run("runProgramInGuest", *cmd_args, guest_user=user, guest_pass=password)

    async def run_script(self, vmx_path: str, interpreter: str, script: str, no_wait: bool = False, active_window: bool = False, interactive: bool = False, user: str = "", password: str = "") -> str:
        cmd_args = [vmx_path]
        if no_wait:
            cmd_args.append("-noWait")
        if active_window:
            cmd_args.append("-activeWindow")
        if interactive:
            cmd_args.append("-interactive")
        cmd_args.extend([interpreter, script])
        return await self._run("runScriptInGuest", *cmd_args, guest_user=user, guest_pass=password)

    async def list_processes(self, vmx_path: str, user: str = "", password: str = "") -> str:
        return await self._run("listProcessesInGuest", vmx_path, guest_user=user, guest_pass=password)

    async def kill_process(self, vmx_path: str, pid: int, user: str = "", password: str = "") -> str:
        return await self._run("killProcessInGuest", vmx_path, str(pid), guest_user=user, guest_pass=password)

    # === Shared Folders ===
    async def enable_shared_folders(self, vmx_path: str) -> str:
        return await self._run("enableSharedFolders", vmx_path)

    async def disable_shared_folders(self, vmx_path: str) -> str:
        return await self._run("disableSharedFolders", vmx_path)

    async def add_shared_folder(self, vmx_path: str, name: str, host_path: str) -> str:
        return await self._run("addSharedFolder", vmx_path, name, host_path)

    async def remove_shared_folder(self, vmx_path: str, name: str) -> str:
        return await self._run("removeSharedFolder", vmx_path, name)

    async def set_shared_folder_state(self, vmx_path: str, name: str, host_path: str, writable: bool = True) -> str:
        return await self._run("setSharedFolderState", vmx_path, name, host_path, "writable" if writable else "readonly")

    # === Device ===
    async def connect_device(self, vmx_path: str, device_name: str) -> str:
        return await self._run("connectNamedDevice", vmx_path, device_name)

    async def disconnect_device(self, vmx_path: str, device_name: str) -> str:
        return await self._run("disconnectNamedDevice", vmx_path, device_name)

    # === Variables ===
    async def read_variable(self, vmx_path: str, var_type: str, name: str, user: str = "", password: str = "") -> str:
        return await self._run("readVariable", vmx_path, var_type, name, guest_user=user, guest_pass=password)

    async def write_variable(self, vmx_path: str, var_type: str, name: str, value: str, user: str = "", password: str = "") -> str:
        return await self._run("writeVariable", vmx_path, var_type, name, value, guest_user=user, guest_pass=password)

    # === Screen/Input ===
    async def capture_screen(self, vmx_path: str, output_path: str) -> str:
        return await self._run("captureScreen", vmx_path, output_path)

    async def type_keystrokes(self, vmx_path: str, keystrokes: str) -> str:
        return await self._run("typeKeystrokesInGuest", vmx_path, keystrokes)

    # === Tools ===
    async def install_tools(self, vmx_path: str) -> str:
        return await self._run("installTools", vmx_path)

    async def check_tools_state(self, vmx_path: str) -> str:
        return await self._run("checkToolsState", vmx_path)

    # === Network ===
    async def get_guest_ip(self, vmx_path: str, wait: bool = False) -> str:
        args = [vmx_path]
        if wait:
            args.append("-wait")
        return await self._run("getGuestIPAddress", *args)

    async def list_host_networks(self) -> str:
        return await self._run("listHostNetworks")

    async def list_port_forwardings(self, network: str) -> str:
        return await self._run("listPortForwardings", network)

    async def set_port_forwarding(self, network: str, protocol: str, host_port: int, guest_ip: str, guest_port: int, description: str = "") -> str:
        args = [network, protocol, str(host_port), guest_ip, str(guest_port)]
        if description:
            args.append(description)
        return await self._run("setPortForwarding", *args)

    async def delete_port_forwarding(self, network: str, protocol: str, host_port: int) -> str:
        return await self._run("deletePortForwarding", network, protocol, str(host_port))
