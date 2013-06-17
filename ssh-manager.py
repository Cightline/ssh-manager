
import argparse
import manager


parser = argparse.ArgumentParser(description='Options for ssh-mgr')

parser.add_argument('-k', dest='ssh_pass', action='store', help='password to use when connecting')
parser.add_argument('-g', dest='remote_target', action='store', 
                    help='retrieve a remote public key and store it locally')

parser.add_argument('-o', dest='overwrite', action='store_true', default='store_false')
parser.add_argument('-i', dest='ignore_host_keys', action='store_true', default='store_false')

args = parser.parse_args()


m = manager.Manager(ssh_pass=args.ssh_pass, 
                    overwrite=args.overwrite, 
                    ignore_host_keys=args.ignore_host_keys)

m.run()
