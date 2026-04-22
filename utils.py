# utils.py
import json
import os
import socket
import requests
def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                def is_online(host="8.8.8.8", port=53, timeout=3):
                    try:
                        socket.setdefaulttimeout(timeout)
                        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                        return True
                    except Exception:
                        return False
                        def read_json(filename):
                            if not os.path.exists(filename):
                                return {}
                                with open(filename, "r", encoding="utf-8") as file:
                                    try:
                                        return json.load(file)
                                    except json.JSONDecodeError:
                                        return {}
                                        def write_json(filename, data):
                                            with open(filename, "w", encoding="utf-8") as file:
                                                json.dump(data, file, indent=2, ensure_ascii=False)
                                                def ensure_file_exists(filename):
                                                    if not os.path.exists(filename):
                                                        with open(filename, "w", encoding="utf-8") as file:
                                                            json.dump({}, file)
                                                            def safely_update_json(filename, key, value):
                                                                data = read_json(filename)
                                                                data[key] = value
                                                                write_json(filename, data)
                                                                def safely_remove_key(filename, key):
                                                                    data = read_json(filename)
                                                                    if key in data:
                                                                        del data[key]
                                                                        write_json(filename, data)
                                                                        return True
                                                                        return False
