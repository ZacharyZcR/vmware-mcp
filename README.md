# VMware Workstation Pro MCP Server

MCP server for controlling VMware Workstation Pro virtual machines via REST API, vmrun, and vmcli.

## Features

**117 tools** covering all VMware Workstation Pro automation capabilities:

| Source | Tools | Description |
|--------|-------|-------------|
| REST API | 20 | VM management, NICs, shared folders, port forwarding |
| vmrun | 54 | Power, snapshots, clone, guest file/process ops, devices |
| vmcli | 43 | Chipset, disk, ethernet, SATA, NVMe, serial, VProbes |

## Requirements

- VMware Workstation Pro 17+
- Python 3.10+
- vmrest running (`vmrest.exe` for REST API tools)

## Installation

```bash
git clone https://github.com/user/vmware-mcp.git
cd vmware-mcp
pip install -e .
```

## Configuration

Start vmrest service:
```bash
# First time setup
"C:\Program Files (x86)\VMware\VMware Workstation\vmrest.exe" -C

# Start service
"C:\Program Files (x86)\VMware\VMware Workstation\vmrest.exe"
```

Add to Claude Code:
```bash
claude mcp add vmware-mcp \
  -e VMWARE_USERNAME=your_username \
  -e VMWARE_PASSWORD=your_password \
  -- vmware-mcp
```

## Tools Reference

### REST API Tools
| Tool | Description |
|------|-------------|
| `vm_list` | List all VMs |
| `vm_get` | Get VM settings |
| `vm_create` | Clone a VM |
| `vm_delete` | Delete a VM |
| `vm_update` | Update VM CPU/memory |
| `vm_power_get` | Get power state |
| `vm_power_set` | Set power state (on/off/suspend/pause) |
| `vm_nic_list` | List network adapters |
| `vm_nic_create` | Create network adapter |
| `vm_nic_delete` | Delete network adapter |
| `vm_ip_get` | Get VM IP address |
| `vm_folder_list` | List shared folders |
| `vm_folder_create` | Create shared folder |
| `vm_folder_delete` | Delete shared folder |
| `network_list` | List virtual networks |
| `network_create` | Create virtual network |
| `network_portforward_list` | List port forwards |
| `network_portforward_set` | Set port forward |
| `network_portforward_delete` | Delete port forward |

### vmrun Tools
| Tool | Description |
|------|-------------|
| `vmrun_list` | List running VMs |
| `vmrun_start` | Start VM |
| `vmrun_stop` | Stop VM (soft/hard) |
| `vmrun_reset` | Reset VM |
| `vmrun_suspend` | Suspend VM |
| `vmrun_pause` | Pause VM |
| `vmrun_unpause` | Unpause VM |
| `vmrun_clone` | Clone VM (full/linked) |
| `vmrun_upgrade` | Upgrade VM format |
| `vmrun_delete` | Delete VM |
| `vmrun_snapshot_list` | List snapshots |
| `vmrun_snapshot_take` | Take snapshot |
| `vmrun_snapshot_delete` | Delete snapshot |
| `vmrun_snapshot_revert` | Revert to snapshot |
| `vmrun_file_exists` | Check file exists in guest |
| `vmrun_dir_exists` | Check directory exists |
| `vmrun_ls` | List directory in guest |
| `vmrun_mkdir` | Create directory in guest |
| `vmrun_rmdir` | Delete directory in guest |
| `vmrun_rm` | Delete file in guest |
| `vmrun_rename` | Rename file in guest |
| `vmrun_copy_to` | Copy file to guest |
| `vmrun_copy_from` | Copy file from guest |
| `vmrun_temp_file` | Create temp file in guest |
| `vmrun_run` | Run program in guest |
| `vmrun_script` | Run script in guest |
| `vmrun_ps` | List processes in guest |
| `vmrun_kill` | Kill process in guest |
| `vmrun_shared_enable` | Enable shared folders |
| `vmrun_shared_disable` | Disable shared folders |
| `vmrun_shared_add` | Add shared folder |
| `vmrun_shared_remove` | Remove shared folder |
| `vmrun_shared_set` | Set shared folder state |
| `vmrun_device_connect` | Connect device |
| `vmrun_device_disconnect` | Disconnect device |
| `vmrun_var_read` | Read VM variable |
| `vmrun_var_write` | Write VM variable |
| `vmrun_screenshot` | Capture screenshot |
| `vmrun_keystrokes` | Type keystrokes |
| `vmrun_tools_install` | Install VMware Tools |
| `vmrun_tools_state` | Check Tools state |
| `vmrun_guest_ip` | Get guest IP |
| `vmrun_host_networks` | List host networks |
| `vmrun_portforward_list` | List port forwardings |
| `vmrun_portforward_set` | Set port forwarding |
| `vmrun_portforward_delete` | Delete port forwarding |

