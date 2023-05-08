# ----------------------------------- #
# Authored by Kurt Rojas              #
# Version 1.kr (26/10/2022)              #
# Version 2.kr (25/04/2023)              #
# ----------------------------------- #

import signal
from subprocess import check_output
import os
import sys
from pprint import pprint
import argparse

"""
Problem description:
    The `ghost job` problem is very common in the smith cluster and it will hinder the user from running jobs properly.
    The current solution is quite tedious to do since we detect, email the owner of the ghost job, and let them kill it.
    Its time consuming since (1) its hard to detect manually and (2) removing the ghost job does not alleviate the hang
    state of the calculations (*so we cancel the job and resubmit*).
    
Cases of ghost jobs:
    (A) - An available node is occupied by a ghost job (but still considered as available)
    (B) - User A has a ghost job running on a node, User B submits a job on the same node, User B's job will be in hang state.
    (C) - User A has a ghost job running on a node, User A submits a job on the same node, User A's job (2nd) will be in hang state.
"""

"""
Usage:
    Used to kill all jobs
    Usage (kill all processes, except connection): python ghostbuster.py
    Usage (kill specific program, ie. `pw.x`):   python ghostbuster.py pw.x
"""


# -- ARGUMENTS --
# create the argument parser
parser = argparse.ArgumentParser(description="Ghostbuster: Kill all processes except the current connection")

# add an argument to control whether to print output or not
parser.add_argument("-s", "--silent", action="store_true", help="suppress output")
parser.add_argument("-d", "--debug", action="store_true", help="print debug messages")
parser.add_argument("-c", "--commands", nargs="*", help="list of commands keyword to cleanup (default: all by user)")
parser.add_argument("-t", "--time", type=int, help="minimum time parameter to include process", default=5)
parser.add_argument("-y", "--yes", action="store_true", help="automatically confirm the process kill")

# parse the arguments
args = parser.parse_args()

# -- INITIALIZE SETTINGS --
version = "2.0.kr"
pid1 = str(os.getpid())
# USERNAME = os.getlogin()
ps_command = "ps -Ao user:30,pid,%cpu,cputime,fname"

if not args.silent:
    print(f"---    Ghostbuster v{version}    ---")
    print("")
    print(f">> PYTHON PID EXCLUDED: {pid1}")
    print(f"   (All `bash` and `ssh` processes will be excluded as well)")
    print(f">> USERNAME: {USERNAME}")
    print(f">> PS COMMAND:")
    print(f"   `{ps_command}`")


def duration_to_minutes(duration):
    days, time = duration.split("-") if "-" in duration else (0, duration)
    hours, minutes, seconds = map(int, time.split(":"))
    total_minutes = (int(days) * 24 * 60) + (hours * 60) + minutes + (seconds / 60)
    return total_minutes


# -- GET ALL PROCESSES --
# a. get all processes
proc = check_output(ps_command, shell=True).decode().splitlines()

# b. filter by user
proc = [i for i in proc if (USERNAME == i.split()[0])]

# c. filter by time
# this filter if jobs that concindentally just happens to run at the same time as this script
# default is 5 minutes.
# This filter can be used to filter out jobs for case (C) by setting the time to the oldest job's time
new_proc = {}
for p in proc:
    _user, _pid, _cpu, _time, _cmd = p.split()
    _time = duration_to_minutes(_time)

    if _time > args.time and float(_cpu) > 5.0:
        new_proc[int(_pid)] = {
            "user": _user,
            "pid": _pid,
            "cpu": _cpu,
            "time": f"{_time:.2f}",
            "cmd": _cmd,
        }
proc = new_proc

if args.debug:
    print(f">> PROCESS LIST:")
    for i in proc.values():
        print("   ", i)


# d. (optional) filter by program
if args.commands:
    new_proc = proc.copy()
    print(f">> PROCESS LIST (program filtered):")
    for p, pval in proc.items():
        if not pval["cmd"] in args.commands:
            new_proc.pop(p)
    proc = new_proc

    if args.debug:
        for i in proc.values():
            print("   ", i)

# -- CONFIRMATION --
print(">> TOTAL PROCESSES TO STOP:", len(proc))
print(">> PROCESS LIST:")
for i in proc.values():
    print("   ", i)

if not args.yes:
    response = input("\nPress Y to confirm, N to cancel:   ").upper()
    confirm = bool(response == "Y")
else:
    confirm = args.yes
    response = "auto"

if not confirm:
    sys.exit(">> TERMINATION CANCELLED")
else:
    print(f">> CONFIRMATION: `{response}`")


# -- KILL PROCESSES --
for p, pval in proc.items():
    try:
        # os.kill(int(pval["pid"]), signal.SIGKILL)
        print(f"   Process {pval['pid']:^10} ({pval['cmd']:^10}) -- terminated.")
    except ProcessLookupError:
        print(f"   Process {pval['pid']:^10} ({pval['cmd']:^10}) -- no longer running since last check.")
