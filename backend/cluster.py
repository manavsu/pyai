import time
import subprocess
from cwd import cwd
import os
from threading import Lock
from threading import Timer

class Node:
    def __init__(self, agent_id, port, api_key):
        self.agent_id = agent_id
        self.port = port
        self.last_pet = time.monotonic()
        self.process = None
        self.spun_up = False
        self.spin_up(api_key)

    
    def pet(self):
        self.last_pet = time.monotonic()
    
    def spin_up(self, api_key):
        agent_env = os.path.join("tmp", self.agent_id)
        
        with cwd(agent_env):
            subprocess.check_call(["python", "-m", "venv", ".venv"])
            subprocess.check_call([os.join('.venv', 'bin', 'pip'), "install", "openai", "nbclient", "nbformat", "ipykernel"])
            subprocess.check_call([os.join('.venv', 'bin', 'python'),"-m", "ipykernel", "install", "--name=venv", "--display-name", "Python (venv)", "--prefix", ".venv"], text=True)
            self.process = subprocess.Popen([os.join(".venv", "bin", "python"), os.join('..','..','backend', 'agent', 'agent_api.py'), str(self.port), api_key, self.agent_id, os.join('..','..','log')], text=True)
        self.spun_up = True

    def spin_down(self):
        if self.process:
            self.process.terminate()
            self.process = None
        self.spun_up = False

class Cluster:
    def __init__(self, api_key):
        self.agents_lock = Lock()
        self.agents = {}
        self.min_port = 10000
        self.max_port = 20000
        self.used_ports = set()
        self.api_key = api_key
        self.max_pet_time_secs = 60 # TODO : 10 minutes
        self.purge_interval_secs = 60
        self.kill_timer = Timer(self.purge_interval_secs, self.kill_agents)
        self.kill_timer.start()

    def add_agent(self, agent_id):
        with self.agents_lock:
            self.agents[agent_id] = Node(agent_id, self._get_next_available_port())


    def _get_next_available_port(self):
        with self.agents_lock:
            for port in range(self.min_port, self.max_port):
                if port not in self.used_ports:
                    self.used_ports.add(port)
                    return port
    
    def get_agent_port(self, agent_id):
        with self.agents_lock:
            if agent_id not in self.agents:
                return None
            self.agents[agent_id].pet()
            return self.agents[agent_id].port
    

    def kill_agents(self):
        with self.agents_lock:
            for agent_id, node in list(self.agents.items()):
                if time.monotonic() - node.last_pet > self.max_pet_time_secs:
                    node.spin_down()
                    del self.agents[agent_id]
                    self.used_ports.remove(node.port)
        self.kill_timer = Timer(self.purge_interval_secs, self.kill_agents)
        self.kill_timer.start()
