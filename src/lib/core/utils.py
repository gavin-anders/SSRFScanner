'''
Created on 5 Mar 2018

@author: gavin
'''
from lib.core import settings

import os
import sys

def stop_running():
    """
    Kill current process and any background threads
    """
    # kill client threads
    os.kill(os.getpid(), 9)
    
def update():
    """
    Update using the git page
    """
    pass

    
def show_version():
    """
    Show version number and exit.
    """
    print("\n" + settings.VERSION)
    sys.exit(0)


def python_version():
    """
    Check python version number and exit.
    """
    pass