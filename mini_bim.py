bl_info = {
	"name": "Experimental BIM",
	"author": "Luca Strano <stranoluca469955@gmail.com>",
	"version": (1, 0),
	"blender": (3, 1, 0),
	"category": "",
	"location": "",
	"description": "",
}

import sqlite3
import bpy
import bmesh
from collections import Counter

mydb = sqlite3.connect(':memory:')
mycursor = mydb.cursor()

def add_mesh(self, context):
	items = []
	items.append(("All", "All", ""))

	for obj in bpy.data.objects:
		if obj.type=='MESH':
			items.append((obj.name, obj.name, ""))
	return items

def add_vertex_group(self, context):
	items = []
	scene = context.scene
	mytool = scene.my_tool
	items.append(("All", "All", ""))

	for obj in bpy.data.objects:
		if mytool.mesh_list == obj.name:
			for vgroup in bpy.data.objects[obj.name].vertex_groups:
				items.append((vgroup.name, vgroup.name, ""))
			break
	return items

class MyProperties(bpy.types.PropertyGroup):
	mesh_list : bpy.props.EnumProperty(
		name = "",
		description = "Select a Mesh",
		items = add_mesh
	)

	vertex_group_list : bpy.props.EnumProperty(
		name = "",
		description = "Select a vertex group",
		items = add_vertex_group
	)

	min_vertex : bpy.props.IntProperty(name = "", min = 0)
	max_vertex : bpy.props.IntProperty(name = "", min = 0)

	min_face : bpy.props.IntProperty(name = "", min = 0)
	max_face : bpy.props.IntProperty(name = "", min = 0)

	min_area: bpy.props.FloatProperty(name = "", min = 0.0)
	max_area: bpy.props.FloatProperty(name = "", min = 0.0)

	check : bpy.props.BoolProperty(name = "", default = False)

def create_table():
	mycursor.execute("""CREATE TABLE IF NOT EXISTS vertex_group(
						id INTEGER PRIMARY KEY, 
						name_vertex_group text, 
						mesh text, 
						num_vertex_vg integer, 
						num_face_vg integer, 
						area_vg real
						)""")

def count_vertex(obj, num_groups):
	vg_num_vertices = [0] * num_groups
	vertices = obj.data.vertices

	for vertex in vertices:
		for vgroup in vertex.groups:
			vg_num_vertices[vgroup.group] += 1
	
	return vg_num_vertices

def count_face_area(obj, num_groups):
	group_faces = [0] * num_groups 
	area = [0] * num_groups
	
	vertices = obj.data.vertices
	polygons = obj.data.polygons
	
	for face in polygons:
		size = len(face.vertices)
		verts = (vertices[i] for i in face.vertices)
		cnt = Counter(g.group for v in verts for g in v.groups)
		for i, c, in cnt.items():
			if c == size:
				group_faces[i]+=1
				area[i]+=face.area
	
	return group_faces, area		

def insert_database(obj, num_groups, group_vertices, group_faces, area):
	for i in range(num_groups):
		val = {
			'id': i,
			'name_vertex_group': obj.vertex_groups[i].name,
			'mesh': obj.name,
			'num_vertex_vg': group_vertices[i],
			'num_face_vg': group_faces[i],
			'area_vg': area[i],
		}
		
		mycursor.execute("INSERT or REPLACE INTO vertex_group VALUES(:id, :name_vertex_group, :mesh, :num_vertex_vg, :num_face_vg, :area_vg)", val)	

def deselect_vertex():
	bpy.ops.object.mode_set(mode="EDIT") 
	bpy.ops.mesh.reveal() 
	bpy.ops.mesh.select_all(action="DESELECT")

def reset_color_vertex(obj):
	mesh = obj.data
	if obj.type == "MESH":
		for vc in mesh.vertex_colors:
			mesh.vertex_colors.remove(vc)
		mesh.vertex_colors.new()

def restore_scene():
	deselect_vertex()
	for obj in bpy.data.objects:
		reset_color_vertex(obj)

def process_query():
	select_mesh = bpy.context.scene.my_tool.mesh_list
	select_vertex_group = bpy.context.scene.my_tool.vertex_group_list
	min_vertex = bpy.context.scene.my_tool.min_vertex
	max_vertex = bpy.context.scene.my_tool.max_vertex
	min_face = bpy.context.scene.my_tool.min_face
	max_face = bpy.context.scene.my_tool.max_face
	min_area = bpy.context.scene.my_tool.min_area
	max_area = bpy.context.scene.my_tool.max_area
	if select_mesh=="All" and select_vertex_group=="All":
		sql = "SELECT * FROM vertex_group WHERE num_vertex_vg >= :min_num_vertex_vg AND num_vertex_vg <= :max_num_vertex_vg AND num_face_vg >= :min_num_face_vg AND num_face_vg <= :max_num_face_vg AND area_vg >= :min_area_vg AND area_vg <= :max_area_vg"
		val = {
			'min_num_vertex_vg': min_vertex, 
			'max_num_vertex_vg': max_vertex, 
			'min_num_face_vg': min_face, 
			'max_num_face_vg': max_face, 
			'min_area_vg': min_area, 
			'max_area_vg': max_area
		}
	if select_mesh!="All" and select_vertex_group == "All":
		sql = "SELECT * FROM vertex_group WHERE mesh = :mesh AND num_vertex_vg >= :min_num_vertex_vg AND num_vertex_vg <= :max_num_vertex_vg AND num_face_vg >= :min_num_face_vg AND num_face_vg <= :max_num_face_vg AND area_vg >= :min_area_vg AND area_vg <= :max_area_vg"
		val = {
			'mesh': select_mesh,
			'min_num_vertex_vg': min_vertex, 
			'max_num_vertex_vg': max_vertex, 
			'min_num_face_vg': min_face, 
			'max_num_face_vg': max_face, 
			'min_area_vg': min_area, 
			'max_area_vg': max_area
		}
	if select_mesh!="All" and select_vertex_group!="All":
		sql = "SELECT * FROM vertex_group WHERE name_vertex_group = :name_vg AND mesh = :mesh"
		val = {
			'name_vg': select_vertex_group,
			'mesh': select_mesh,
		}
	return sql, val

