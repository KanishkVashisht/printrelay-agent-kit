#!/usr/bin/env python3
"""Save a local PrintRelay credential; emit only native registration arguments. No network calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys


def prepare(path, resume=False):
    path = Path(path).expanduser()
    if resume:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                raise ValueError('Existing key must be an owned regular file with mode0600.')
            raw = os.read(fd, 128)
            if not re.fullmatch(rb'pr_key_[a-f0-9]{64}\n?', raw):
                raise ValueError('Existing file is not a PrintRelay credential.')
            return raw.rstrip(b'\n').decode('ascii')
        finally:
            os.close(fd)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    key = 'pr_key_' + secrets.token_hex(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', closefd=False) as output:
            output.write(key + '\n')
            output.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    return key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key-file', required=True, help='Private path outside source control. Never overwritten.')
    parser.add_argument('--name', required=True, help='Named target agent; use exactly the same name on retries.')
    parser.add_argument('--confirm-full-account-access', action='store_true', required=True,
                        help='Owner authorized read/upload/compare/delete and backlog create/cancel access until revoked; no key management, operator, payment or production access.')
    parser.add_argument('--resume', action='store_true', help='Reuse an existing mode0600 file after an interrupted registration.')
    args = parser.parse_args()
    name = args.name.strip()
    if not 1 <= len(name) <= 60 or any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValueError('Name must be1–60 characters without control characters.')
    key = prepare(args.key_file, args.resume)
    print(json.dumps({'name': name, 'key_sha256': hashlib.sha256(key.encode('ascii')).hexdigest(),
                      'confirm_full_account_access': True}))


if __name__ == '__main__':
    try:
        main()
    except FileExistsError:
        print(json.dumps({'error': 'Key file already exists. Use --resume with the same name to retry; never overwrite an active credential.'}), file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError):
        print(json.dumps({'error': 'Credential preparation failed. Check the private file path, ownership, mode0600, and key name. No secret was printed.'}), file=sys.stderr)
        sys.exit(1)
