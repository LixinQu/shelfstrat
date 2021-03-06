#!/bin/env python2.7

import os
import argparse
import itertools

import numpy as np

preamble = '''#!/bin/bash

### Set the job name
#PBS -N shelfstrat 

### Declare myprogram non-rerunable
#PBS -r n

### Set the queue to "default"
#PBS -q default

### Run on 
#PBS -l nodes=1:ppn=8

### You can override the default 1 hour real-world time limit.
#PBS -l walltime=72:00:00

echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR 

echo HOSTNAME: $HOSTNAME
'''


def get_suffix(**kwargs):
    keys = kwargs.keys()
    keys.sort()
    suffix=''
    for key in keys:
        suffix += '_%s_%4.2e' % (str(key), kwargs[key])
    
    return suffix
    
def qsub_case(f, M2, N2):
    suffix = get_suffix(f=f, M2=M2, N2=N2)
    rootdir = './sims_vlfric/shelfstrat%s' % suffix
    
    Ri = N2 * f**2 / M2**2
    phi = M2 * 1e-3 * np.sqrt(Ri) / f**2
    delta = np.sqrt(Ri) * phi
    
    print 'M2 = %4.2e;   N2 = %4.2e;    f = %4.2e;    Ri=%4.2f;   phi=%4.2f' % (M2, N2, f, Ri, phi)
    
    if os.path.exists(rootdir):
        print ' ### DIRECTORY ', rootdir, ' EXISTS'
        return
    
    if not args.dryrun:
        qfile = open('shelfstrat%s.sh' % suffix, 'w')
        qfile.writelines(preamble)
        qfile.write('/anaconda/bin/python2.7 ./run_case.py --rootdir %s --M2 %4.2e --N2 %4.2e --f %f \n' % (rootdir, M2, N2, f))
        qfile.write('/usr/mpi/gcc/openmpi-1.4.3/bin/mpiexec -np 8 ./project/coawstM %s/ocean_shelfstrat.in > %s/ocean_shelfstrat.out\n' % (rootdir, rootdir))
        qfile.close()
        os.system('qsub shelfstrat%s.sh' % suffix)



parser = argparse.ArgumentParser()
parser.add_argument('--M2', type=float, nargs='+',
                   help='Horizontal stratification')
parser.add_argument('--Ri', type=float, nargs='+',
                   help='Richardson number')
parser.add_argument('--delta', type=float, nargs='+',
                   help='Slope parameter')
parser.add_argument('--S', type=float, nargs='+',
                   help='Slope Burger number')
parser.add_argument('--N2', type=float, nargs='+',
                   help='Vertical stratification')
parser.add_argument('--f', type=float, nargs='+',
                   help='Coreolis parameter')
parser.add_argument('--dryrun', action="store_true")
args = parser.parse_args()

alpha = 1.0e-3
z0 = 0.0001

if args.Ri is None and args.delta is None:
    for M2, N2, f in itertools.product(args.M2, args.N2, args.f):
        qsub_case(f, M2, N2)
elif args.Ri is not None and args.delta is not None:
    if args.M2 is not None:
        for Ri, delta, M2 in itertools.product(args.Ri, args.delta, args.M2):
            N2 = M2 * delta / alpha
            f = M2 * np.sqrt(Ri / N2)
            qsub_case(f, M2, N2)
    elif args.N2 is not None:
        for Ri, delta, N2 in itertools.product(args.Ri, args.delta, args.N2):
            M2 = N2 * alpha / delta
            f =  M2 * np.sqrt(Ri / N2)
            qsub_case(f, M2, N2)
    # elif args.f is not None:
    #     for Ri, delta, f in itertools.product(args.Ri, args.delta, args.f):
    #         N2 = foo
    #         f = foo
    #         qsub_case(f, M2, N2)
    # else:
    #     raise, 'Parameters not well formed..'
elif args.Ri is not None and args.S is not None:
    if args.M2 is not None:
        for Ri, S, M2 in itertools.product(args.Ri, args.S, args.M2):
            delta = np.sqrt(Ri) * S
            N2 = M2 * delta / alpha
            f = M2 * np.sqrt(Ri / N2)
            qsub_case(f, M2, N2)
    elif args.N2 is not None:
        for Ri, S, N2 in itertools.product(args.Ri, args.S, args.N2):
            delta = np.sqrt(Ri) * S
            M2 = N2 * alpha / delta
            f =  M2 * np.sqrt(Ri / N2)
            qsub_case(f, M2, N2)




# elif args.M2 is None:
#     for Ri, N2, f in itertools.product(args.Ri, args.N2, args.f):
#         M2 = np.sqrt(N2 * f**2 / Ri)
#         qsub_case(f, M2, N2)
# elif args.N2 is None:
#     for Ri, M2, f in itertools.product(args.Ri, args.M2, args.f):
#         N2 = Ri * M2**2 / f**2
#         qsub_case(f, M2, N2)


