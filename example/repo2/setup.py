from setuptools import setup

setup(
    name='camp',
    version='0.1.0',
    py_modules=['camp'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        camp=camp:camp
    ''',
)
