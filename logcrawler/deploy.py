#!/usr/bin/env python
# coding: utf-8


import os
import sys

from fabric.context_managers import cd, hide, settings
from fabric.api import run, sudo, execute, env
from fabric.operations import put
from fabric.tasks import Task
from optparse import OptionParser
from StringIO import StringIO

class BaseDeployer(Task):
    """ Deployer Base Class

        Args:
            hosts:  Directory of target hosts to deploy,
                    key is alpha/release, value is list of hosts.
            root:   Root path of repository to deploy.
            repo:   Git repository URL.
            passwd: Git password.
            tag:    Git tag.
            env:    Target environment of deployment.

        Example:
            >>> deployer = BaseDeployer(hosts={'alpha': ['127.0.0.1']}, root='/tmp',
                    repo='git@192.168.16.205:/home/example.git')
            >>> fabric.api.execute(deployer)
    """

    def __init__(self, tag=None, env='alpha', *args, **kwargs):
        super(BaseDeployer, self).__init__(*args, **kwargs)
        self.tag = tag
        self.env = env
        self.hosts = None

    def load_config(self, path, target_host):
        """ Load config from configure file.
        """
        config = _load_config(path)
        if config:
            print "loading config: %s\n" % os.path.abspath(path)
            self.hosts = {self.env: config.get(target_host)}
            self.root = config.get('GIT_ROOT')
            self.repo = config.get('GIT_REPO')
            self.passwd = config.get('GIT_PASSWORD')
            env.user = config.get('SSH_USER')
            env.password = config.get('SSH_PASSWORD')
        return config

    def get_hosts(self, arg_hosts, arg_roles, arg_exclude_hosts, env=None):
        """ Override function of Task baseclass.
        """
        return self.hosts.get(self.env)

    def run(self):
        self.deploy()

    def deploy(self):
        if self.is_cloned():
            self.pull()
            self.restart_service()
            self.restart_app()
        else:
            self.clone()
            self.setup()
            self.start_service()
            self.start_app()

    def pull(self, remote='origin', branch='master'):
        cmd = "git pull {remote} {branch} ;".format(remote=remote, branch=branch)
        if self.tag:
            cmd += "git checkout {tag} ;".format(tag=self.tag)

        if self.passwd:
            self.auto_auth_run(cmd)
        else:
            with cd(self.root):
                run(cmd)

    def clone(self):
        sudo("mkdir -p %s" % self.root)

        cmd = "git clone {repo} {path}".format(repo=self.repo, path='.')
        if self.passwd:
            self.auto_auth_run(cmd)
        else:
            with cd(self.root):
                run(cmd)

        if self.tag:
            with cd(self.root):
                run("git checkout {tag} ;".format(tag=self.tag))

    def is_cloned(self):
        dot_git = '/'.join([self.root, '.git'])
        with settings(warn_only=True):
            test_root = "test -d %s" % self.root
            test_dot_git = "test -d %s" % dot_git
            return run(test_root).succeeded and run(test_dot_git).succeeded

    def auto_auth_run(self, cmd):
        """ Run git command.
            Enter the password automatically when encounter the prompt.
            Note: support unix-like os only.
        """
        # FIX ME
        pass

    def setup(self):
        pass

    def start_service(self):
        pass

    def restart_service(self):
        pass

    def start_app(self):
        pass

    def restart_app(self):
        pass

class MasterDeployer(BaseDeployer):
    """ BaseDeployer for master host.
    """
    name = "master"

    def setup(self):
        self._setup_env()
        self._setup_app()

    def start_service(self):
        uwsgi = '/'.join([self.root, 'logcrawler/web/uwsgi-logcrawler'])
        with cd(os.path.dirname(uwsgi)):
            sudo('bash {service} start'.format(service=uwsgi))

    def restart_service(self):
        uwsgi = '/'.join([self.root, 'logcrawler/web/uwsgi-logcrawler'])
        with cd(os.path.dirname(uwsgi)):
            sudo('bash {service} reload'.format(service=uwsgi))

    def start_app(self):
        with cd(self.root):
            run('bin/logcrawler_daemon.py start')

    def restart_app(self):
        with cd(self.root):
            run('bin/logcrawler_daemon.py restart')

    def clean(self):
        with settings(hide('warnings', 'stderr'), warn_only=True):
            if run("test -d %s" % self.root).succeeded:
                # stop app
                with cd(self.root):
                    run("bin/logcrawler_daemon.py stop")

                # stop service
                uwsgi = '/'.join([self.root, 'logcrawler/web/uwsgi-logcrawler'])
                if run("test -e %s" % uwsgi).succeeded:
                    with cd(os.path.dirname(uwsgi)):
                        sudo('{service} stop'.format(service=uwsgi))

                # clean repository
                run("rm -rf %s" % self.root)

            # remove .pth
            sudo("rm -f /usr/local/lib/python2.7/site-packages/logcrawler.pth")

    def _setup_env(self):
        pass

    def _setup_app(self):
        # setup sys.path
        src = StringIO(self.root+'\n')
        dst = "/usr/local/lib/python2.7/site-packages/logcrawler.pth"
        put(local_path=src, remote_path=dst, use_sudo=True)

class MasterCleaner(MasterDeployer):
    def run(self):
        self.clean()

