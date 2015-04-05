from setuptools import setup

with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='camp',
    version='0.1.0',
    author='Max Brauer',
    author_email='max@rootswiseyouths.com',
    url='http://github.com/mamachanko/camp/',
    description='manages venvs',
    long_description=readme,
    py_modules=['camp'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        camp=camp:cli
    ''',
)
