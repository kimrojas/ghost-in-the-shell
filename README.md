# ghost-in-the-shell
Utility for managing ghost jobs in smith supercomputer


## Problem desciption
- The `ghost job` problem is very common in the smith cluster and it will hinder the user from running jobs properly.
- The current solution is quite tedious to do since we detect, email the owner of the ghost job, and let them kill it.
- Its time consuming since (1) its hard to detect manually and (2) removing the ghost job does not alleviate the hang state of the calculations (*so we cancel the job and resubmit*).
    
## Cases of ghost jobs
- An available node is occupied by a ghost job (but still considered as available)
- User A has a ghost job running on a node, User B submits a job on the same node, User B's job will be in hang state.
- User A has a ghost job running on a node, User A submits a job on the same node, User A's job (2nd) will be in hang state.

## Utility functions

### Ghostbuster

This function is primarily inteded to kill ghost jobs. There are three ways to use it. 

1. `python3 ghostbuster` - This will kill all of the user's jobs in the current machine with the exception of the python script itself. **NOTE: Run only in compute-nodes, never in login-node**
2. `python3 ghostbuster -p pw.x neb.x` - This will kill all of the user's jobs in the current machine which involves the command `pw.x` or `neb.x`. **NOTE: Run only in compute-nodes, never in login-node**
3. `python3 ghostbuster -t x2020 x2021` - This will send the kill command to the compute nodes `x2020` and `x2021`. **NOTE: It is possible to run anywhere**

> NOTE: the usage #2 and #3, meaning with -p (program) and -t (target) options, can be used together.

### Ghosthunter

This function is intended to be a finder of ghost jobs. There are two modes of operation,  attack and defense. 

1. attack - Check all compute-nodes, except compute-nodes with your legal jobs, for ghost jobs which involves your username. This is the default mode. This help you not become a nuisance to other users.
2. defence - Check all compute-nodes with your legal jobs for ghost jobs involving other users. This is useful in cases where you are the victim of ghost jobs.

### Ghostsweeper

This function is inteded to automate the ghostbuster function in collaboration with ghosthunter. 

First, the ghosthunter will check for infected nodes. Then the ghostbuster will be called to kill the ghost jobs in the infected nodes.

## Useful implementation scenarios

### Best practices

Somtimes, even when the calculations finishes successfully, the process will still be in the system. Maybe due to a problem with the memory releasing and this typically happens for very large calculations. To make sure the your calculations exits cleanly, make sure to include the ghostbuster with program option at the end of you submission script. For example:

```bash
#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -q x17.q
#$ -pe x32 32
#$ -j y
#$ -N jobcalc
#$ -t 1-10

export I_MPI_PIN=1
export OMP_NUM_THREADS=1
export I_MPI_FABRICS=shm:ofi

echo "========= Job started  at `date` =========="

python3 pythonscript.py
mpirun pw.x -in espresso.pwi > espresso.pwo
mpirun neb.x -in espresso.pwi > espresso.pwo

echo "========= Job finished at `date` =========="

# --- CLEANUP ---
python3 ghostbuster -p pw.x neb.x python3s
```





