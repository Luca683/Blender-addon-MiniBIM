# Blender addon MiniBIM

This addon allows you to export all data of your scene, relating to vertex groups of each mesh, into a local database, to make queries on that database and select vertex groups with the required requirements.

The addon is equipped with a small interface that will be immediately available, once the addon is installed, at the top right next to the menus View, Tool, Item.

## Installation

- Download Blender (Version 3.2 and older)

- Install modules

  ` pip install bpy `
  
  ` pip install fake-bpy-module-latest `
  
  ` pip install mysql-connector-python `

- Install [mysql.connector](https://downloads.mysql.com/archives/c-python/) (Version 8.0.29 and older) and put "mysql" folder and in the "blender modules" folder.

- Before installing the addon on blender make sure you have an active version of mysql on your device (it is also okay to use a XAMPP distribution)

- Install the addon on blender: Edit> Preferences> Install and look for ` mini_bim.py ` file
