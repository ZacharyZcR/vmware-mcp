# VMware Workstation Pro MCP Server

通过 REST API、vmrun 和 vmcli 控制 VMware Workstation Pro 虚拟机的 MCP 服务器。

## 功能特性

**117 个工具**，覆盖 VMware Workstation Pro 全部自动化能力：

| 来源 | 工具数 | 描述 |
|------|--------|------|
| REST API | 20 | 虚拟机管理、网卡、共享文件夹、端口转发 |
| vmrun | 54 | 电源、快照、克隆、客户机文件/进程操作、设备 |
| vmcli | 43 | 芯片组、磁盘、网卡、SATA、NVMe、串口、VProbes |

## 环境要求

- VMware Workstation Pro 17+
- Python 3.10+
- vmrest 服务运行中（REST API 工具需要）

## 安装

```bash
git clone https://github.com/ZacharyZcR/vmware-mcp.git
cd vmware-mcp
pip install -e .
```

## 配置

启动 vmrest 服务：
```bash
# 首次配置
"C:\Program Files (x86)\VMware\VMware Workstation\vmrest.exe" -C

# 启动服务
"C:\Program Files (x86)\VMware\VMware Workstation\vmrest.exe"
```

添加到 Claude Code：
```bash
claude mcp add vmware-mcp \
  -e VMWARE_USERNAME=your_username \
  -e VMWARE_PASSWORD=your_password \
  -- vmware-mcp
```

## 工具列表

### REST API 工具
| 工具 | 描述 |
|------|------|
| `vm_list` | 列出所有虚拟机 |
| `vm_get` | 获取虚拟机设置 |
| `vm_create` | 克隆虚拟机 |
| `vm_delete` | 删除虚拟机 |
| `vm_update` | 更新虚拟机 CPU/内存 |
| `vm_power_get` | 获取电源状态 |
| `vm_power_set` | 设置电源状态（开/关/挂起/暂停） |
| `vm_nic_list` | 列出网络适配器 |
| `vm_nic_create` | 创建网络适配器 |
| `vm_nic_delete` | 删除网络适配器 |
| `vm_ip_get` | 获取虚拟机 IP 地址 |
| `vm_folder_list` | 列出共享文件夹 |
| `vm_folder_create` | 创建共享文件夹 |
| `vm_folder_delete` | 删除共享文件夹 |
| `network_list` | 列出虚拟网络 |
| `network_create` | 创建虚拟网络 |
| `network_portforward_list` | 列出端口转发 |
| `network_portforward_set` | 设置端口转发 |
| `network_portforward_delete` | 删除端口转发 |

### vmrun 工具
| 工具 | 描述 |
|------|------|
| `vmrun_list` | 列出运行中的虚拟机 |
| `vmrun_start` | 启动虚拟机 |
| `vmrun_stop` | 停止虚拟机（软/硬） |
| `vmrun_reset` | 重置虚拟机 |
| `vmrun_suspend` | 挂起虚拟机 |
| `vmrun_pause` | 暂停虚拟机 |
| `vmrun_unpause` | 恢复暂停的虚拟机 |
| `vmrun_clone` | 克隆虚拟机（完整/链接） |
| `vmrun_upgrade` | 升级虚拟机格式 |
| `vmrun_delete` | 删除虚拟机 |
| `vmrun_snapshot_list` | 列出快照 |
| `vmrun_snapshot_take` | 创建快照 |
| `vmrun_snapshot_delete` | 删除快照 |
| `vmrun_snapshot_revert` | 恢复快照 |
| `vmrun_file_exists` | 检查客户机文件是否存在 |
| `vmrun_dir_exists` | 检查目录是否存在 |
| `vmrun_ls` | 列出客户机目录 |
| `vmrun_mkdir` | 在客户机创建目录 |
| `vmrun_rmdir` | 删除客户机目录 |
| `vmrun_rm` | 删除客户机文件 |
| `vmrun_rename` | 重命名客户机文件 |
| `vmrun_copy_to` | 复制文件到客户机 |
| `vmrun_copy_from` | 从客户机复制文件 |
| `vmrun_temp_file` | 在客户机创建临时文件 |
| `vmrun_run` | 在客户机运行程序 |
| `vmrun_script` | 在客户机运行脚本 |
| `vmrun_ps` | 列出客户机进程 |
| `vmrun_kill` | 终止客户机进程 |
| `vmrun_shared_enable` | 启用共享文件夹 |
| `vmrun_shared_disable` | 禁用共享文件夹 |
| `vmrun_shared_add` | 添加共享文件夹 |
| `vmrun_shared_remove` | 移除共享文件夹 |
| `vmrun_shared_set` | 设置共享文件夹状态 |
| `vmrun_device_connect` | 连接设备 |
| `vmrun_device_disconnect` | 断开设备 |
| `vmrun_var_read` | 读取虚拟机变量 |
| `vmrun_var_write` | 写入虚拟机变量 |
| `vmrun_screenshot` | 截取屏幕 |
| `vmrun_keystrokes` | 发送按键 |
| `vmrun_tools_install` | 安装 VMware Tools |
| `vmrun_tools_state` | 检查 Tools 状态 |
| `vmrun_guest_ip` | 获取客户机 IP |
| `vmrun_host_networks` | 列出主机网络 |
| `vmrun_portforward_list` | 列出端口转发 |
| `vmrun_portforward_set` | 设置端口转发 |
| `vmrun_portforward_delete` | 删除端口转发 |

