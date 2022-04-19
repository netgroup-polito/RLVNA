# RLVNA: An NGI-funded Project

## Project Structure
This repository is structured as follows:
```
├── api
│   ├── ...
│   ├── geni_utilities
|   |   ├── geni-lib-updated
|   ├── requirements.txt
│   └── mystique
├── examples
├── frontend
|   ├── src/components
|   ├── App.js
│   └── src/utilities
└── manage.py
```

Analyzing what each directory contains:
- ``` manage.py ``` is the script used for running the backend.
- ``` examples ``` contains the results of the experiment run into GENI and examples.
- ``` frontend/src/App.js  ``` is the entry point of the frontend react application
- ``` frontend/src/components ``` containts GoJS, Topology, and Settings components.
- ``` frontend/src/utilities ``` containts CSS and the classes used for passing parameters from the frontend to the backend.
- ``` api/geni_utilities/my_context.py ``` containts the GENI configuration username and PW used in this project
- ``` api/geni_utilities/config_geni.py ``` containts EVERY call used to interact with GENI
- ``` api/geni_utilities/geni-lib-updated  ``` contains the files changed to allow geni-lib to run in python3 (it was designed to run in python2 only.)

However, the overall project uses some material in:
- https://github.com/Enrico-git/NGI-support

While the main code is in this first repository, the second **public** repository is used only for minor purposes like GENI node (controller, switches, host) configuration.

# Run the project
To run the project it is needed to follow these steps:

1. Run the virtual environment with all the backend requirements
2. Run the backend
3. Run the frontend

## 1. create and use *venv*
The virtual environment is useful to create a container where to install requirements without inserting it in the real machine. 

For running the backend you need to install: ```api/requirements.txt```.
Then _probably_ you have to change some files in the "venv/geni-lib" as reported in "geni-lib-updated". (See also 'edit to geni-lib for working with python3').

```bash
$ virtualenv venv
$ source venv/bin/activate
$ which python -> should show venv version
$ pip3 install -r requirements.txt
$ deactivate
```

## edit to geni-lib for working with python3
```
in '.../venv/lib/python3.8/site-packages/geni/aggregate/context.py' on line 63 
in '/venv/lib/python3.8/site-packages/geni/aggregate/context.py' on line 234
    -> update wb+ to w+
```
```
in '.../venv/lib/python3.8/site-package/geni/rspec/pg.py, on line 90
in '.../venv/lib/python3.8/site-packages/geni/rspec/pgmanifest.py' on line 259 in writeXML
    -> change w+ to wb+
```

'Document is Empty' -> rm -rf .bssw/

## Generate the key and cert for access GENI and run the backend
From ```api/geni_utilities/mycontext.py``` it is possible to specify the keys and certificates needed for the geni-lib for communicationg with GENI testbed.

After the registration to GENI testbed, login and get the following information.
From the Profile/Account_Summary and project:
- user.name = "..."
- user.urn = "urn:publicid:IDN+ch.geni.net+user+..."
- context.project = "..."

From SSL download the 'geni.pem' file and insert the path into:
- framework.cert = ".../geni-.pem"
- framework.key = ".../geni-.pem"

It is important to upload the public key into GENI (SSH Keys). Futhermore, insert the path of the public key into : 
- user.addKey(".../id_ed25519.pub")

For generating the key pair I suggest: 
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent


## Access the RLVNA container
You can explore the RLVNA algorithm from: ```docker push enrico2docker/ubuntu-mystique:1.4```

## 2. Run the backend
Since some paths are defined starting from the **RLVNA directory** it's important you run everything from this directory.

```
(venv)$ ~/RLVNA$ python3 manage.py runserver
```

## 3. Run the frontend
In this case, run the command from the **frontend directory**.

```
~/RLVNA/frontend$ npm install
~/RLVNA/frontend$ npm run dev
```

Now, going to http://127.0.0.1:8000/ you can access the web platform.

# Running an experiment

## 1. Create a new slice
Once the backend is running, you can use the button on the frontend (Work in progress) or you can execute a curl request.

Before starting, you can customize some geni settings. 
In ``` api/config.ini ``` it is possible to change the *slice name* you want to create and the *aggregate* to use (
    https://geni-lib.readthedocs.io/en/latest/_modules/geni/aggregate/instageni.html#IGCompute
).

NOTE: It's important to create a slice from GENI portal, in order to pass the slice name.

