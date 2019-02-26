#!/bin/bash

#set -x

echo $2 > ./WLS-automation/files/secret

# Get from the repo the hosts
awk 'NF > 0' ./WLS-automation/files/hosts-$2 > ~/host1

# Go to the main path
cd ~/

awk '!/audit_admin|audit_as01|audit_as02|children/{print }' <(cat host1) > host2
awk '!_[$1]++' host2 > host1
sed -i -e 's/ansible_host=//g' host1

if [ ! -f ~/.ssh/id_rsa ]; then
  ssh-keygen -q -f ~/.ssh/id_rsa -N ""
  echo ssh-keygen executed
fi

# Get the two VM
pattern1=`awk 'NR==1{ print $1 }' host1`
awk '{ print  $2 " " $1 }' host1 | sort -nk2 > host2
sed '1d' host2 > host1 
awk '{ print  $2 " " $1 }' host1 | sort -nrk2 > host3
pattern2=`awk 'NR==1{ print $1 }' host3`

if [ ! -f ~/.ssh/known_hosts ]; then
	touch ~/.ssh/known_hosts
	chmod 0644 ~/.ssh/known_hosts
	echo known_hosts created
fi

if grep $pattern1 ~/.ssh/known_hosts </dev/null >/dev/null 2>&1 || grep $pattern2 ~/.ssh/known_hosts </dev/null >/dev/null 2>&1; then
   echo ***One or both server exist: -$pattern1 -$pattern2***
else
   # This will add hosts/ip on /etc/hosts
   if grep $pattern1 /etc/hosts </dev/null >/dev/null 2>&1 || grep $pattern2 /etc/hosts </dev/null >/dev/null 2>&1; then
   	  echo One or two host EXIST! -not added to /etc/hosts
   else
      cat host1 | sudo tee --append /etc/hosts
      echo added hosts to /etc/hosts
   fi

   rpm -qa sshpass > epelx
   if [[ ! -s epelx ]]; then
      sudo yum install sshpass -y
      echo sshpass installed
   fi   
   
   pass=$1
   awk NF host1 > host2
   awk -v password="$pass" '{print "sshpass -p " password " ssh-copy-id -o StrictHostKeyChecking=no " $2}' host2 > sshcopy
   chmod u+x sshcopy
   ./sshcopy
   if [ $? -eq 0 ]; then
    echo sshcopy executed!
   else
    echo ***sshcopy failed!!!***
    echo ***Please do a manual copy of ssh-copy-id on the destinations***
    echo ***or fixed the OPENSSL settings.***
    exit 1
   fi
   
   #rm -f epelx host1 host2 host3 sshcopy

fi
