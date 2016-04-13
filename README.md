Migasfree: Systems Management System (server side)
==================================================

Migasfree is an application to manage systems. Fundamentally to deploy software to computers in an organization.

This project was born within the project [migration to open source software for desktops](http://www.zaragoza.es/contenidos/azlinux/migracionescritoriosl.pdf) of [City council of Zaragoza](http://zaragozaciudad.net/azlinux).

You can learn about systems management systems at:
    * http://en.wikipedia.org/wiki/Systems_management
    * http://en.wikipedia.org/wiki/List_of_systems_management_systems


License
=======

Migasfree is free software, released under [GNU GPL v3](https://github.com/migasfree/migasfree/blob/master/COPYING).


Authors
=======

See [AUTHORS file](https://github.com/migasfree/migasfree/blob/master/AUTHORS)


Requirements
============

    * Server:
        + Apache with WSGI
        + Python 2.7
        + Django 1.9.3
        + PostgreSQL 9.1

    * Clients:
        + a Linux distribution (Debian, Fedora, openSUSE, Ubuntu, ...)
        + Python >= 2.6
            - pycurl >= 7.19
            - python-notify (optional)
        + lshw >= B.02.15
        + dmidecode


Features
========

    * Web administration
    * Multiuser and multiversion (you can have desktops with differents versions and/or Distributions of GNU/Linux)
    * Automated Data Capture (you do not worry about adding hostnames, users, IPs, devices, etc. to server)
    * Centralized system of errors and faults
    * Hardware and software inventories


Behaviour
=========

How can you change the software configuration of machines with migasfree?

When migasfree client is running, queries the migasfree Server and it responds with a code survey to execute in the client, created *ad hoc* for this client after consulting the database.

This code survey is executed in the client and basically configures the repositories of packages (rpm or deb). Previously, these repositories have been created for the server when the migasfree's administrator configures a repository.

A repository in migasfree server defines the packages that should be installed, updated or removed in the clients in function of attributes of client computer: **HOSTNAME**, **USER**, **LDAP CONTEXT**, **VIDEO CARD**, ... (the administrator defines the properties that he wants to use in his organization).

All changes of configuration in the clients are made through packages. Therefore it is necessary that you know how create packages in order to change the configuration of the machines that you want administrate. You can consider hiring a professional, this is the hard work, you were warned!


Use
===

For example: You want change the Firefox homepage in all PCs in a range of IPs.

    1. You must create a package (for example ``myorg-firefox-1-0.rpm`` or ``myorg-firefox-1-0.deb``). You must investigate which files need to be modified and allow the package to perform the task of changing the configuration. This is hard work!

    2. You must upload your package to the server. This is simple!

    3. You must create a repository in migasfree server. Add your package ``myorg-firefox-1-0`` and define the range of IPs. This is easy!

    4. *Voilà!* When migasfree client is executed and his IP is in range, the package is installed.


Documentation
=============

[Fun with migasfree](http://fun-with-migasfree.readthedocs.org/en/master/index.html) (spanish)

*That's all folks!!!*
