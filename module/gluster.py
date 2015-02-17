#!/usr/bin/python

import subprocess
import shlex
import json
from ast import literal_eval

class Gluster():

    def __init__(self, module):
        self.server = module.params['server']
        if module.params['force'] == 'yes':
            self.force = True
        else:
            self.force = False

        self.volname = module.params['volname']
        self.voltype = module.params['voltype']
        self.replicacount = module.params['replicacount']
        # self.brickdir = module.params['brickdir']

    def peer_status(self):
        """List the set of gluster peers"""
        cmdlist = shlex.split("gluster peer status")
        output = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
        stdout = output.stdout.read()
        print json.dumps({
            "output": stdout
        })

    def peer_probe(self):
        """Probe the peers in the listed nodes.

        From any one node gluster calls probe to all the other nodes.
        """
        cmd = "gluster peer probe %s"%(self.server)
        cmdlist = shlex.split(cmd)
        output = subprocess.Popen(cmdlist, stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE)
        # TODO: extensive error check if the command succeeded
        stdout = output.stdout.read()
        stderr = output.stderr.read()
        print json.dumps({
            "Peer probed": self.server,
            "Status": stdout
        })

    def peer_detach(self):
        """Detach the listed peers"""
        cmd = "gluster peer detach %s"%(self.server)
        if self.force is True:
            cmd = cmd + ' force'
        cmdlist = shlex.split(cmd)
        output = subprocess.Popen(cmdlist, stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE)
        # TODO: Do more extensive error check
        stdout = output.stdout.read()
        stderr = output.stderr.read()
        print json.dumps({
            "Server detached": self.server,
            "Status": stdout
        })

    def volume_create(self):
        """Create a volume"""
        # In case of a volume the a list of servers and brick path are
        # provided. Loop through them to create a volume.
        brick_list = literal_eval(self.server)

        cmd = "gluster volume create %s"%(self.volname)
        if self.voltype == 'replica':
            cmd += ' replica ' + self.replicacount

        for brick in brick_list:
            cmd += ' ' + brick
        if self.force is True:
            cmd += ' force'

        cmdlist = shlex.split(cmd)
        output = subprocess.Popen(cmdlist, stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE)
        # TODO: Do more extensive error check
        print json.dumps({
            "Executed: ": cmd,
            "Result": output.stdout.read(),
            "Error": output.stderr.read(),
        })


def main():
    module = AnsibleModule(
        argument_spec = dict(
            command = dict(choices=['peer_status', 'peer_probe', 'peer_detach',
                                    'volume_create', 'quota']),
            force = dict(required = False, default = False),
            server = dict(required = False, aliases=['args'], default = ''),
            volname = dict(required = False, default = ''),
            voltype = dict(required = False, default = 'replica'),
            replicacount = dict(required = False, default = '2'),
            transport = dict(required = False, default = 'tcp'),
            # brickdir = dict(required = False, default = ''),
        ),
        supports_check_mode=True
    )

    gluster = Gluster(module)

    if module.params['command'] is None:
        module.fail_json(msg="Command is mandatory")

    func = "gluster.%s"%(module.params['command'])
    if module.params['command'] == 'volume_create' and \
       module.params['volname'] == '':
        module.fail_json(msg = "Module name and brick directory are mandatory")

    eval(func)()

from ansible.module_utils.basic import *
main()
