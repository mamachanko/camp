import os
import shlex
import shutil
from subprocess import Popen, PIPE

import click


class NoPythonPackageError(Exception):
    pass


class Camp(object):

    WHEELDIR = 'wheelhouse'

    def __init__(self, path=None):
        if path is None:
            path = os.getcwd()
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

    def create_wheels(self):
        wheeldir = os.path.join(os.getcwd(), self.WHEELDIR)
        wheel_command_template = 'pip wheel --no-cache-dir --wheel-dir={} {}'

        for requirement in self.get_requirements():
            wheel_command = wheel_command_template.format(wheeldir, requirement)
            parsed_wheel_command = shlex.split(wheel_command)
            wheel_command_process = Popen(parsed_wheel_command, stdout=PIPE, stderr=PIPE)
            output, errors = wheel_command_process.communicate()

    def get_requirements(self):
        requirements = set()
        for package in self.packages:
            requirements.update(package.requirements)
        return requirements

    def remove_wheels(self):
        shutil.rmtree(os.path.join(self.path, self.WHEELDIR), ignore_errors=True)


class Package(object):

    VENV = 'venv'

    def __init__(self, path):
        self.path = path
        self.validate()

    def validate(self):
        if not os.path.isdir(self.path):
            raise NoPythonPackageError('{} must be directory'.format(self.path))
        must_haves = ('setup.py', 'requirements.txt')
        if not all(path in os.listdir(self.path) for path in must_haves):
            raise NoPythonPackageError('cannot find setup.py or requirements.txt in {}'.format(self.path))

    @property
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

    @property
    def venv(self):
        return os.path.join(self.path, self.VENV)

    @property
    def requirements_file(self):
        return os.path.join(self.path, 'requirements.txt')

    def get_installed(self):
        return self.run_in_venv('pip freeze')[0].split('\n')
        
    def install_requirements(self):
        wheeldir = os.path.join(os.getcwd(), 'wheelhouse')
        install_command = 'pip install --use-wheel --no-index --find-links={} -r {}'.format(wheeldir, self.requirements_file)
        return self.run_in_venv(install_command)

    def create_venv(self, force=False):
        if self.has_venv() and not force:
            return
        return self.run_in_path('virtualenv {}'.format(self.VENV))

    def has_venv(self):
        return self.VENV in os.listdir(self.path)

    def remove_venv(self):
        shutil.rmtree(os.path.join(self.path, self.VENV), ignore_errors=True)

    def run_in_venv(self, command):
        command_template = '/bin/bash -c "source {}/bin/activate && {}"'
        command = command_template.format(self.venv, command)
        return self.run_in_path(command, path=self.venv)

    def run_in_path(self, command, path=None):
        if path is None:
            path = self.path

        with working_directory(path):
            parsed_command = shlex.split(command)
            command_process = Popen(parsed_command, stdout=PIPE, stderr=PIPE, shell=False)
            return command_process.communicate()


class working_directory(object):

    def __init__(self, working_directory):
        self.old_working_directory = os.getcwd()
        self.working_directory = working_directory

    def __enter__(self):
        os.chdir(self.working_directory)

    def __exit__(self, *args, **kwargs):
        os.chdir(self.old_working_directory)


pass_camp = click.make_pass_decorator(Camp, ensure=True)


@click.group()
@pass_camp
def cli(camp):
    click.echo('this is camp\n')


@cli.command()
@pass_camp
def up(camp):
    click.echo('found Python packages')
    click.echo()
    for package in camp.packages:
        click.echo('    {}'.format(package.path))
    click.echo()

    click.echo('creating virtualenvs...')
    for package in camp.packages:
        package.create_venv()
    click.echo('done\n')

    click.echo('getting wheels...')
    camp.create_wheels()
    click.echo('done\n')

    click.echo('installing requirements...')
    for package in camp.packages:
        package.install_requirements()
    click.echo('done')


@cli.command()
@pass_camp
def down(camp):
    click.echo('removing virtualenvs...')
    for package in camp.packages:
        package.remove_venv()
    click.echo('done\n')

    click.echo('removing wheels...')
    camp.remove_wheels()
    click.echo('done')


@cli.command()
@pass_camp
def show(camp):
    click.echo('found Python packages')
    click.echo()
    for package in camp.packages:
        click.echo('    {}'.format(package.path))
        for installed in package.get_installed():
            click.echo('        {}'.format(installed))