### vmcli Tools
| Tool | Description |
|------|-------------|
| `snapshot_list` | List snapshots |
| `snapshot_take` | Take snapshot |
| `snapshot_revert` | Revert to snapshot |
| `snapshot_delete` | Delete snapshot |
| `snapshot_clone` | Clone from snapshot |
| `guest_run` | Run program |
| `guest_ps` | List processes |
| `guest_kill` | Kill process |
| `guest_ls` | List files |
| `guest_mkdir` | Create directory |
| `guest_rm` | Delete file |
| `guest_rmdir` | Delete directory |
| `guest_copy_to` | Copy to guest |
| `guest_copy_from` | Copy from guest |
| `guest_env` | Get environment |
| `mks_screenshot` | Capture screenshot |
| `mks_send_key` | Send key sequence |
| `mks_query` | Query MKS state |
| `chipset_query` | Query CPU/memory config |
| `chipset_set_cpu` | Set CPU count |
| `chipset_set_memory` | Set memory size |
| `chipset_set_cores` | Set cores per socket |
| `tools_query` | Query Tools status |
| `tools_install` | Install Tools |
| `tools_upgrade` | Upgrade Tools |
| `template_create` | Create VM template |
| `template_deploy` | Deploy VM template |
| `disk_query` | Query disk config |
| `disk_create` | Create disk |
| `disk_extend` | Extend disk |
| `config_query` | Query config params |
| `config_set` | Set config param |
| `power_query` | Query power state |
| `power_start` | Start VM |
| `power_stop` | Stop VM |
| `power_pause` | Pause VM |
| `power_unpause` | Unpause VM |
| `power_reset` | Reset VM |
| `power_suspend` | Suspend VM |
| `ethernet_query` | Query ethernet config |
| `ethernet_set_type` | Set connection type |
| `ethernet_set_present` | Set adapter present |
| `ethernet_set_connected` | Set start connected |
| `ethernet_set_device` | Set virtual device |
| `ethernet_set_network` | Set network name |
| `ethernet_purge` | Remove adapter |
| `hgfs_query` | Query shared folders |
| `hgfs_set_enabled` | Enable/disable share |
| `hgfs_set_path` | Set host path |
| `hgfs_set_name` | Set guest name |
| `hgfs_set_read` | Set read access |
| `hgfs_set_write` | Set write access |
| `serial_query` | Query serial ports |
| `serial_set_present` | Set serial present |
| `serial_purge` | Remove serial port |
| `sata_query` | Query SATA config |
| `sata_set_present` | Set SATA present |
| `sata_purge` | Remove SATA adapter |
| `nvme_query` | Query NVMe config |
| `nvme_set_present` | Set NVMe present |
| `nvme_purge` | Remove NVMe adapter |
| `vprobes_query` | Query VProbes |
| `vprobes_enable` | Enable VProbes |
| `vprobes_load` | Load VProbes script |
| `vprobes_reset` | Reset VProbes |

## License

MIT
