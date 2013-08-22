# Setup tool for temporary used.
# We should use python standart module setuptools in the future.

import os
import sys

def setup_celeryd():
#    print "setup celeryd"
    
    # celeryd sysconfig
    sysconfig = os.path.abspath("conf/celeryd/celeryd.sysconfig")
    cmd = "ln -s {0} /etc/sysconfig/celeryd".format(sysconfig)
    os.system(cmd)
    print cmd

    # celeryd command
    celeryd = os.path.abspath("conf/celeryd/celeryd")
    
    cmd = "chmod a+x {0}".format(celeryd)
    os.system(cmd)
    print cmd

    cmd = "ln -s {0} /etc/init.d/celeryd".format(celeryd)
    os.system(cmd)
    print cmd


def main():
    usage = "Usage: python setup.py install\n"

    if len(sys.argv) != 2 or sys.argv[1] != 'install':
        print usage
        sys.exit(1)

    setup_celeryd()


if __name__ == "__main__":
    main()