def query_database():
	sql, val = process_query()
	mycursor.execute(sql, val)
	myresult = mycursor.fetchall()

	return myresult

def select_vertex(obj, myObj):
	bpy.context.view_layer.objects.active = obj 
	bpy.ops.object.mode_set(mode="OBJECT") 
	vertices = obj.data.vertices

	for vertex in vertices:
		for vgroup in vertex.groups:
			if vgroup.group in myObj[obj]:
				vertices[vertex.index].select = True

def color_vertex(obj, myObj):
	bpy.ops.object.mode_set(mode = "EDIT")
	bm = bmesh.from_edit_mesh(obj.data)
	vgroup_colors = {}

	for index_vg in myObj[obj]:
		vgroup_colors.update({index_vg: (1, 0, 0, 1)})

	target_vertex_groups = vgroup_colors.keys()
	vcolor_layers = {}

	for index_vg in myObj[obj]:
		vcolor_layers.update({index_vg: bm.loops.layers.color['Col']})
	dl = bm.verts.layers.deform.verify()

	for vertex in bm.verts:
		if len(vertex[dl]):
			in_vgroups = [vgroup_index for vgroup_index, weight in vertex[dl].items() if (weight)]
						
			in_target_vgroups = set(target_vertex_groups).intersection(in_vgroups)
						
			for face_corner in vertex.link_loops:
				for vgroup_idx in in_target_vgroups:
					face_corner[vcolor_layers[vgroup_idx]] = vgroup_colors[vgroup_idx]

def hide_unselected_vertices():
	bpy.ops.object.mode_set(mode="OBJECT")
	bpy.ops.object.select_all(action="SELECT")
	bpy.ops.object.mode_set(mode = "EDIT")

	if bpy.context.scene.my_tool.check == True:
		bpy.ops.mesh.hide(unselected=True)

class export(bpy.types.Operator):
	"""Preleva dati dalla scena e caricali in un database"""
	bl_idname = "mesh.export"
	bl_label = "Export data"

	def execute(self, context):
		create_table()

		myObjects = bpy.data.objects
		
		for obj in myObjects:
			if obj.type != 'MESH':
				continue

			num_groups = len(obj.vertex_groups) 
			
			group_vertices = count_vertex(obj, num_groups)

			group_faces, area = count_face_area(obj, num_groups)

			insert_database(obj, num_groups, group_vertices, group_faces, area)
		
		mydb.commit() 
		return {"FINISHED"}
	
class query(bpy.types.Operator):
	"""Fai una query"""
	bl_idname = "mesh.query_database"
	bl_label = "Query"

	def execute(self, context):
		restore_scene()
		myresult = query_database()

		myObj = {}
		for obj in bpy.data.objects:
			myObj[obj] = []

		for result in myresult:
			name_vertex_group = result[1]
			name_mesh = result[2]

			selected_mesh = bpy.data.objects[name_mesh]
			selected_vg = bpy.data.objects[name_mesh].vertex_groups[name_vertex_group].index

			myObj[selected_mesh].append(selected_vg)

		for obj in myObj:
			if(len(myObj[obj])!=0):
				select_vertex(obj, myObj)
				color_vertex(obj, myObj)

		hide_unselected_vertices()

		return {"FINISHED"}

class restore(bpy.types.Operator):
	"""Ripristina tutta la scena"""
	bl_idname = "mesh.restore_data"
	bl_label = "Restore"

	def execute(self, context):
		restore_scene()
		return {"FINISHED"}

class VIEW3D_PT_query(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Experimental BIM"
	bl_label = "Query"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool

		select_vertex_group = bpy.context.scene.my_tool.vertex_group_list

		row = layout.row()
		row.operator('mesh.export')
		layout.separator()

		row = layout.row()
		row.label(text="Search: ")

		row = layout.row(align=True)
		row.label(text = "Mesh")
		row.prop(mytool, "mesh_list")

		row = layout.row(align=True)
		row.label(text = "Vertex Group")
		row.prop(mytool, "vertex_group_list")

		if select_vertex_group == "All":
			row = layout.row(align=True)
			row.label(text = "Numero vertici")
			row.prop(mytool, "min_vertex", text = "MIN")
			row.prop(mytool, "max_vertex", text = "MAX")

			row = layout.row(align=True)
			row.label(text = "Numero facce")
			row.prop(mytool, "min_face", text = "MIN")
			row.prop(mytool, "max_face", text = "MAX")

			row = layout.row(align=True)
			row.label(text = "Area")
			row.prop(mytool, "min_area", text = "MIN")
			row.prop(mytool, "max_area", text = "MAX")
		
		row = layout.row()
		row.prop(mytool, "check", text="Show only selected vertex group")
		
		layout.separator()
		row = layout.row()
		row.operator('mesh.query_database')

		row = layout.row()
		row.operator('mesh.restore_data')

classes = [MyProperties, export, query, restore, VIEW3D_PT_query]		

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyProperties)
	
def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.my_tool