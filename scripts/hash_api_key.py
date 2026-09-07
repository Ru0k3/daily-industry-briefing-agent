#!/usr/bin/env python3
"""Print a SHA-256 hash suitable for AGENT_API_KEYS."""

import argparse
import hashlib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("api_key", help="API key to hash; avoid shell history in production")
args = parser.parse_args()
print(hashlib.sha256(args.api_key.encode()).hexdigest())
