KINDEN VIETNAM Customize & Deploy OpenERP 7
===========================================

### General information about KDVN OpenERP 7

KINDEN VIETNAM OpenERP 7 customization modules.

1. Project & Contract

2. Purchase Orders

3. Expenses

4. Material Price

5. Stock Management

6. Asset and Fixed Asset Control

7. General Expenses

8. Addtional Tools

### Already to use docker-compose file

This repository included a docker-compose.yml file that already to used with the command `docker-compose up`..  
*Some notes:*

* If cloning the repository, the customized addons, follow instruction below
    * goto github.com to common repository, fork repository
    * git init
    * git remote add origin your forked repository url
    * git fetch
    * git branch oe7-develop origin/oe7-develop
    * git checkout oe7-develop
* If push your changing to common repository
    * goto your forked repositry click pull request -> create pull request
* Get latest code from common repository
    * Add upstream to your working git folder (one time only)
        * git remote add upstream https://www.github.com/kdvn/openerp7
        * git fetch --all
        * git merge upstream/oe7-develop (Note: Must working on your branch you want to get latest code)
        * git push
* Using pgtool.bash to dump or restore a database (on real machine running docker)
* Passwords showing in the docker-compose.yml file are for demonstration purpose only. They can be changed and **should _NOT_ upload** to github.