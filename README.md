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

## Interface

![Image](https://github.com/Luca683/Blender-addon-MiniBIM/blob/main/images/interface.png)

Interface is equipped with:

- A button ` Export data `: by pressing it, automatically, vertex groups data will be loaded into your local database, each tuple will include (name_vertex_group, name_mesh, number_vertex_of_vertex_group, number_faces_of_vertex_group, area_of_vertex_group)
PS. This operation will take 2-3 seconds if we are dealing with meshes with a large number of vertices and faces

- A series of ` Panels ` that allow you to model your query and then to choose what you want to see (a specific vertex_group based on its name, one or more vertex groups with required characteristics)

- A ` Show only selected vertex group ` checkbutton: if you activate it, after a query, only the affected vertex groups will be displayed while the rest of the scene will be made invisible

- A button ` Query `: pressing it, the query will be executed and then the interested vertex_groups will be selected and colored in red (make sure that in the "viewport shading" panel on blender under "Color" the option "Attribute" or "Vertex" is activated, it depends from the blender version used, otherwise the coloring will not be visible).
PS. the operation will take 2-3 seconds if we are dealing with meshes with a large number of vertices and faces

- A button ` Restore `: allows you to reset the results of a query (colors and vertex selection) by returning your meshes to its basic state

---

***In development***: we are trying to eliminate the dependency on the mysql connector module to allow the user to use the addon more easily, we will use SQLite for this reason.