To create a new slice, this is an example of a curl request:
```bash
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"topology":"{\"ctrl\":{\"c0\":{\"s0\":[\"h0\",\"h1\"],\"s1\":[\"h2\",\"h3\"],\"s2\":[\"h4\",\"h5\"],\"s3\":[],\"s4\":[],\"s5\":[],\"s6\":[\"h6\",\"h7\"],\"s7\":[\"h8\",\"h9\"]}},\"links\":{\"s0\":[\"s1\",\"s2\",\"s3\"],\"s1\":[\"s0\",\"s7\"],\"s2\":[\"s0\",\"s4\",\"s5\"],\"s3\":[\"s0\",\"s6\",\"s7\"],\"s7\":[\"s1\",\"s3\",\"s5\"],\"s4\":[\"s2\",\"s6\"],\"s5\":[\"s2\",\"s6\",\"s7\"],\"s6\":[\"s3\",\"s4\",\"s5\"]},\"num_ctrl\":1,\"num_sw\":8,\"num_h\":10,\"num_link\":32}"}' \
"127.0.0.1:8000/api/topology"
```

As you can see, the topology requested is parsed in JSON and sent as a body in the POST request.

Through this curl request, the "create_topology()" function from the config_geni.py file is invoked. All the needed nodes are requested to the target aggregate and when they are ready, they are also configured. In particular, the controller node downloads the docker engine and the image; the OVS switches nodes map the physical port with the OVS port and set the IP address of the controller. The host nodes download the available scripts for the traffic generator. Both tree kind of nodes download and uses the scripts available in the public repository *NGI-support*.

## 2. Configuring an experiment
Once the nodes are correctly reserved, you need further configuration. Other scripts in NGI-support are invoked.
## 2.1 Configure Ryu controller
Inside the GENI controller node, you have a docker (see below) which contains all the code available to run the RLVNA algorithm.
Before run the RLVNA algorithm, you have to run the configuration, such that the config.ini files are properly generated.

To create configure Ryu, this is an example of a curl request:
```bash
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"support_switches":"s3,s5","data_frequency":1}' \
"127.0.0.1:8000/api/ryu"
```

In this example, you are configuring the Ryu controller to have two support switches 's3' and 's5' and, to collect data every '1 second'.

## 2.2 Configure Model
Inside the GENI controller node, you have a docker which contains all the code available to run the RLVNA algorithm.
Before run the RLVNA algorithm, you have to run the configuration, such that the config.ini files are properly generated.
In the docker, consider that 'Miniconda' are already provided. This tool is mandatory to run 'Keras' and 'TensorFlow' needed in the machine learning model present in RLVNA algorithm. 

To create and configure the model, this is an example of a curl request:
```bash
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"num_support_switches":2,"op_penalty":300, "helped_switches":"4,1,2", "data_frequency":1}' \
 "127.0.0.1:8000/api/model"
```

In this example, you are configuring the model to have two support switches, to ask for collected data every '1 second', a list of helped switches, and the overprovisioning penalty to use.

**IMPORTANT NOTE:** Be careful that another parameter to configure is hidden for the moment. The idea is to automatize it but for the moment you have to configure the number of interfaces available in the whole network manually! You can find this parameters inside ```config_geni.py / configure_model() / NumIntf=...```

## 2.3 Configure Hosts

The GENI host nodes have the scripts available in NGI-support and the proper requirements (like iperf3) already installed. 

This is an example of a curl request:

```bash
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"iperf_num":"15","traffic_type":"train"}' \
"127.0.0.1:8000/api/traffic"
```

This request was designed for running the traffic generator in each node, but **it doesn't work.**
After many hours of testing, we realized that you have to manually open many shells and run each with ssh and the script for generating the traffic. 

This curl request for the moment, generates the SSH command of each host and their IP addresses inside ```api/minor_utilities/login*.txt```

# Collecting statistics from an experiment
NOTE: For now on, you could even shut down the backend(and frontend of course). 

Once generated the ssh login.txt file, you could open **one shell window for each host** and two for the controller. You can use also ```api/minor_utilities/login.sh``` for support. 

IMPORTANT NOTE: We realized that iperf3 is not good for testing RTT. We decided to use netperf.
You can find an example in ```NGI-support/config_host_static.py```

## Without RLVNA
In this case, you don't have to run the model.
Open the controller ssh and access inside the docker container for running the Ryu controller: 
```bash
s279434@c0:~$ sudo docker container ls
s279434@c0:~$ sudo docker exec -it mystique bash
root@f1518a123e80:/mystique# cd ryu_controller/
root@f1518a123e80:/mystique/ryu_controller# ryu-manager controller.py
```
These commands, access the docker and run the controller.py which deletes previous flows and configures the default shortest paths on each OVS switch.

Now, all OVS switches have their flows. It's possible to run the traffic generator. 

**NOTE**: If you use an  aggregate different from clemson-ig, you should change it in 'omni hack' in ```/network/configuration_v1.py ```

