import sys
import os
from grpc_tools import protoc

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    proto_path = os.path.join(base_dir, "cxx-device-runtime", "proto", "device_service.proto")
    out_dir = os.path.join(base_dir, "python-validation-engine", "proto")

    os.makedirs(out_dir, exist_ok=True)
    
    # Touch __init__.py
    with open(os.path.join(out_dir, "__init__.py"), "w") as f:
        f.write("# Generated gRPC package\n")

    print(f"[INFO] Generating gRPC Python stubs from {proto_path} into {out_dir}...")
    command = [
        "grpc_tools.protoc",
        f"-I{os.path.dirname(proto_path)}",
        f"--python_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        proto_path
    ]

    res = protoc.main(command)
    if res == 0:
        print("[SUCCESS] Python gRPC stubs generated successfully.")
    else:
        print(f"[ERROR] protoc failed with exit code: {res}")
        sys.exit(res)

if __name__ == "__main__":
    main()
