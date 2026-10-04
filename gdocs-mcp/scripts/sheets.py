#!/usr/bin/env python3
"""
Google Sheets 读写工具 — 基于 gdocs-mcp 的 OAuth token。

用法:
    # 读取整个 sheet
    python sheets.py read <spreadsheet_id> <sheet_name>

    # 读取指定范围
    python sheets.py read <spreadsheet_id> <sheet_name> --range A1:D20

    # 写入（覆盖指定范围）
    python sheets.py write <spreadsheet_id> <sheet_name> --range A1:B2 --data '[["Name","Age"],["Alice","30"]]'

    # 追加行（在数据末尾追加）
    python sheets.py append <spreadsheet_id> <sheet_name> --data '[["新行1","值1"],["新行2","值2"]]'

    # 列出所有 sheet
    python sheets.py info <spreadsheet_id>

Token 自动从 ~/.gdocs-mcp/token.json 读取，过期自动刷新。
"""

import json
import sys
import os
import argparse
import urllib.request
import urllib.error
import urllib.parse

TOKEN_PATH = os.path.expanduser("~/.gdocs-mcp/token.json")
CRED_PATH = os.path.expanduser("~/.gdocs-mcp/credentials.json")
SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"


def load_token():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token 不存在: {TOKEN_PATH}\n请先运行: npx gdocs-mcp auth")
    with open(TOKEN_PATH) as f:
        return json.load(f)


def refresh_token(token_data):
    """用 refresh_token 换新 access_token"""
    with open(CRED_PATH) as f:
        creds = json.load(f)
    client_info = creds.get("installed") or creds.get("web")
    if not client_info:
        raise ValueError("无法解析 credentials.json")

    data = urllib.parse.urlencode({
        "client_id": client_info["client_secret"],
        "client_secret": client_info["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    resp = urllib.request.urlopen(req)
    new_tokens = json.loads(resp.read())

    token_data["access_token"] = new_tokens["access_token"]
    if "expires_in" in new_tokens:
        import time
        token_data["expiry_date"] = int(time.time() * 1000) + new_tokens["expires_in"] * 1000

    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f, indent=2)
    return token_data


def api_call(url, token_data, method="GET", body=None):
    """调 Google Sheets API，自动处理 token 刷新"""
    def _do_call():
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token_data['access_token']}")
        if body is not None:
            req.add_header("Content-Type", "application/json")
            req.method = method
            req.data = json.dumps(body).encode()
        try:
            resp = urllib.request.urlopen(req)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            return {"error": {"code": e.code, "body": err_body}}

    result = _do_call()
    # 401 说明 token 过期，刷新后重试
    if result.get("error", {}).get("code") == 401:
        token_data = refresh_token(token_data)
        result = _do_call()
    return result


def sheet_url(spreadsheet_id, sheet_name, range_spec=None):
    """构建 Sheets API URL"""
    encoded = urllib.parse.quote(sheet_name)
    base = f"{SHEETS_API}/{spreadsheet_id}/values/{encoded}"
    if range_spec:
        base += f"!{range_spec}"
    else:
        base += "!A1:ZZ10000"
    return base


def cmd_info(args):
    """列出 spreadsheet 的 sheet 信息"""
    token = load_token()
    result = api_call(f"{SHEETS_API}/{args.spreadsheet_id}", token)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_read(args):
    """读取 sheet 数据"""
    token = load_token()
    url = sheet_url(args.spreadsheet_id, args.sheet_name, args.range)
    result = api_call(url, token)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    values = result.get("values", [])
    if args.json:
        print(json.dumps({"range": result.get("range"), "values": values}, ensure_ascii=False, indent=2))
    else:
        print(f"Range: {result.get('range')}")
        print(f"Rows: {len(values)}")
        for i, row in enumerate(values):
            print(f"  [{i + 1}] {' | '.join(row)}")


def cmd_write(args):
    """写入 sheet 数据（覆盖指定范围）"""
    token = load_token()
    url = sheet_url(args.spreadsheet_id, args.sheet_name, args.range)
    try:
        values = json.loads(args.data)
    except json.JSONDecodeError:
        print("Error: --data 必须是合法 JSON 数组", file=sys.stderr)
        sys.exit(1)

    body = {
        "range": f"{args.sheet_name}!{args.range}",
        "values": values,
    }
    params = "?valueInputOption=USER_ENTERED"
    result = api_call(url + params, token, method="PUT", body=body)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ 写入成功: {result.get('updatedCells', '?')} cells → {result.get('updatedRange', '?')}")


def cmd_append(args):
    """追加行到 sheet 末尾"""
    token = load_token()
    url = f"{SHEETS_API}/{args.spreadsheet_id}/values/{urllib.parse.quote(args.sheet_name)}:append"
    try:
        values = json.loads(args.data)
    except json.JSONDecodeError:
        print("Error: --data 必须是合法 JSON 数组", file=sys.stderr)
        sys.exit(1)

    body = {"values": values}
    params = "?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS"
    result = api_call(url + params, token, method="POST", body=body)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ 追加成功: {result.get('updates', {}).get('updatedRows', '?')} rows → {result.get('updates', {}).get('updatedRange', '?')}")


def main():
    parser = argparse.ArgumentParser(description="Google Sheets 读写工具 (基于 gdocs-mcp token)")
    sub = parser.add_subparsers(dest="command")

    p_info = sub.add_parser("info", help="查看 spreadsheet 信息")
    p_info.add_argument("spreadsheet_id")

    p_read = sub.add_parser("read", help="读取 sheet 数据")
    p_read.add_argument("spreadsheet_id")
    p_read.add_argument("sheet_name")
    p_read.add_argument("--range", help="范围，如 A1:D20（默认整表）")
    p_read.add_argument("--json", action="store_true", help="JSON 输出")

    p_write = sub.add_parser("write", help="写入/覆盖 sheet 数据")
    p_write.add_argument("spreadsheet_id")
    p_write.add_argument("sheet_name")
    p_write.add_argument("--range", required=True, help="写入范围，如 A1:B2")
    p_write.add_argument("--data", required=True, help='数据 JSON，如 \'[["A","B"],["C","D"]]\'')

    p_append = sub.add_parser("append", help="追加行到 sheet 末尾")
    p_append.add_argument("spreadsheet_id")
    p_append.add_argument("sheet_name")
    p_append.add_argument("--data", required=True, help='数据 JSON，如 \'[["新行1","值1"]]\'')

    args = parser.parse_args()
    if args.command == "info":
        cmd_info(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "write":
        cmd_write(args)
    elif args.command == "append":
        cmd_append(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
