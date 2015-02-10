import os

# Creates the hawq user if it doesn't already exist and changes the password.
# FIXME Find a better way to do this without os.system calls if possible. Handle error checking.
def hawq_useradd():
  import params
  os.system("/usr/sbin/useradd "+params.hawq_user +" 2> /dev/null")
  os.system("echo -e \""+params.hawq_password+"\n"+ params.hawq_password+"\" | passwd "+params.hawq_user + " 2>/dev/null")
  os.system("/usr/sbin/usermod -a -G hdfs "+params.hawq_user)
  os.system("echo "+ params.source_cmd +" >> /home/"+params.hawq_user+"/.bashrc")


def hawq_modify_kernel_parameters():
  # These need to be appended to the sysctl_conf_file so they load on the next reboot for the machines but they also need to
  # be looped through and ran with the sysctl -w system command so they take effect immediately. That way the system 
  # doesn't require a reboot during the install. Note: do not set the vm.overcommit_memory parameter if you run HAWQ on
  # small memory virtual machines. If you set this parameter you may encounter out of memory issues.
 
  # The way this should most efficiently be done is run the command with sysctl and if it's return code is 0, then add the parameter
  # to the sysctl_conf_file, otherwise, do not.
  
  #sysctl.kernel.shmmax = 500000000
  #sysctl.kernel.shmmni = 4096
  #sysctl.kernel.shmall = 4000000000
  #sysctl.kernel.sem = 250 512000 100 2048
  #sysctl.kernel.sysrq = 1
  #sysctl.kernel.core_uses_pid = 1
  #sysctl.kernel.msgmnb = 65536
  #sysctl.kernel.msgmax = 65536
  #sysctl.kernel.msgmni = 2048
  #sysctl.net.ipv4.tcp_syncookies = 0
  #sysctl.net.ipv4.ip_forward = 0
  #sysctl.net.ipv4.conf.default.accept_source_route = 0
  #sysctl.net.ipv4.tcp_tw_recycle = 1
  #sysctl.net.ipv4.tcp_max_syn_backlog = 200000
  #sysctl.net.ipv4.conf.all.arp_filter = 1
  #sysctl.net.ipv4.ip_local_port_range = 1025 65535
  #sysctl.net.core.netdev_max_backlog = 200000
  #sysctl.vm.overcommit_memory = 2
  #sysctl.fs.nr_open = 3000000
  #sysctl.kernel.threads-max = 798720
  #sysctl.kernel.pid_max = 798720
  ##increase network
  #sysctl.net.core.rmem_max = 2097152
  #sysctl.net.core.wmen_max = 2097152

  # For RHEL version 6.x platforms, the above parameters do not include the sysctl. prefix, as follows:
  #kernel.shmmax = 500000000
  #kernel.shmmni = 4096
  #kernel.shmall = 4000000000
  #kernel.sem = 250 512000 100 2048
  #kernel.sysrq = 1
  #kernel.core_uses_pid = 1
  #kernel.msgmnb = 65536
  #kernel.msgmax = 65536
  #kernel.msgmni = 2048
  #net.ipv4.tcp_syncookies = 0
  #net.ipv4.ip_forward = 0
  #net.ipv4.conf.default.accept_source_route = 0
  #net.ipv4.tcp_tw_recycle = 1
  #net.ipv4.tcp_max_syn_backlog = 200000
  #net.ipv4.conf.all.arp_filter = 1
  #net.ipv4.ip_local_port_range = 1025 65535
  #net.core.netdev_max_backlog = 200000
  #vm.overcommit_memory = 2
  #fs.nr_open = 3000000
  #kernel.threads-max = 798720
  #kernel.pid_max = 798720
  ## increase network
  #net.core.rmem_max=2097152
  #net.core.wmem_max=2097152
  print "This function needs to be written still - hawq_modify_kernel_parameters()"

def hawq_modify_security_parameters():
  print "This function needs to be written still - hawq_modify_security_parameters()"
  # Append this to the security_conf_file exactly as shown:
  #soft nofile 2900000
  #hard nofile 2900000
  #soft nproc 131072
  #hard nproc 131072

def hawq_modify_mount_options():
  print "This function needs to be written still - hawq_modify_mount_options()"
  # Please see http://pivotalhd.docs.pivotal.io/doc/2010/InstallingHAWQ.html#InstallingHAWQ-InstalltheHAWQBinaries
  # and scroll down to the XFS section. It talks about mount options, io schedulers, blockdev, etc. 
  # All of this is extremely important to set in a production environment, but not as important to test hawq. 
  # It should still be set though even in testing so that the performance is best as possible to show how awesome
  # hawq is.

def hawq_create_gpinitsystem_config():
  import params
  os.system("mkdir -p " + params.gpconfigs_dir)
  os.system("chown -R "+ params.hawq_user +" "+params.gpconfigs_dir)
  f = open(params.gpinitsystem_config_file, 'w')
  if f:
    f.write("# Auto-generated by zData\n");
    f.write("ARRAY_NAME="+str(params.ARRAY_NAME)+"\n");
    f.write("SEG_PREFIX="+str(params.SEG_PREFIX)+"\n");
    f.write("PORT_BASE="+str(params.PORT_BASE)+"\n");
    f.write("declare -a DATA_DIRECTORY=(" + params.DATA_DIRECTORY+")\n");
    f.write("MASTER_HOSTNAME="+str(params.MASTER_HOSTNAME)+"\n");
    f.write("MASTER_DIRECTORY="+str(params.MASTER_DIRECTORY)+"\n");
    f.write("MASTER_PORT="+str(params.MASTER_PORT)+"\n");
    f.write("TRUSTED_SHELL="+str(params.TRUSTED_SHELL)+"\n");
    f.write("CHECK_POINT_SEGMENTS="+str(params.CHECK_POINT_SEGMENTS)+"\n");
    f.write("ENCODING="+str(params.ENCODING)+"\n");
    f.write("DATABASE_NAME="+str(params.DATABASE_NAME)+"\n")
    f.write("MACHINE_LIST_FILE="+str(params.MACHINE_LIST_FILE)+"\n")
    f.write("DFS_NAME="+str(params.DFS_NAME)+"\n")
    f.write("DFS_URL="+str(params.DFS_URL)+"\n")
    f.write("KERBEROS_KEYFILE="+str(params.KERBEROS_KEYFILE)+"\n")
    f.write("ENABLE_SECURE_FILESYSTEM="+str(params.ENABLE_SECURE_FILESYSTEM)+"\n")
    f.close()
  else:
    sys.exit("Install error: Cannot open "+ params.gpinitsystem_config_file + "for writing.")