Run this command - adapting what needs to be adapted - in each ssh host shell:
```bash
s279434@h0:~$ python3 /NGI-support-main/config_host_static.py test 10 h0 192.168.0.2,192.168.0.4,192.168.0.9,192.168.0.11,192.168.0.15,192.168.0.17,192.168.0.30,192.168.0.32,192.168.0.37,192.168.0.39
```

config_host_static.py available in NGI-support, needs the kind of traffic (train/test), the amount of experiment for each bandwidth (10 * 10Mbps, 10 * 20Mbps, etc), the host who is running the script (h0, h1, etc) and the list of all hosts separated by a comma.

When the script terminates, you can find in h0 the measurement. You have to download this file (and remove it before run the next experiment).

To download the file, this is the curl request:

```bash
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"file":"traffic"}' \
"127.0.0.1:8000/api/download"
```

The download files, are inside ```collected_data/exp/```. Remove from this directory before downloading next files.

## With RLVNA
In this case, you have to run the model.
Open two controller ssh and access inside the docker container for running the ryu controller and the mode: 
```bash

SHELL 1
s279434@c0:~$ sudo docker container ls
s279434@c0:~$ sudo docker exec -it mystique bash
root@f1518a123e80:/mystique# cd ryu_controller/
root@f1518a123e80:/mystique/ryu_controller# ryu-manager controller.py

SHELL 2
s279434@c0:~$ sudo docker container ls
s279434@c0:~$ sudo docker exec -it mystique bash
root@f1518a123e80:/mystique# cd model/
root@f1518a123e80:/mystique/model# conda activate conda_venv
(conda_venv)root@f1518a123e80:/mystique/model# python3 train_centralized.py

 -and later - 

(conda_venv)root@f1518a123e80:/mystique/model# python3 test_centralized.py
```
These commands, access the docker and run the Ryu controller.py which deletes previous flows and configures the default shortest paths on each OVS switch.
Then activate the conda virtual environment (Keras, TensorFlow) and execute the train or the test.

Now, all OVS switches have their flows. It's possible to run the traffic generator. 

**NOTE**: If you use an  aggregate different from clemson-ig, you should change it in 'omni hack' in ```/network/configuration_v1.py ```

Run this command - adapting what needs to be adapted - in each ssh host shell:
```bash
s279434@h0:~$ python3 /NGI-support-main/config_host_static.py train 5 h0 192.168.0.2,192.168.0.4,192.168.0.9,192.168.0.11,192.168.0.15,192.168.0.17,192.168.0.30,192.168.0.32,192.168.0.37,192.168.0.39
```

config_host_static.py available in NGI-support, needs the kind of traffic (train/test), the amount of experiment for each bandwidth (5 * 10Mbps, 5 * 20Mbps, etc), the host who is running the script (h0, h1, etc) and the list of all hosts separated by a comma.

When the script terminates, you can find in h0 the measurement. You have to download this file (and remove it before running the next experiment).

To download the measurement and the reward, this is the curl request:

```bash
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"file":"traffic"}' \
"127.0.0.1:8000/api/download"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"file":"reward"}' \
"127.0.0.1:8000/api/download"
```
The downloaded files are inside ```collected_data/exp/```. Remove from them before downloading next files.

In this case, since the model is activated, sometimes mystique's action 1 is available and it means that an alternative path is available for reaching the destination. 

NOTE: Try to have several traffic generator for each bandwidth comparable with the time of the model.
Example: each iperf3 is 2 min; if you want 2 times for each band, 2 * 2 min * 10 bandwidth = 40 minutes. You have to adapt the sim_time and episodes inside the train_centralized.py and test_centralized.py to take at least 40 minutes 


# Checking path of the traffic
NOTE: For now on, you could even shut down the backend(and frontend of course). 

Once generated the ssh login.txt file, you could open one shell window for each SWITCH and two for the controller.

Inside the controller node, run this command for *resetting all flows*:
```bash
s279434@c0:~$ sudo docker exec -it mystique bash
root@f1518a123e80:/mystique# cd ryu_controller/
root@f1518a123e80:/mystique/ryu_controller# ryu-manager controller.py
```


Run this command - adapting what needs to be adapted - in each ssh switch shell:
```bash
s279434@s0:~$ sudo ovs-ofctl dump-flows s0
```

This commands, *shows* all the flows present in the switches. 

Finally, run this command in ALL switches to check which path is used for communication:
```bash
s279434@s0:~$ sudo tcpdump -i any host h1 or host h2 or host h3 or host h4 or host h5 or host h6 or host h7 or host h8 or host h9
```

Of course, while using this command in the switches, remember to run iperf3/ping in an host.


----------------

_NOTE: For further details you can contact me at:_
_**enrico.alberti@studenti.polito.it**_