### vmcli 工具
| 工具 | 描述 |
|------|------|
| `snapshot_list` | 列出快照 |
| `snapshot_take` | 创建快照 |
| `snapshot_revert` | 恢复快照 |
| `snapshot_delete` | 删除快照 |
| `snapshot_clone` | 从快照克隆 |
| `guest_run` | 运行程序 |
| `guest_ps` | 列出进程 |
| `guest_kill` | 终止进程 |
| `guest_ls` | 列出文件 |
| `guest_mkdir` | 创建目录 |
| `guest_rm` | 删除文件 |
| `guest_rmdir` | 删除目录 |
| `guest_copy_to` | 复制到客户机 |
| `guest_copy_from` | 从客户机复制 |
| `guest_env` | 获取环境变量 |
| `mks_screenshot` | 截取屏幕 |
| `mks_send_key` | 发送按键序列 |
| `mks_query` | 查询 MKS 状态 |
| `chipset_query` | 查询 CPU/内存配置 |
| `chipset_set_cpu` | 设置 CPU 数量 |
| `chipset_set_memory` | 设置内存大小 |
| `chipset_set_cores` | 设置每插槽核心数 |
| `tools_query` | 查询 Tools 状态 |
| `tools_install` | 安装 Tools |
| `tools_upgrade` | 升级 Tools |
| `template_create` | 创建虚拟机模板 |
| `template_deploy` | 部署虚拟机模板 |
| `disk_query` | 查询磁盘配置 |
| `disk_create` | 创建磁盘 |
| `disk_extend` | 扩展磁盘 |
| `config_query` | 查询配置参数 |
| `config_set` | 设置配置参数 |
| `power_query` | 查询电源状态 |
| `power_start` | 启动虚拟机 |
| `power_stop` | 停止虚拟机 |
| `power_pause` | 暂停虚拟机 |
| `power_unpause` | 恢复虚拟机 |
| `power_reset` | 重置虚拟机 |
| `power_suspend` | 挂起虚拟机 |
| `ethernet_query` | 查询网卡配置 |
| `ethernet_set_type` | 设置连接类型 |
| `ethernet_set_present` | 设置适配器存在 |
| `ethernet_set_connected` | 设置启动时连接 |
| `ethernet_set_device` | 设置虚拟设备 |
| `ethernet_set_network` | 设置网络名称 |
| `ethernet_purge` | 移除适配器 |
| `hgfs_query` | 查询共享文件夹 |
| `hgfs_set_enabled` | 启用/禁用共享 |
| `hgfs_set_path` | 设置主机路径 |
| `hgfs_set_name` | 设置客户机名称 |
| `hgfs_set_read` | 设置读取权限 |
| `hgfs_set_write` | 设置写入权限 |
| `serial_query` | 查询串口 |
| `serial_set_present` | 设置串口存在 |
| `serial_purge` | 移除串口 |
| `sata_query` | 查询 SATA 配置 |
| `sata_set_present` | 设置 SATA 存在 |
| `sata_purge` | 移除 SATA 适配器 |
| `nvme_query` | 查询 NVMe 配置 |
| `nvme_set_present` | 设置 NVMe 存在 |
| `nvme_purge` | 移除 NVMe 适配器 |
| `vprobes_query` | 查询 VProbes |
| `vprobes_enable` | 启用 VProbes |
| `vprobes_load` | 加载 VProbes 脚本 |
| `vprobes_reset` | 重置 VProbes |

## 许可证

MIT