class WorkerDeployer(MasterDeployer):
    """ Deployer for celery worker hosts.
    """

    def start_service(self):
        sudo("/etc/init.d/celeryd-download start")
        sudo("/etc/init.d/celeryd-analyze start")

    def restart_service(self):
        sudo("/etc/init.d/celeryd-download restart")
        sudo("/etc/init.d/celeryd-analyze restart")

    def start_app(self):
        pass

    def restart_app(self):
        pass

    def clean(self):
        with settings(hide('warnings', 'stderr'), warn_only=True):
            # stop service
            if run("test -h /etc/init.d/celeryd").succeeded:
                sudo("/etc/init.d/celeryd stop")

            # remove service startup scripts
            for softlink in ["/etc/sysconfig/celeryd", "/etc/init.d/celeryd"]:
                if run("test -h %s" % softlink).succeeded:
                    sudo("rm -f %s" % softlink)

            # remove .pth
            sudo("rm -f /usr/local/lib/python2.7/site-packages/logcrawler.pth")

            # clean repository
            if run("test -d %s" % self.root).succeeded:
                run("rm -rf %s" % self.root)

    def _setup_env(self):
        # setup celeryd worker service
        sysconfig = "/".join([self.root, "celeryd/celeryd.sysconfig"])
        cmd = "ln -s {0} /etc/sysconfig/celeryd".format(sysconfig)
        sudo(cmd)

        celeryd = "/".join([self.root, "celeryd/celeryd"])
        cmd = "ln -s {0} /etc/init.d/celeryd".format(celeryd)
        sudo(cmd)

class WorkerCleaner(WorkerDeployer):
    def run(self):
        self.clean()

class BaseAgent(Task):
    """ Agent Base Class
        
        Args:
            tag:             Tag name in git repository.
            config_filename: Path of config file.
            script_filename: Path of deploy file, for uploading to agent.
            remote_dir:      Target path for deploy file to upload to.

        Example:
            agent = BaseAgent(tag='v0.1.0', config_filename='deploy_release.cfg',
                script_filename='deploy.py', remote_dir='/tmp')
            fabric.api.execute(agent)
    """
    def __init__(self, config_filename, tag=None, script_filename=__file__, remote_dir='/tmp', *args, **kwargs):
        super(BaseAgent, self).__init__(*args, **kwargs)
        self.script_filename = script_filename
        self.config_filename = config_filename
        self.remote_dir = remote_dir
        self.host = None
        self.tag = tag
        self.config = {}

        self.build_env(config_filename)

    def build_env(self, filename):
        config = _load_config(filename)
        env.port = config.get('SSH_AGENT_PORT')
        env.user = config.get('SSH_AGENT_USER')
        env.key_filename = config.get('SSH_AGENT_KEY')
        self.host = config.get('SSH_AGENT_HOST')
        self.config = config

    def get_hosts(self, arg_hosts, arg_roles, arg_exclude_hosts, env=None):
        return [self.host,]

    def run(self):
        self._upload_files()
        self._do_deploy()

    def _upload_files(self):
        # TO BE FIX
        content = ''

        # upload .cfg file
        local = StringIO(content)
        remote = '/'.join([self.remote_dir + os.path.basename(self.config_filename)])
        put(local_path=local, remote_path=remote, use_sudo=True)

        # upload .py file
        local = self.script_filename
        remote = '/'.join([self.remote_dir, self.script_filename])
        put(local_path=local, remote_path=remote, use_sudo=True)

    def _do_deploy(self):
        with cd(self.remote_dir):
            cmd = ' '.join(sys.argv)
            run(cmd)

class Agent(BaseAgent):
    def run(self):
        self.exec_shell()

    def exec_shell(self):
        cmds = [
            "cd; ./logcrawler_pub.sh",
            "ssh -p 5044 git@192.168.111.214 './logcrawler-pull.sh all {tag}'".format(tag=self.tag),
            "ssh -p 5044 192.168.111.140 '/data/logcrawler-pull.sh {tag}'".format(tag=self.tag)
        ]
        for cmd in cmds:
            run(cmd)

def _load_config(path):
    config = {}
    try:
        execfile(path, config)
    except IOError, e:
        print "load config error:", str(e)
        return None
    del config['__builtins__']
    return config

def _use_agent(config):
    return 'SSH_AGENT_HOST' in config

def parse_cmdline():
    usage = "\n" + "  python %prog [options] alpha [clean]\n" + "  python %prog [options] release"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--tag", dest="tag",
                      help="specify tagged revision to deploy")
    parser.add_option("-f", "--config", dest="config_file",
                      help="config file path")
    parser.add_option("--master", action="store_true", dest="master",
                      help="Deploy master host only")
    parser.add_option("--worker", action="store_true", dest="worker",
                      help="Deploy worker host only")
    options, args = parser.parse_args(args=None, values=None)

    if not args or args[0] not in ['alpha', 'release']:
        parser.error('argument error')
        sys.exit(1)
    if args[0] == 'release' and not options.tag:
        parser.error('tag option is required when deploy to release')
        sys.exit(1)
    if not options.config_file:
        # load default config file
        default_config = "deploy_%s.cfg" % args[0]
        if os.path.exists(default_config):
            options.config_file = default_config
        else:
            parser.error('no config file')
            sys.exit(1)

    return options, args

if __name__ == "__main__":
    options, args = parse_cmdline()
    target_env = args[0]
    config = _load_config(options.config_file)
    if _use_agent(config):
        # use agent host to deploy
        agent = Agent(config_filename=options.config_file, tag=options.tag)
        execute(agent)
        sys.exit(0)

    if len(args) > 1 and args[1] == 'clean':
        master_clz, worker_clz = MasterCleaner, WorkerCleaner
    else:
        master_clz, worker_clz = MasterDeployer, WorkerDeployer

    if not options.worker:
        master = master_clz(tag=options.tag, env=target_env)
        master.load_config(options.config_file, 'HOSTS_MASTER')
        execute(master)

    if not options.master:
        worker = worker_clz(tag=options.tag, env=target_env)
        worker.load_config(options.config_file, 'HOSTS_WORKER')
        execute(worker)
