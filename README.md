# Introduction
Weblogic 12c for SAE applications like Audit.  

# Getting Started
TODO: 
1.	On ansible server. Install git, ansible, sshpass, azure devops agent, etc.  Make user for ansible server and destinations the same.
2.	Established the ansible server connectivity to the destinations.
3.	Setup the pipeline.  Create token, create the build using bash, ansible_user variable, etc.

# Build and Test

- VSTS build and release pipeline (overall) using bash:

Step 1 -Initial Setup 
  WLS-automation/files/setup.sh $(ansible_password)
Step 2 -Install Weblogic Servers
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t install_weblogic -e 'ansible_become_pass=$(ansible_password)' audit.yml
Step 3 -Clean Domain Folders
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t clean -e 'ansible_become_pass=$(ansible_password)' audit.yml
Step 4 -Build Weblogic
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t build -e 'server=admin ansible_become_pass=$(ansible_password)' audit.yml
Step 5 -Start Weblogic Admin
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t start -e 'server=admin ansible_become_pass=$(ansible_password)' audit.yml
Step 6 -Configure Weblogic
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t config -e 'ansible_become_pass=$(ansible_password)' audit.yml
Step 7 -Restart Weblogic Admin
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t restart -e 'server=admin ansible_become_pass=$(ansible_password)' audit.yml
Step 8 -Deploy Apps
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t deploy -e 'ansible_become_pass=$(ansible_password)' audit.yml
Step 9 -Start Managed Servers
  cd ./WLS-automation
  ansible-playbook -v -i hosts -t start_managed -e 'ansible_become_pass=$(ansible_password)' audit.yml  
  
Note: If you will be running on the CLI/linux instead of pipeline/Azure Devops, replace the "$(ansible_password)" to your actual "pasword".   


# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://www.visualstudio.com/en-us/docs/git/create-a-readme). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)
# weblogic
# weblogic
