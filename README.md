# Project Part 4: Catalog App
Logs Analysis project is part of [Full Stack Web Developer
Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)

> It is about an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Installation guide

### Prerequisites software and data:
  1. Install following software:
    * [Python3](https://www.python.org/)
    * [Git Bash](https://git-scm.com/downloads)
    * [Vagrant](https://www.vagrantup.com/)
    * [VirtualBox](https://www.virtualbox.org/)

  2. Download & Unzip catalog-app-project.zip file
  3. move the catalog-app-project folder to the vagrant directory


### Dependencies
`requirement.txt` is generated to help in installing all Dependencies
run following code to install

  ```
  $ pip install -r requirement.txt
  ```


### Launch Virtual Machine (VM):
  1. Launch Git Bash and `cd` to vagrant folder
  2. run vagrant following command at Git Bash vagrant specific directory

  ```
    $ vagrant up
  ```

  3. Log in using following command:

  ```
    $ vagrant ssh
  ```

  4. cd to catalog folder by using following command:

  ```
    $ cd /vagrant/catalog
  ```


### Set up the database:
  Use following command to set up the fake database:

  ```
  $ python catalog_db.py
  ```

  and

  ```
  $ python application.py
  ```

  to start catalog app


## Using Google Login (optional)
To get the Google login working there are a few additional steps:

  1. Go to [Google Dev Console](https://console.developers.google.com)
  2. Sign up or Login if prompted
  3. Go to Credentials
  4. Select Create Crendentials > OAuth Client ID
  5. Select Web application
  6. Enter name 'Catalog App'
  7. Authorized JavaScript origins = 'http://localhost:5000'
  8. Authorized redirect URIs = 'http://localhost:5000/login' && 'http://localhost:5000/gconnect'
  9. Select Create
  10. Copy the Client ID and paste it into the `data-clientid` in login.html
  11. On the Dev Console Select Download JSON
  12. Rename JSON file to client_secrets.json
  13. Place JSON file in catalog folder
  14. Run application using `python application.py`


## JSON Endpoints

  Catalog JSON: `/catalog/JSON`
    - Displays all Categories and items.

  Categories JSON: `/catalog/categories/JSON`
    - Displays all categories.

  Category Items JSON: `/catalog/category/<int:category_id>/item/JSON`
    - Displays items for a specific category.

  Category Item JSON: `/catalog/category/<int:category_id>/item/<int:item_id>/JSON`
    - Describe category item in detail.


## FAQ's:
  [FAQ link](https://knowledge.udacity.com/)
