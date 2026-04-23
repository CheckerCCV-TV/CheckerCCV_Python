# Checker CCV

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-requirements.txt-success)](./requirements.txt)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](#)
[![Language](https://img.shields.io/badge/docs-EN%20%7C%20中文%20%7C%20VI-orange)](#english)

Multi-language guide for running `checkerccv.py` with **English**, **Chinese**, and **Vietnamese** instructions.

---

## Table of Contents

- [1) Install dependencies first (REQUIRED)](#1-install-dependencies-first-required)
- [English](#english)
- [中文](#中文)
- [Tiếng Việt](#tiếng-việt)

## 1) Install dependencies first (REQUIRED)

> [!IMPORTANT]
> Always install dependencies before the first run.

Before doing anything else, install required Python packages:

```bash
pip install -r requirements.txt
```

If your system has both Python 2 and Python 3, use:

```bash
pip3 install -r requirements.txt
```

If `pip` is not found:

```bash
python -m pip install -r requirements.txt
```

Quick run command after installation:

```bash
python checkerccv.py
```

---

## English

### Quick Start
```bash
pip install -r requirements.txt
python checkerccv.py
```

### Overview
`checkerccv.py` is a multi-threaded card checker client.  
It reads cards from `listcc.txt`, checks them via remote API, and writes results to:
- `Live.txt`
- `Dead.txt`
- `Error.txt`

It also stores your credentials in `config.json`:
- `api_key`
- `token`

### Requirements
- Python 3.10+ (recommended)
- Internet connection
- Valid API key and token

### Files
- `checkerccv.py`: main script
- `requirements.txt`: Python dependencies (`requests`, `colorama`)
- `config.json`: saved credentials
- `listcc.txt`: input card list (one card per line)

### Input format (`listcc.txt`)
Put one card record per line. Example:

```text
4111111111111111|12|2028|123
5555555555554444|10|2027|456
```

Empty lines are ignored.

### How to run
1. Open terminal in project folder.
2. Install dependencies first:
   ```bash
   pip install -r requirements.txt
   ```
3. Run script:
   ```bash
   python checkerccv.py
   ```
4. If `config.json` is empty/invalid, enter:
   - `API_KEY`
   - `TOKEN`
5. Script checks your credit balance.
6. Script shows enabled gates and asks you to choose one.
7. Enter number of threads.
8. Script starts checking cards from `listcc.txt`.

### Output behavior
- `Live` cards -> appended to `Live.txt`
- `Dead` cards -> appended to `Dead.txt`
- Other errors/unsupported/unknown max retries -> appended to `Error.txt`

During run, the script removes processed lines from `listcc.txt` to avoid duplicate processing on next run.

### Error codes (from API)
- `0`: Live
- `1`: Unknown (auto retry)
- `2`: Dead
- `3`: Unknown (auto retry)
- `4`: Error (unsupported card)
- `5`: Invalid key or insufficient credits (fatal stop)
- `6`: Gate maintenance (fatal stop)

### Notes
- Keep `API_KEY` and `TOKEN` private.
- Max threads accepted by script is dynamic (up to 64 and not more than total cards).
- If `listcc.txt` is missing or empty, script exits.

---

## 中文

### 快速开始
```bash
pip install -r requirements.txt
python checkerccv.py
```

### 概述
`checkerccv.py` 是一个多线程卡片检测脚本。  
它会从 `listcc.txt` 读取卡数据，通过远程 API 检测，并把结果写入：
- `Live.txt`
- `Dead.txt`
- `Error.txt`

凭证会保存在 `config.json`：
- `api_key`
- `token`

### 环境要求
- Python 3.10+（推荐）
- 可用网络连接
- 有效的 API key 和 token

### 文件说明
- `checkerccv.py`：主程序
- `requirements.txt`：依赖（`requests`, `colorama`）
- `config.json`：保存凭证
- `listcc.txt`：待检测卡数据（每行一条）

### 输入格式（`listcc.txt`）
每行一条卡数据，例如：

```text
4111111111111111|12|2028|123
5555555555554444|10|2027|456
```

空行会被忽略。

### 使用步骤
1. 在项目目录打开终端。
2. 先安装依赖（第一步必须执行）：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行脚本：
   ```bash
   python checkerccv.py
   ```
4. 如果 `config.json` 为空或无效，输入：
   - `API_KEY`
   - `TOKEN`
5. 脚本会先检查余额（credit）。
6. 脚本显示可用 gate，按编号选择。
7. 输入线程数量。
8. 脚本开始处理 `listcc.txt` 中的数据。

### 输出逻辑
- `Live` -> 写入 `Live.txt`
- `Dead` -> 写入 `Dead.txt`
- 其他错误/不支持/重试后未知 -> 写入 `Error.txt`

运行过程中，已处理的行会从 `listcc.txt` 中移除，避免下次重复处理。

### API 返回码说明
- `0`：Live
- `1`：未知（自动重试）
- `2`：Dead
- `3`：未知（自动重试）
- `4`：错误（卡不支持）
- `5`：Key 无效或余额不足（致命，停止）
- `6`：Gate 维护中（致命，停止）

### 注意事项
- 请妥善保管 `API_KEY` 和 `TOKEN`。
- 线程上限由脚本控制（最多 64，且不超过总卡数）。
- `listcc.txt` 不存在或为空时，脚本会退出。

---

## Tiếng Việt

### Chạy nhanh
```bash
pip install -r requirements.txt
python checkerccv.py
```

### Tổng quan
`checkerccv.py` là script check thẻ chạy đa luồng.  
Script đọc dữ liệu từ `listcc.txt`, gửi lên API để kiểm tra và ghi kết quả vào:
- `Live.txt`
- `Dead.txt`
- `Error.txt`

Thông tin đăng nhập được lưu trong `config.json`:
- `api_key`
- `token`

### Yêu cầu
- Python 3.10+ (khuyến nghị)
- Có kết nối Internet
- Có `API_KEY` và `TOKEN` hợp lệ

### Các file chính
- `checkerccv.py`: chương trình chính
- `requirements.txt`: thư viện cần cài (`requests`, `colorama`)
- `config.json`: lưu thông tin API
- `listcc.txt`: danh sách thẻ đầu vào (mỗi dòng 1 thẻ)

### Định dạng input (`listcc.txt`)
Mỗi dòng 1 thẻ. Ví dụ:

```text
4111111111111111|12|2028|123
5555555555554444|10|2027|456
```

Dòng trống sẽ bị bỏ qua.

### Cách dùng chi tiết
1. Mở terminal tại thư mục dự án.
2. Cài dependency trước tiên (bắt buộc):
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy chương trình:
   ```bash
   python checkerccv.py
   ```
4. Nếu `config.json` chưa có dữ liệu, nhập:
   - `API_KEY`
   - `TOKEN`
5. Script kiểm tra credit còn lại.
6. Script hiển thị danh sách gate đang bật, chọn theo số thứ tự.
7. Nhập số luồng muốn chạy.
8. Script bắt đầu check các dòng trong `listcc.txt`.

### Cơ chế ghi kết quả
- Thẻ `Live` -> ghi vào `Live.txt`
- Thẻ `Dead` -> ghi vào `Dead.txt`
- Trường hợp lỗi/không hỗ trợ/unknown quá số lần retry -> ghi vào `Error.txt`

Trong lúc chạy, các dòng đã xử lý sẽ bị xóa khỏi `listcc.txt` để tránh check trùng ở lần sau.

### Ý nghĩa mã lỗi API
- `0`: Live
- `1`: Unknown (tự retry)
- `2`: Dead
- `3`: Unknown (tự retry)
- `4`: Error (thẻ không hỗ trợ)
- `5`: Key không hợp lệ hoặc hết credit (lỗi nghiêm trọng, dừng)
- `6`: Gate đang bảo trì (lỗi nghiêm trọng, dừng)

### Lưu ý
- Giữ kín `API_KEY` và `TOKEN`.
- Số luồng tối đa do script giới hạn (không quá 64 và không vượt tổng số dòng thẻ).
- Nếu thiếu `listcc.txt` hoặc file rỗng, script sẽ dừng.

---

Nếu README này hữu ích, bạn có thể star repository để ủng hộ dự án.
