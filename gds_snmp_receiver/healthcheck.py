"""Simple healthcheck for the gds_snmp_receiver container.

This script inspects /proc/*/cmdline to determine whether the receiver
process is running. It exits 0 if found, non-zero otherwise. Using a
small Python script avoids depending on external utilities like pgrep.
"""

import os
import sys


def main() -> int:
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmd = f.read().decode(errors="ignore")
                if (
                    "gds_snmp_receiver.receiver" in cmd
                    or "gds_snmp_receiver/core.py" in cmd
                ):
                    return 0
        except OSError:
            # processes can disappear; ignore OS-related errors
            continue
    return 1


if __name__ == "__main__":
    sys.exit(main())
