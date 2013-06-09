import os
import argparse

from binascii import hexlify
import paramiko
import yaml



class Manager():
    def __init__(self, ssh_pass=None):
        paramiko.util.log_to_file('ssh_manager_sftp.log')
        self.client    = None
        self.transport = None
        self.config    = None
        self.ssh_pass  = ssh_pass
        self.config_path = '/home/stealth/programming/ssh_manager'
       


    def run(self):
        self.read_config(self.config_path)
        self.parse_config()

    def msg(self, message, level=0):
        levels = ['debug','warning','error','success']
        
        print "[%s] %s " % (levels[level], message)


    def read_config(self, config_path):
        skc_path = '%s/skc' % (config_path)
        assert os.path.exists(skc_path)

        with open(skc_path, 'r') as config:
            self.config = yaml.load(config.read())




    def parse_config(self):
        total_users = len(self.config.keys())

        for user in self.config.keys():

            key_type = self.config[user]['type']
            target_key_path = '%s/%s/%s' % (self.config_path, user, key_type)

            if os.path.exists(target_key_path):
                for target in self.config[user]['targets']:
                    self.msg('checking for key')

                    info = target.split('@')
                  
                    # get the key we need to send 

                    target_key = open(target_key_path, 'r') 
                    target_key_contents = target_key.read()
                    
                    if not self.key_present(info[0], info[1], target_key_contents):
                        self.msg('sending key')
                        
                        self.add_authorized_key(info[0], info[1], target_key_contents)
                        
                        self.msg('success', 3)



            else:
                self.msg('could not find the public key', 1)
                # prompt to generate or autogen if config says so


    
        
    
    def add_authorized_key(self, username, hostname, target_key):
        # I guess if no exception is thrown, then its good ;_;
        f = self.sftp.file('/home/%s/.ssh/authorized_keys' % (username), 'a')
        f.write(target_key)
        f.close()
        
        

    def key_present(self, username, hostname, target_key):
        if not self.client:
            self.connect(username, hostname)

        try:
            self.sftp.stat('/home/%s/.ssh/authorized_keys' % (username))
        except IOError as e:
            # File does not exist
            if e.errno == 2:
                return False 


        ssh_key_file = self.sftp.file('/home/%s/.ssh/authorized_keys' % (username)).read()

        # 0 type
        # 1 key
        # 2 host

        keys = ssh_key_file.splitlines()

        for key in keys:

            if target_key.strip() == key.strip():
                self.msg("key exists")
                return True


        return False 
        

    def connect(self, username, hostname, port=22, password=None, allow_agent=True):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
      
        print "connecting to %s as %s" % (hostname, username)


        # Use self.ssh_pass if no password was given 
        if password == None and self.ssh_pass != None:
            password = self.ssh_pass
        
        self.client.connect(username=username, hostname=hostname, password=password)


        self.transport = self.client.get_transport()
        
        self.sftp = self.client.open_sftp()



        


# generate the key for the remote system, don't keep locally (leave it on remote system)
# copy remote public key to local so it can be distributed
# have ability to copy our public key to remote system so we can get back in (if somebody is initially using passwords)

