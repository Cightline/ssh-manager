
import argparse
import manager


parser = argparse.ArgumentParser(description='Options for ssh-mgr')

parser.add_argument('-k', dest='ssh_pass', action='store', help='password to use when connecting')


args = parser.parse_args()

m = manager.Manager(args.ssh_pass)
m.run()
