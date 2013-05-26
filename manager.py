import os

from binascii import hexlify
import paramiko
import yaml



class Manager():
    def __init__(self):
        paramiko.util.log_to_file('ssh_manager_sftp.log')
        self.client    = None
        self.transport = None
        self.config    = None
        self.config_path = '/home/stealth/programming/ssh_manager'
        

    def run(self):
        self.read_config(self.config_path)
        self.parse_config()


    def read_config(self, config_path):
        skc_path = '%s/skc' % (config_path)
        assert os.path.exists(skc_path)

        with open(skc_path, 'r') as config:
            self.config = yaml.load(config.read())


    def parse_config(self):
        total_users = len(self.config.keys())
        print "total users:", total_users

        for user in self.config.keys():
            print "checking for local key (%s)" % (user)
            
            if os.path.exists('%s/%s/pub_key' % (self.config_path, user)):
                for host in self.config[user]:
                    print '[copying] local -> %s' % (host)
                    #copy it 

            else:
                print 'could not find the public key'
                # prompt to generate or autogen if config says so


    
        
    
    def add_authorized_key(self, username, hostname):
        pass


    def check_key_present(self, username, hostname):
        if not self.client:
            self.connect(username, hostname)

        ssh_key_file = self.sftp.file('/home/%s/.ssh/authorized_keys' % (username)).read()

        # 0 type
        # 1 key
        # 2 host

        keys = ssh_key_file.splitlines()

        print "found %s keys" % (len(keys))
        for key in keys:
            print key.split()[0:2]
        

        
        

    def connect(self, username, hostname, port=22, password=None):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
      
        print "connecting to %s as %s" % (hostname, username)
        self.client.connect(username=username, hostname=hostname) 

        self.transport = self.client.get_transport()
        
        self.sftp = self.client.open_sftp()



        


# generate the key for the remote system, don't keep locally (leave it on remote system)
# copy remote public key to local so it can be distributed
# have ability to copy our public key to remote system so we can get back in (if somebody is initially using passwords)

m = Manager()
m.run()
