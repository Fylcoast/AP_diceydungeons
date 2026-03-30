#!/usr/bin/env python3
"""Launcher to start the game and capture stdout/stderr in real time.

Usage examples:
  python launch_and_capture.py --log out.log "C:\\Path\\To\\DiceyDungeons.exe" --arg1 --arg2
  python launch_and_capture.py --log out.log run_game.bat

Behavior:
- Prints stdout lines prefixed with [STDOUT] and stderr with [STDERR].
- If a line starts with "[AP]" the remainder is attempted to be parsed as JSON and is printed as parsed JSON.
"""
from __future__ import annotations
import argparse
import os
import platform
import subprocess
import threading
import sys
import json
from typing import TextIO, Optional
from queue import Queue

import re


def read_stream(stream: TextIO, prefix: str, logfile: Optional[TextIO] = None, message_queue: Optional[Queue] = None) -> None:
    try:
        while True:
            line = stream.readline()
            if line == "":
                break
            line = line.rstrip("\n")
            out = f"{prefix} {line}"
            print(out)
            if logfile:
                logfile.write(out + "\n")
                logfile.flush()

            # optional: detect messages from the game with a prefix
            if "[AP]" in line:
                # Detect formatting errors for sending shop hints
                if "Error: No symbol" in line:
                    location = re.findall(r'\d+', line.partition("[AP]")[2].strip())[0]
                    print(f"[AP-LOC] {location}")
                    if message_queue and location:
                        message_queue.put({"type": "game_message", "data": {"command": "potential_hint", "payload": location}})
                else:
                    # Send normal messages
                    payload = line.partition("[AP]")[2].strip()
                    try:
                        obj = json.loads(payload)
                        print(f"[AP-JSON] {json.dumps(obj, ensure_ascii=False)}")
                        if message_queue:
                            message_queue.put({"type": "game_message", "data": obj})
                    except Exception:
                        pass
    finally:
        try:
            stream.close()
        except Exception:
            pass

def launch(game_path: str) -> Queue:
    """Launch the game and return a queue for receiving messages.
    
    Args:
        game_path: Path to the game executable.
    
    Returns:
        A queue.Queue() that receives dicts with 'type' and 'data' keys.
        When a line starts with [AP], it's parsed as JSON and put in the queue.
    """
    message_queue: Queue = Queue()
    
    use_shell = False
    cmd_to_run = game_path
    if platform.system() == 'Windows':
        cmd_to_run = os.path.join(cmd_to_run, "diceydungeons.exe")
    elif platform.system() == 'Linux':
        cmd_to_run = os.path.join(cmd_to_run, "diceydungeons")
    logfile = None
    try:
        popen = subprocess.Popen(
            [cmd_to_run, "mod=diceyap"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=use_shell,
            bufsize=1,
            universal_newlines=True,
            cwd=game_path
        )
    except FileNotFoundError:
        print("Executable not found; check the path.")
        message_queue.put({"type": "error", "data": "Executable not found"})
        return message_queue
    except Exception as e:
        print(f"Failed to start process: {e}")
        message_queue.put({"type": "error", "data": str(e)})
        return message_queue

    threads = []
    if popen.stdout:
        t = threading.Thread(target=read_stream, args=(popen.stdout, "[STDOUT]", logfile, message_queue), daemon=True)
        t.start()
        threads.append(t)
    if popen.stderr:
        t = threading.Thread(target=read_stream, args=(popen.stderr, "[STDERR]", logfile, message_queue), daemon=True)
        t.start()
        threads.append(t)

    # Launch a thread to wait for process exit and signal completion
    def wait_for_process():
        try:
            exit_code = popen.wait()
            # ensure threads finish reading
            for t in threads:
                t.join(timeout=1)
        finally:
            if logfile:
                logfile.close()
            message_queue.put({"type": "process_exit", "data": exit_code})
    
    exit_thread = threading.Thread(target=wait_for_process, daemon=True)
    exit_thread.start()
    
    return message_queue
