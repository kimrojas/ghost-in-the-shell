from subprocess import check_output
from concurrent.futures import ProcessPoolExecutor
import json
import os


# -- USERJOBS --
USERNAME = os.getlogin()
jobs = check_output(f"qstat -f -s r -r | grep -A  2 {USERNAME}", shell=True).decode().split("--")

node_dict = {}
print(len(jobs))
for job in jobs:
    job = job.splitlines()
    job = job[-3:]

    jobid = int(job[0].split()[0])
    jobowner = job[0].split()[3]
    jobname = job[1].split("Full jobname:")[1].strip()
    jobpartition, jobnode = job[2].split("Master Queue:")[1].strip().split("@")

    print(jobid, jobowner, jobname, jobpartition, jobnode)

    node_dict[jobnode] = {
        "jobid": jobid,
        "jobowner": jobowner,
        "jobname": jobname,
        "jobpartition": jobpartition,
        "jobnode": jobnode,
    }

for key, val in node_dict.items():
    print(key, val)

# -- NODES --
x = check_output("qstat -f | grep .q@x", shell=True).decode().splitlines()
ssh_list = [i.split()[0].split("@")[1] for i in x]
ssh_list = [i for i in ssh_list if i not in node_dict.keys()]
print(ssh_list)


# -- SWEEPING --
def isweep(target):
    try:
        k = f"Acting on target: {target: <7}"
        return k + " report : something"
    except Exception as e:
        return f"Error on {target}: {e}"


with ProcessPoolExecutor(max_workers=2) as executor:
    # Submit the tasks to the executor using map
    results = list(executor.map(isweep, ssh_list))

for r in results:
    print(r)
