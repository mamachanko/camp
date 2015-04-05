# Camp

Camp helps you manage a set of _virtualenvs_.

The use case is a set of repositories, possibly services. some of which might
share certain requirements. however, as there might be conflicting requirements
it is not possible to put them all in the same virtualenv. As the number of
repositories grows larger it becomes cumbersome and errorprone to maintain all
these virtualenvs by hand.

This is what `camp` helps with.

Say, we have three repositories:

``` shell
$ tree -L 1
.
├── repo1
│   ├── repo1.py
│   ├── requirements.txt
│   └── setup.py
├── repo2
│   ├── repo2.py
│   ├── requirements.txt
│   └── setup.py
└── dep
    ├── dep.py
    ├── requirements.txt
    └── setup.py
```
The set of requirements is this for exmaple:
``` shell
$ tail */requirements.txt
==> repo1/eequirements.txt <==
click
six==1.8.0

==> repo2/requirements.txt <==
click
six==1.9.0

==> dep/requirements.txt <==
requests
```
Clearly, these requirements cannot go into one virtualenv as both the _six_ and
the _click_ versions collide. However, downloading both _six_ and _click_
versions twice does not make sense either. Using pip wheels does part of the
job, but then one would have to iterate of the set of repositories manually.

## Update

Just do:

``` shell
$ camp up
found Python repositories

    repo1
    repo2
    dep

getting wheels...          done.
creating venvs...          done.
installing requirements... done.
```
Camp found the three repositories. It created virtualenvs in each of them
(_<repo>/venv.camp_).  It fetched wheels and keeps them in the parent
directory(_.pip-wheels.camp_). It installed the respetive requirements into
each virtualenv.

Should one wish to update requirements, simply repeat `camp up`.

## Install editable

Now it may occur that one of your repositories is actually a requirement of
some of the others. For that purpose you'd want to install it with pip's `-e`
flag. With camp it's e.g.:
``` shell
$ camp install -e dep
```
This will install _dep_ in all four virtualenvs. It always forces to update.

## Tear down

Once the show is over, everything can torn down with:
``` shell
$ camp down
removing venvs...          done.
removing wheels...         done.
```
