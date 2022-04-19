import api.geni_utilities.mycontext as mycontext #NOTE run from NGI dir only
import json
import time
import geni.aggregate.instageni as IGAM
import geni.rspec.pg as PG
import geni.rspec.igext as IGX

import paramiko     #open ssh connection for docker config
from scp import SCPClient # copy traffic from h0
import xmltodict    #read omni listresource xml
from datetime import datetime

import os 
import configparser     #slice, aggregate from config.ini

class Experiment:
    def __init__(self):
        # self.target_aggregate = IGAM.Clemson
        # self.target_aggregate = IGAM.Colorado
        # self.target_aggregate = IGAM.Chicago # HTTPSConnectionPool(host='geni.uchicago.edu', port=12369): Read timed out. (read timeout=60)
        # self.target_aggregate = IGAM.Kansas # Exception
        # self.target_aggregate = IGAM.Stanford # 19 nodes of type pcvm requested, but only 10 available nodes of type pcvm found
        # self.target_aggregate = IGAM.Illinois

        config = configparser.ConfigParser()
        config.read(os.getcwd()+'/api/config.ini')

        read_slice = config['DEFAULT']['slice']
        read_aggregate = config['DEFAULT']['aggregate'].lower()

        aggregates = IGAM.aggregates()
        for aggregate in aggregates: 
            if read_aggregate in aggregate.name:
                self.target_aggregate = aggregate
        
        #self.context = geni.util.loadContext() #from bundle
        self.context = mycontext.buildContext() #from custom context
        # if self.context.project != "network-scalability-tests":
        #     print("geni_init: Error. context not built properly.")
        #     #TODO throw exception.
    
    # This function clear previous instance
    # of nodes reserved in this aggregate
    # and slice. It is an internal function
    # called by create_topology()
    def _delete_previous_aggregate(self):
        while True:
            try:
                print('Clearing from previous sliver...')
                self.target_aggregate.deletesliver(self.context, self.target_slice)
                time.sleep(5)
                status = self.target_aggregate.sliverstatus(self.context, self.target_slice)
                print(status['geni_resources'])
                #Note: if no nodes, sliverstatus -> exception==12
            except Exception as e:
                print(e)
                print(e.data['code']['geni_code'])
                if e.data['code']['geni_code'] == 14 : 
                    print('resource is busy; trying in 30 seconds')
                    time.sleep(30)
                    continue
                elif e.data['code']['geni_code'] == 12 : 
                    print('No such slice here. The aggregate is already empty!')
                    break
                else:
                    time.sleep(5)
                    continue

    # This function waits for resource allocation.
    # This is needed before starting the node
    # customization. It is an internal function 
    # called by create_topology() 
    def _wait_resource_ready(self):
        before_ready = datetime.now()
        # Wait resource ready
        all_ready = False
        while not all_ready:
            try:
                status = self.target_aggregate.sliverstatus(self.context, self.target_slice)
                all_ready = True
                for i in range(len(status['geni_resources'])):
                    status_res_i = status['geni_resources'][i]['geni_status']
                    if status_res_i == 'failed':
                        after_ready  = datetime.now()
                        duration_ready = after_ready - before_ready
                        duration_in_s = duration_ready.total_seconds()
                        print('wait ready minutes: ' + str(duration_in_s/60))
                        return False
                    elif status_res_i != 'ready': #'changing' / 'unknown' / 'notready'
                        all_ready = False
                        print('resources are not ready; trying in 30 seconds')
                        time.sleep(30)
                        break
            except Exception as e:
                if e.data['code']['geni_code'] == 14 : 
                    print('resource is busy; trying in 30 seconds')
                    all_ready = False
                    time.sleep(30)
        after_ready  = datetime.now()
        duration_ready = after_ready - before_ready
        duration_in_s = duration_ready.total_seconds()
        print('wait ready minutes: ' + str(duration_in_s/60))
        return True

    def _find_aggregate(self, needed_resources):
        #The GENI federation provides the ability to request two blocks of information from each aggregate 
        # - the version information             -> pprint.pprint(IGAM.Clemson.getversion(self.context))
        # - a list of the advertised resources  -> advertisement = IGAM.Clemson.listresources(self.context, available=True)

        # target_aggregate = ()
        # print('scanning all aggregates, searching one with ' + str(needed_resources) + ' resources...')
        # for am in IGAM.aggregates():
        #     try:
        #         print('Looking for '+ am.name + ' aggregate...')
        #         adv = am.listresources(self.context, available=True)
        #     except:
        #         print('Aggregate '+ am.name + ' not available!')
        #         continue
        #     print(am.name + ' has ' + str(adv.routable_addresses.available) + ' resources')
        #     print('str(adv.routable_addresses.capacity): ' + str(adv.routable_addresses.capacity))

        #     if adv.routable_addresses.available >= needed_resources : 
        #         target_aggregate = am
        #         break
        
        # if target_aggregate == () :
        #     err_msg = 'IGAM.X.listresources: No available aggregate'
        #     return err_msg
        # return target_aggregate
        pass

    # This function parses the manifest and 
    # defines a list of ssh commands for 
    # connecting to nodes. It is an internal
    # function called by create_topology()
    def _get_ssh(self):
        filepath_manifest = 'manifest_'+self.target_aggregate.name+'_'+self.target_slice+'.xml'
        with open(filepath_manifest) as fd:
            doc = xmltodict.parse(fd.read())
        
        nodes_geni = doc['rspec']['node']
        ip_hosts = ''
        #collect hosts_ip, write SSH
        with open("api/login"+self.target_slice+".txt", "w") as file1:
            for i in range(len(nodes_geni)):
                node_id = doc['rspec']['node'][i]['@client_id']
                if node_id.startswith('h') :
                    node_ip = doc['rspec']['node'][i]['interface']['ip']
                    ip = node_ip['@address']

                    if ip.startswith('192.168'):
                        ip_hosts = ip_hosts+str(ip)+','
                    
                    #SSH file
                    node = doc['rspec']['node'][i]['services']['login']
                    hostname = node['@hostname']
                    port = node['@port']
                    usr = node['@username']
                    file1.write(node_id+'='+ usr+'@'+hostname +' -p '+port+"\n")
            #remove last comma from ip_hosts
            ip_hosts=ip_hosts[0:-1]
            print(ip_hosts)
            file1.write(ip_hosts+"\n")

            for i in range(len(nodes_geni)):
                node_id = doc['rspec']['node'][i]['@client_id']
                if node_id.startswith('c') :
                    #SSH file
                    node = doc['rspec']['node'][i]['services']['login']
                    hostname = node['@hostname']
                    port = node['@port']
                    usr = node['@username']
                    file1.write(node_id+'='+ usr+'@'+hostname +' -p '+port+"\n")
                elif node_id.startswith('s') :
                    #SSH file
                    node = doc['rspec']['node'][i]['services']['login']
                    hostname = node['@hostname']
                    port = node['@port']
                    usr = node['@username']
                    file1.write(node_id+'='+ usr+'@'+hostname +' -p '+port+"\n")

    def create_topology(self, data):
        return 'OK'
        before_allocation = datetime.now()

        #Decode the topology
        data = json.loads(data.topology)
        nodes = data['ctrl']    # {'c0': {'s0': ['h0'], 's1': ['h1'], 's2': ['h2'], 's3': ['h3']}}
        links = data['links']   # {'s0': ['s1', 's3'], 's1': ['s0', 's2'], 's2': ['s1', 's3'], 's3': ['s2', 's0']}
        list_links_intf = {}    #{'s1_s2': [ints1, ints2], 's1_s3': [ints1, ints3]}

        # needed_resources = data['num_h'] + data['num_sw'] + data['num_ctrl'] + data['num_link']
        # target_aggregate = self._find_aggregate(needed_resources)  #check error
        
        print('using aggregate: '+ self.target_aggregate.name + ', slice: ' + self.target_slice)

        self._delete_previous_aggregate()
        
        #Create empty Request
        rspec = PG.Request()

        print('Creating the rspec based by front-end request...')
        print(nodes.items())
        print(links.items())

        #NOTE: I'm using 192.168.0.0/21. 
        # From 192.168.0.1 to 192.168.6.255 for link between SW and SW or SW and Host.
        b=0     # 0 - 6
        c=1     # 0 - 255

        #Controllers
        for ctrl_key, ctrl_value in nodes.items():
            #c0, {'s0': [], 's1': ['h1'], 's2': ['h2'], 's3': ['h3']}
            ctrl_vm = IGX.XenVM(ctrl_key)
            ctrl_vm.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU20-64-STD"
            ctrl_vm.cores=2
            ctrl_vm.ram=4096
                
            ctrl_vm.addService(PG.Install(url='https://github.com/Enrico-git/NGI-support/archive/refs/heads/main.tar.gz', path='/'))
            
            for sw_key, sw_values in ctrl_value.items(): #s1, ['h1']
                #NOTE Using the geni IP addresses 172.17 It's not needed the link to cotroller anymore
                
                #Switches machine
                sw_vm = IGX.XenVM(sw_key)
                sw_vm.disk_image="urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18OVS"
                #NOTE OVS switch configuration done by means of script+ssh
                sw_vm.addService(PG.Install(url='https://github.com/Enrico-git/NGI-support/archive/refs/heads/main.tar.gz', path='/'))

                for i in range(len(sw_values)): #these are the hosts of the sw under loop (sw_values[i] = h0)
                    #switch link to host
                    sw_intf_to_h = sw_vm.addInterface('if_'+sw_key+'_'+sw_values[i])
                    sw_intf_to_h.addAddress(PG.IPv4Address('192.168.'+str(b)+'.'+str(c), '255.255.248.0')) #.0.1
                    c += 1
                    if c > 255:
                        c = 0
                        b += 1 

                    #Hosts machines
                    vm = IGX.XenVM(sw_values[i])
                    h_intf_to_sw = vm.addInterface("if_"+sw_key+'_'+sw_values[i])
                    h_intf_to_sw.addAddress(PG.IPv4Address('192.168.'+str(b)+'.'+str(c), '255.255.248.0'))
                    c += 1
                    if c > 255:
                        c = 0
                        b += 1

                    vm.addService(PG.Install(url='https://github.com/Enrico-git/NGI-support/archive/refs/heads/main.tar.gz', path='/'))
                    # vm.addService(PG.Execute(shell='bash', command='sudo apt update -y ; sudo apt install python3-pip iperf3 -y ; pip3 install iperf3'))
                    
                    link_sw_h = PG.Link()
                    link_sw_h.addInterface(sw_intf_to_h)
                    link_sw_h.addInterface(h_intf_to_sw)

                    rspec.addResource(vm)
                    rspec.addResource(link_sw_h)
                
                #create further interfaces for links between switches
                sw_links = links.get(sw_key)    #get(src) gives the array of destinations
                if sw_links != None:
                    for i in range(len(sw_links)):
                        key_tuple = ''
                        if sw_key < sw_links[i] :
                            key_tuple = sw_key + '_' + sw_links[i]
                        else:
                            key_tuple = sw_links[i] + '_' + sw_key

                        if key_tuple not in list_links_intf.keys():
                            list_links_intf[key_tuple] = []
                        
                        sw_intf_sw_sw = sw_vm.addInterface('if_'+key_tuple)
                        sw_intf_sw_sw.addAddress(PG.IPv4Address('192.168.'+str(b)+'.'+str(c), '255.255.248.0'))
                        c += 1
                        if c > 255:
                            c = 0
                            b += 1

                        list_links_intf[key_tuple].append(sw_intf_sw_sw)

                rspec.addResource(sw_vm)
            
            #when all switches has been created, it's possible to generate the further switch links
            for key in list_links_intf:
                link_sw_sw = PG.Link()
                for intf in list_links_intf[key]:
                    link_sw_sw.addInterface(intf)
                rspec.addResource(link_sw_sw)

            rspec.addResource(ctrl_vm)  #the controller has to add all interfaces before being created
        
        print('Generating Rspec file...')
        rspec.writeXML('rspec-test_'+self.target_aggregate.name+'_'+self.target_slice+'.xml')

        try:
            print('Asking for resource reservation...')
            manifest = self.target_aggregate.createsliver(self.context, self.target_slice, rspec)
        except Exception as e:
            print(e)
            return 'IGAM.X.createsliver: Not possible to reserve resource'

        manifest.writeXML("manifest_"+self.target_aggregate.name+"_"+self.target_slice+".xml")
        after_allocation  = datetime.now()
        duration_allocation = after_allocation - before_allocation
        duration_in_s_A = duration_allocation.total_seconds()
        print('wait ready minutes: ' + str(duration_in_s_A/60))

        print('Geni resource has been allocated but not ready yet...')        
        ret = self._wait_resource_ready() #TODO while waiting the others, ready hosts could be configured.
                                         # It could same a lot of time especially if c0 is ready soon.
                                         # configured_nodes[num_node] = []
                                         # if node == ready and not in configured_nodes: 
                                         #  ssh_config(node); 
                                         #  configured_nodes.append(node)
        if ret == False:
            return 'Error. Some Geni node failed to boot'

        print('Geni resource has been allocated and are ready!')
        # create login file
        self._get_ssh()

        # Handle docker and get IP_CTRLS_GENI for setting OVS-sw
        ip_ctrls = {}
        doc = xmltodict.parse(manifest.text)
        print(manifest.text)
        nodes_geni = doc['rspec']['node']
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        before_ssh_config = datetime.now()

        print('Installing docker, pulling image, starting...')
        for i in range(len(nodes_geni)):
            node_id = doc['rspec']['node'][i]['@client_id']
            if node_id.startswith('c') : 
                node = doc['rspec']['node'][i]['services']['login']
                hostname = node['@hostname']
                port = node['@port']
                usr = node['@username']

                ssh.connect(hostname, port, usr)

                #Get IP CTRL assigned by geni
                ctrl_ip_geni = "hostname -I"
                stdin, stdout, stderr = ssh.exec_command(ctrl_ip_geni)
                lines = stdout.readlines()[0]  #Blocking call. Wait untile command done.
                splitted_ips = lines.split(' ') #there could be many addresses
                for el in splitted_ips:
                    if el.startswith('172.17'):
                        ip_ctrls[node_id] = el
                        break

                #Install Docker, download image, create container
                config_docker = "bash /NGI-support-main/config_docker.sh"
                stdin, stdout, stderr = ssh.exec_command(config_docker)
                lines = stdout.readlines()  #Blocking call. Wait untile command done.
                print(lines)

                ssh.close()

        #After receiving IP CTRL, set OVS switches
        print('Setting controller to OVS switches...')
        for i in range(len(nodes_geni)):
            node_id = doc['rspec']['node'][i]['@client_id']
            if node_id.startswith('s') :
                node = doc['rspec']['node'][i]['services']['login']
                hostname = node['@hostname']
                port = node['@port']
                usr = node['@username']
                
                ssh.connect(hostname, port, usr)
                for ctrl_name in nodes:
                    if node_id in nodes[ctrl_name]:
                        IP_CTRL = ip_ctrls[ctrl_name]
                        break
                
                cmd_set_ctrl='bash /NGI-support-main/config_ovs.sh '+ str(IP_CTRL) + ' ' + node_id
                stdin, stdout, stderr = ssh.exec_command(cmd_set_ctrl)
                lines = stdout.readlines()  #Blocking call. Wait untile command done.
                print(lines)
                ssh.close()
            
        print('Configuring hosts...')
        for i in range(len(nodes_geni)):
            node_id = doc['rspec']['node'][i]['@client_id']
            if node_id.startswith('h') :
                node = doc['rspec']['node'][i]['services']['login']
                hostname = node['@hostname']
                port = node['@port']
                usr = node['@username']

                ssh.connect(hostname, port, usr)
                cmd_req='sudo apt update -y ; sudo apt install python3-pip iperf3 netperf -y ; pip3 install iperf3'
                stdin, stdout, stderr = ssh.exec_command(cmd_req)
                # if int(node_id[1:]) == (int(data['num_h']) - 1 ): #last host
                # lines = stdout.readlines()  # Wait untile command done.
                # print(lines)
                ssh.close()

        after_ssh_config  = datetime.now()
        duration_ssh_config = after_ssh_config - before_ssh_config
        duration_in_s_ssh = duration_ssh_config.total_seconds()
        print('wait docker minutes: ' + str(duration_in_s_ssh/60))

        return 'ok'


    # This function log with ssh into the controller 
    # node and generates the config.ini file used 
    # for mystique Ryu SDN controller
    def configure_controller(self, data):
        ret_msg = 'Controller OK'
        filepath_manifest = 'manifest_'+self.target_aggregate.name+'_'+self.target_slice+'.xml'
        before = datetime.now()
        try:
            with open(filepath_manifest) as fd:
                doc = xmltodict.parse(fd.read())
                nodes_geni = doc['rspec']['node']
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                for i in range(len(nodes_geni)):
                    node_id = doc['rspec']['node'][i]['@client_id']
                    if node_id.startswith('c') : 
                        node = doc['rspec']['node'][i]['services']['login']
                        hostname = node['@hostname']
                        port = node['@port']
                        usr = node['@username']

                        ssh.connect(hostname, port, usr)

                        #TODO receive or parse parameters from front-end
                        data_frequency = ' '+str(data.data_frequency)
                        support_switches=' '+data.support_switches #' #s0,s1,s2
                        slice_name = ' '+self.target_slice
                        split_aggr=self.target_aggregate.name.split('-')
                        aggretate_name = ' '+split_aggr[1]+'-'+split_aggr[0]
                        params=data_frequency+support_switches+slice_name+aggretate_name
                        cmd_config_ryu = '/bin/bash /mystique/ryu_controller/config_ryu.sh'+params #config.ini - ryu_controller
                        cmd_docker_ryu = 'sudo docker exec -d mystique ' + cmd_config_ryu
                        stdin, stdout, stderr = ssh.exec_command(cmd_docker_ryu)
                        lines = stdout.readlines()
                        print(lines)

                        # run ryu-controller (insert OVS flows into SW)
                        # cmd_run_ryu = 'sudo docker exec -d -w /mystique/ryu_controller mystique ryu-manager controller.py'
                        # stdin, stdout, stderr = ssh.exec_command(cmd_run_ryu)
                        # lines = stdout.readlines()
                        # print(lines)

                        ssh.close()
        except Exception as e:
                print(e)
                ret_msg = filepath_manifest + ' not found '
        
        after  = datetime.now()
        duration = ((after - before).total_seconds())/60
        print('wait time: ' + str(duration) + ' min')
        return ret_msg

    # This function count the interfaces
    # in all switches. It called by 
    # configure_model()
    def _get_num_intfs(self):
        num_intfs = 0
        filepath_manifest = 'manifest_'+self.target_aggregate.name+'_'+self.target_slice+'.xml'
        try:
            with open(filepath_manifest) as fd:
                doc = xmltodict.parse(fd.read())
        except Exception as e:
                print(e)
                return filepath_manifest + ' not found '
        nodes_geni = doc['rspec']['node']
        for i in range(len(nodes_geni)):
            node_id = doc['rspec']['node'][i]['@client_id']
            if node_id.startswith('s') : 
                intfs = len(doc['rspec']['node'][i]['interface'])
                num_intfs = num_intfs + intfs
                
        print(num_intfs)
        return num_intfs

    # This function log with ssh into the controller 
    # node and generates the config2.ini file used 
    # for mystique model
    def configure_model(self, data):
        ret_msg = 'Model OK'
        filepath_manifest = 'manifest_'+self.target_aggregate.name+'_'+self.target_slice+'.xml'
        
        before  = datetime.now()
        try:
            with open(filepath_manifest) as fd:
                doc = xmltodict.parse(fd.read())
                nodes_geni = doc['rspec']['node']
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                #config+run model; collect hosts_ip
                for i in range(len(nodes_geni)):
                    node_id = doc['rspec']['node'][i]['@client_id']
                    if node_id.startswith('c') : 
                        node = doc['rspec']['node'][i]['services']['login']
                        hostname = node['@hostname']
                        port = node['@port']
                        usr = node['@username']

                        ssh.connect(hostname, port, usr)

                        #TODO receive or parse parameters from front-end
                        NumIntf=' '+str(self._get_num_intfs()) # NumIntf4SW=' 14' 8SW=' 32'
                        NumSuppSwitch=' '+str(data.num_support_switches)
                        OPPenalty=' '+str(data.op_penalty)
                        HelpedSwitches=' '+data.helped_switches #' 4,1,2'
                        FrequencyData=' '+str(data.data_frequency)
                        cmd_config_model = '/bin/bash /mystique/model/config_model.sh'+NumIntf+NumSuppSwitch+OPPenalty+HelpedSwitches+FrequencyData #config2.ini - model
                        cmd_docker_model = 'sudo docker exec -d mystique ' + cmd_config_model
                        stdin, stdout, stderr = ssh.exec_command(cmd_docker_model)
                        lines = stdout.readlines()
                        print(lines)

                        #run train model
                        # cmd_run_model = 'sudo docker exec -d -w /mystique/model mystique /minicoda3/condabin/conda run -n conda_venv python3 train_centralized.py'
                        # stdin, stdout, stderr = ssh.exec_command(cmd_run_model)
                        # lines = stdout.readlines()
                        # print(lines)
                        #TODO run test

                        ssh.close()
        except Exception as e:
                print(e)
                ret_msg = filepath_manifest + ' not found '
        after  = datetime.now()
        duration = ((after - before).total_seconds())/60
        print('wait time MODEL: ' + str(duration) + ' min')
        return ret_msg

    # This function log with ssh into each host
    # node and download the traffic generator
    # scripts
    def configure_hosts(self, config, traffic_type):
        ret_msg = 'Hosts OK'
        filepath_manifest = 'manifest_'+self.target_aggregate.name+'_'+self.target_slice+'.xml'
        
        before  = datetime.now()

        try:
            with open(filepath_manifest) as fd:
                doc = xmltodict.parse(fd.read())
        except Exception as e:
                print(e)
                ret_msg = filepath_manifest + ' not found '
                after  = datetime.now()
                duration = ((after - before).total_seconds())/60
                print(f'wait time {traffic_type}: ' + str(duration) + ' min')
                return ret_msg
        
        nodes_geni = doc['rspec']['node']
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ip_hosts = ''
        #collect hosts_ip
        for i in range(len(nodes_geni)):
            node_id = doc['rspec']['node'][i]['@client_id']
            if node_id.startswith('h') :
                node_ip = doc['rspec']['node'][i]['interface']['ip']
                ip = node_ip['@address']

                if ip.startswith('192.168'):
                    ip_hosts = ip_hosts+str(ip)+','                            
        #remove last comma from ip_hosts
        ip_hosts=ip_hosts[0:-1]
        print(ip_hosts)

        # TODO It runs the traffic in each hosts. It not works.
        print(f'start host traffic for {traffic_type}')
        for i in range(len(nodes_geni)):
            node_id = doc['rspec']['node'][i]['@client_id']    
            if node_id.startswith('h') and node_id != 'h0' : 
                #Run command and do not wait termination
                node = doc['rspec']['node'][i]['services']['login']
                hostname = node['@hostname']
                port = node['@port']
                usr = node['@username']

                ssh.connect(hostname, port, usr)
                cmd_config='killall python3 /NGI-support-main/config_host_static.py; killall iperf3;'
                cmd_config += ' git clone https://github.com/Enrico-git/NGI-support.git ; sudo rm -rf /NGI-support-main/ ; sudo mv NGI-support/ /NGI-support-main ;'
                # cmd_config += ' sudo apt update -y ; sudo apt install python3-pip iperf3 netperf -y ; pip3 install iperf3'
                stdin, stdout, stderr = ssh.exec_command(cmd_config)
                lines = stdout.readlines() # Wait until command done.
                print(lines)

                args = traffic_type +' '+ str(config.iperf_num) + ' ' + node_id +' '+ ip_hosts
                # cmd_iperf3='python3 /NGI-support-main/config_host_static.py '+ args
                # stdin, stdout, stderr = ssh.exec_command(cmd_iperf3)
                # Don't Wait untile command done.
                ssh.close()
        for i in range(len(nodes_geni)):
            node_id = doc['rspec']['node'][i]['@client_id']    
            if node_id == 'h0' : 
                #Run command and do wait termination
                node = doc['rspec']['node'][i]['services']['login']
                hostname = node['@hostname']
                port = node['@port']
                usr = node['@username']

                ssh.connect(hostname, port, usr)
                cmd_config='killall python3 /NGI-support-main/config_host_static.py; killall iperf3;'
                cmd_config += ' git clone https://github.com/Enrico-git/NGI-support.git ; sudo rm -rf /NGI-support-main/ ; sudo mv NGI-support/ /NGI-support-main'
                stdin, stdout, stderr = ssh.exec_command(cmd_config)
                lines = stdout.readlines() # Wait untile command done.
                print(lines)

                args = traffic_type +' '+ str(config.iperf_num) + ' ' + node_id +' '+ ip_hosts
                # cmd_iperf3='python3 /NGI-support-main/config_host_static.py '+ args
                # stdin, stdout, stderr = ssh.exec_command(cmd_iperf3)
                # lines = stdout.readlines() # Wait untile command done.
                # print(lines)
                ssh.close()
                break
        after  = datetime.now()
        duration = ((after - before).total_seconds())/60
        print(f'wait time {traffic_type}: ' + str(duration) + ' min')
        return ret_msg

    # This function logs inside the target node
    # and downloads the measurement done 
    # during traffic generation. 
    def download_file(self, file):
        ret_msg = 'Download OK'
        filepath_manifest = 'manifest_'+self.target_aggregate.name+'_'+self.target_slice+'.xml'
        
        before  = datetime.now()
        try:
            with open(filepath_manifest) as fd:
                doc = xmltodict.parse(fd.read())
                nodes_geni = doc['rspec']['node']
        except Exception as e:
            print(e)
            ret_msg = filepath_manifest + ' not found '
            return ret_msg

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if file == 'traffic':            
            for i in range(len(nodes_geni)):
                node_id = doc['rspec']['node'][i]['@client_id']    
                if node_id == 'h0' : 
                    node = doc['rspec']['node'][i]['services']['login']
                    hostname = node['@hostname']
                    port = node['@port']
                    usr = node['@username']
                    ssh.connect(hostname, port, usr)
                    with SCPClient(ssh.get_transport()) as scp:
                        scp.get(node_id+'_iperf3_total.txt', local_path='collected_data/exp/')
                    ssh.close()
                    break
        elif file == 'latency':            
            for i in range(len(nodes_geni)):
                node_id = doc['rspec']['node'][i]['@client_id']    
                if node_id == 'h0' : 
                    node = doc['rspec']['node'][i]['services']['login']
                    hostname = node['@hostname']
                    port = node['@port']
                    usr = node['@username']
                    ssh.connect(hostname, port, usr)
                    with SCPClient(ssh.get_transport()) as scp:
                        scp.get('netperf_latency.txt', local_path='collected_data/exp/')
                    ssh.close()
                    break
        elif file == 'rspec':
            pass
        elif file == 'manifest':
            pass
        elif file == 'reward':
            for i in range(len(nodes_geni)):
                node_id = doc['rspec']['node'][i]['@client_id']    
                if node_id.startswith('c') : 
                    node = doc['rspec']['node'][i]['services']['login']
                    hostname = node['@hostname']
                    port = node['@port']
                    usr = node['@username']
                    ssh.connect(hostname, port, usr)

                    cmd_reward='sudo docker cp mystique:/mystique/plot/rewards/cpu_300_rewards.txt .'
                    stdin, stdout, stderr = ssh.exec_command(cmd_reward)
                    lines = stdout.readlines() # Wait untile command done.
                    print(lines)
                    cmd_reward2='sudo docker cp mystique:/mystique/model/model_prints_10test.txt .'
                    stdin, stdout, stderr = ssh.exec_command(cmd_reward2)
                    lines = stdout.readlines() # Wait untile command done.
                    print(lines)
                    cmd_reward3='sudo docker cp mystique:/mystique/model/model_prints_2train.txt .'
                    stdin, stdout, stderr = ssh.exec_command(cmd_reward3)
                    lines = stdout.readlines() # Wait untile command done.
                    print(lines)
                    with SCPClient(ssh.get_transport()) as scp:
                        scp.get('cpu_300_rewards.txt', local_path='collected_data/exp/')
                        scp.get('model_prints_10test.txt', local_path='collected_data/exp/')
                        scp.get('model_prints_2train.txt', local_path='collected_data/exp/')
                    ssh.close()
                    break
        elif file == 'login':
            filepath_login = 'api/'
            filepath_login += file+self.target_slice+'.txt'
            try:
                with open(filepath_login) as fd:
                    file = fd.readlines()
                
                target_list = []
                for el in file:
                    if '=' in el:
                        target_list.append(el)
                
                ret_msg = target_list

            except Exception as e:
                print(e)
                ret_msg = filepath_login + ' not found '
                return ret_msg
        after  = datetime.now()
        duration = ((after - before).total_seconds())/60
        print(f'wait time : ' + str(duration) + ' min')
        return ret_msg