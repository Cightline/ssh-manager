import os
import argparse

from binascii import hexlify
import paramiko
import yaml



class Manager():
    def __init__(self, ssh_pass=None, overwrite=False, ignore_host_keys=False):
        paramiko.util.log_to_file('ssh_manager_sftp.log')
        self.client    = None
        self.transport = None
        self.config    = None
        self.ssh_pass  = ssh_pass
        self.overwrite = overwrite
        self.host_keys_path   = os.path.expanduser('~/.ssh/known_hosts')
        self.ignore_host_keys = ignore_host_keys
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
            username, hostname = user.split('@')

            key_type = self.config[user]['type']
            target_key_path = '/%s/%s/%s/%s' % (self.config_path, hostname, username, key_type)

            if os.path.exists(target_key_path):
                for target in self.config[user]['targets']:
                    self.msg('checking for local key from: %s' % (target))

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


                
            if 'store_key' in self.config[user]:

                if 'overwrite' in self.config[user]:
                    self.get_public_key(info[0], info[1], key_type, overwrite=True)
               
                else:
                    self.get_public_key(info[0], info[1], key_type)



    def get_public_key(self, username, hostname, key_type, overwrite=False):
        self.msg('attempting to store %s' % (key_type))
        if not self.client:
            self.connect(username, hostname)

        try:
            self.sftp.stat('/home/%s/.ssh/%s' % (username, key_type))

        except IOError as e:
            # File does not exist
            if e.errno == 2:
                self.msg('key type: %s does not exist on %s' % (key_type, hostname), 1)

                return False
    
        f = self.sftp.file('/home/%s/.ssh/%s' % (username, key_type), 'r')
        pub_key = f.read()
        f.close()

        self.save_public_key(username, hostname, key_type, pub_key, overwrite)
   


    def save_public_key(self, username, hostname, key_type, key_contents, overwrite=False):

        key_path = '%s/%s/%s/%s' % (self.config_path, hostname, username, key_type)
        key_dir  = '%s/%s/%s' % (self.config_path, hostname, username)

        # If the key exists locally and we don't want to overwrite, return True
        if os.path.exists(key_path):
            if overwrite == False and self.overwrite != True:
                return True

        
        elif not os.path.exists(key_dir):
            os.makedirs(key_dir)

        # Otherwise we should save the key 
        with open('%s/%s/%s/%s' % (self.config_path, hostname, username, key_type), 'w') as to_write:
            to_write.write(key_contents)
            self.msg('saving public key on %s type %s' % (username, key_type), 0)
            
         

    def add_authorized_key(self, username, hostname, target_key):
        f = self.sftp.file('/home/%s/.ssh/authorized_keys' % (username), 'a')
        f.write(target_key)
        f.close()
        
        

    def key_present(self, username, hostname, target_key):
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
                self.msg("user: %s, host: %s authorized_keys contains correct key" % (username, hostname))
                return True


        return False 
        

    def connect(self, username, hostname, port=22, password=None, allow_agent=True):
        self.client = paramiko.SSHClient()
        self.msg('loading host keys from: %s' % (self.host_keys_path))
        self.client.load_host_keys(self.host_keys_path)
        self.client.set_missing_host_key_policy(self)
        
      
        self.msg("connecting to %s as %s" % (hostname, username), 0)


        # Use self.ssh_pass if no password was given 
        if password == None and self.ssh_pass != None:
            password = self.ssh_pass
       
        try:
            self.client.connect(username=username, hostname=hostname, password=password)

        except paramiko.SSHException as e:
            self.msg(e, 2)
            exit()
            
        

        self.transport = self.client.get_transport()
        
        self.sftp = self.client.open_sftp()

    def missing_host_key(self, client, hostname, key):
        self.msg('could not verify host key from: %s, self.ignore_host_keys == %s' % (hostname, self.ignore_host_keys))

        if self.ignore_host_keys == True:
            return 

        elif raw_input('continue [y/n]: ') == 'yes' or 'y':
            return

        else:
            exit()


# generate the key for the remote system, don't keep locally (leave it on remote system)
# copy remote public key to local so it can be distributed
# have ability to copy our public key to remote system so we can get back in (if somebody is initially using passwords)

