import socket
import json
import base64
import sys

def send_command(cmd):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 9090))
        msg = json.dumps(cmd) + "\n"
        s.sendall(msg.encode('utf-8'))
        
        data = b""
        while True:
            chunk = s.recv(8192)
            if not chunk:
                break
            data += chunk
            if b"\n" in chunk:
                break
                
        s.close()
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
        return None

if len(sys.argv) > 1:
    cmd_name = sys.argv[1]
    if cmd_name == "screenshot":
        resp = send_command({"command": "screenshot"})
        if resp and "data" in resp:
            with open("screenshot.png", "wb") as f:
                f.write(base64.b64decode(resp["data"]))
            print("Screenshot saved")
    elif cmd_name == "click":
        # python mcp_client.py click <x> <y>
        x, y = int(sys.argv[2]), int(sys.argv[3])
        resp = send_command({"command": "click", "params": {"x": x, "y": y}})
        print(resp)
    elif cmd_name == "get_scene_tree":
        resp = send_command({"command": "get_scene_tree"})
        print(json.dumps(resp, indent=2))
    elif cmd_name == "get_ui_elements":
        resp = send_command({"command": "get_ui_elements"})
        print(json.dumps(resp, indent=2))
    elif cmd_name == "raw":
        raw_cmd = json.loads(sys.argv[2])
        resp = send_command(raw_cmd)
        print(json.dumps(resp, indent=2))
else:
    print("Usage: python mcp_client.py <command> [args...]")
    print("Commands:")
    print("  screenshot            - Save visual snapshot to screenshot.png")
    print("  click <x> <y>         - Send click event to coordinates (x, y)")
    print("  get_scene_tree        - Output current SceneTree as JSON")
    print("  get_ui_elements       - Output list of UI controls as JSON")
    print("  raw '<json_string>'   - Send raw JSON payload to McpInteractionServer")
