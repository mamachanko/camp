import os
import shlex
import shutil
from subprocess import Popen, PIPE

import click


class NoPythonPackageError(Exception):
    pass


class Camp(object):

    WHEELDIR = 'wheelhouse'

    def __init__(self, path):
        self.path = path
        self.packages = set()
        self.collect_packages() 

    def collect_packages(self):
        for path in os.listdir(self.path):
            absolute_path = os.path.abspath(path)
            try:
                package = Package(absolute_path)
            except NoPythonPackageError:
                pass
            else:
                self.packages.add(package)

    def get_requirements(self):
        requirements = set()
        for package in self.packages:
            requirements.update(package.requirements)
        return requirements
        
    def create_wheels(self):
        wheeldir = os.path.join(os.getcwd(), self.WHEELDIR)
        wheel_command_template = 'pip wheel --no-cache-dir --wheel-dir={} {}'.format(wheeldir)

        for requirement in self.get_requirements():
            wheel_command = wheel_command_template.format(requirement)
            wheel_command_process = Popen(wheel_command, stdout=PIPE, stderr=PIPE)
            output, errors= command.communicate()

    def remove_wheels(path):
        shutil.rmtree(os.path.join(self.path, self.WHEELDIR), ignore_errors=True)


class Package(object):

    VENV = 'venv'

    def __init__(self, path):
        self.path = path
        self.validate()

    def validate(self):
        if not os.path.isdir(self.path):
            raise NoPythonPackageError('{} must be directory'.format(path))
        must_haves = ('setup.py', 'requirements.txt')
        if not all(path in os.listdir(self.path) for path in must_haves):
            raise NoPythonPackageError('cannot find setup.py or requirements.txt in {}'.format(self.path))

    def requirements(self):
        try:
            return self._requirements
        except AttributeError:
            requirements = set()
            with open(os.path.join(self.path, 'requirements.txt')) as requirements_file:
                reqs = requirements_file.readlines()
                reqs = map(lambda path: path.rstrip('\n'), reqs)
                requirements.update(reqs)
            self._requirements = requirements
            return self._requirements

    #FIXME
    def get_installed(self):
        self.run_in_venv('pip freeze')
        
    def install_requirements(self):
        wheeldir = os.path.join(os.getcwd(), 'wheelhouse')
        install_command = 'pip install --use-wheel --no-index --find-links={} -r requirements.txt'.format(wheeldir)
        self.run_in_venv(install_command)

    def create_venv(self, force=False):
        if self.has_venv() and not force:
            return
        with working_directory(path):
            command = Popen(['virtualenv', self.VENV], stdout=PIPE)
            output = command.communicate()[0]
            output = output.rstrip('\n')

    def has_venv(self):
        return self.VENV in os.listdir(self.path)

    def remove_venv(self):
        shutil.rmtree(os.path.join(self.path, self.VENV), ignore_errors=True)

    def run_in_path(self, commands):
        with working_directory(self.path):
            for command in commands:
                parsed_command = shlex.split(command)
                command_process = Popen(parsed_command, stdout=PIPE, stderr=PIPE)
                output, errors = command_process.communicate()
                if errors:
                    click.echo(errors)
                else:
                    click.echo(output)

    def run_in_venv(self, commands):
        for command in commands:
            command_template = '/bin/bash -c "source {}/venv/bin/activate && {}"'
            command = command_template.format(command)
            parsed_command = shlex.split(command)
            command_process = Popen(command, stdout=PIPE, stderr=PIPE, shell=False)
            output, errors = command_process.communicate()
            if errors:
                click.echo(errors)
            else:
                click.echo(output)
        

class working_directory(object):

    def __init__(self, working_directory):
        self.old_working_directory = os.getcwd()
        self.working_directory = working_directory

    def __enter__(self):
        os.chdir(self.working_directory)

    def __exit__(self, *args, **kwargs):
        os.chdir(self.old_working_directory)


def find_packages(path):
    packages = set()
    for entry in os.listdir(path):
        absolute_path = os.path.abspath(entry)
        if os.path.isfile(absolute_path):
            continue
        must_haves = ('setup.py', 'requirements.txt')
        if all(path in os.listdir(absolute_path) for path in must_haves):
            packages.add(absolute_path)
    return packages


def create_venv(path, overwrite=False):
    if 'venv' in os.listdir(path) and not overwrite:
        return
    with working_directory(path):
        command = Popen(['virtualenv', 'venv'], stdout=PIPE)
        output = command.communicate()[0]
        output = output.rstrip('\n')


def remove_venv(path):
    shutil.rmtree(os.path.join(path, 'venv'), ignore_errors=True)


def get_requirements(packages):
    requirements = set()
    for package in packages:
        with open(os.path.join(package, 'requirements.txt')) as requirements_file:
            reqs = requirements_file.readlines()
            reqs = map(lambda path: path.rstrip('\n'), reqs)
            requirements.update(reqs)
    return requirements


def create_wheels(packages, wheeldir=None):
    if wheeldir is None:
        wheeldir = os.path.join(os.getcwd(), 'wheelhouse')
    
    wheel_command = ['pip', 'wheel', '--no-cache-dir', '--wheel-dir=%s' % wheeldir]

    for package in packages:
        command = Popen(wheel_command + [package], stdout=PIPE)
        output = command.communicate()[0]
        output = output.rstrip('\n')


def remove_wheels(path):
    shutil.rmtree(os.path.join(path, 'wheelhouse'), ignore_errors=True)


def run_in_venv(venv, command):
    with working_directory(venv):
        command_template = '/bin/bash -c "source {}/venv/bin/activate && {}"'
        command = shlex.split(command_template.format(venv, command))
        process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    return process.communicate()


def show_packages(package):
    pip = os.path.join(package, 'venv/bin/pip')
    output = run_in_venv(package, 'pip freeze')[0]
    click.echo('packages in {}:\n{}'.format(package, output))


def install_requirements(package, wheeldir=None):
    if wheeldir is None:
        wheeldir = os.path.join(os.getcwd(), 'wheelhouse')
    install_command = 'pip install --use-wheel --no-index --find-links={} -r requirements.txt'.format(wheeldir)
    run_in_venv(package, install_command)


@click.group()
def camp():
    click.echo('this is camp\n')


@camp.command()
def up():
    cwd = os.getcwd()
    packages = find_packages(cwd)
    click.echo('found Python repositories')
    click.echo()
    for package in packages:
        click.echo('    {}'.format(package))
    click.echo()

    click.echo('creating virtualenvs...')
    map(create_venv, packages)
    click.echo('done\n')

    click.echo('getting wheels...')
    requirements = get_requirements(packages) 
    create_wheels(requirements)
    click.echo('done\n')

    click.echo('installing requirements...')
    map(install_requirements, packages)
    click.echo('done')


@camp.command()
def down():
    cwd = os.getcwd()
    packages = find_packages(cwd)

    click.echo('removing virtualenvs...')
    map(remove_venv, packages)
    click.echo('done\n')

    click.echo('removing wheels...')
    remove_wheels(cwd)
    click.echo('done')


@camp.command()
def show():
    cwd = os.getcwd()
    packages = find_packages(cwd)

    click.echo('found Python repositories')
    click.echo()
    for package in packages:
        click.echo('    {}'.format(package))
    click.echo()

    map(show_packages, packages)
