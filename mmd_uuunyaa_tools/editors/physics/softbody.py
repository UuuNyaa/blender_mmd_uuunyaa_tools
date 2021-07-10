# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Tuple, Union

import bmesh
import bpy
import mathutils
from mathutils import Matrix, Vector
from mmd_uuunyaa_tools.editors.physics import MeshEditor
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import MessageException, import_mmd_tools


class BreastBoneDirection(Enum):
    UNKNOWN = 'Unknown'
    DOWN = 'Down'
    FLAT = 'Flat'


@dataclass
class Target:
    bone_name: str
    deform_mesh_object: bpy.types.Object
    vertex_group: bpy.types.VertexGroup
    origin: Vector
    direction: Vector


def convert(breast_bones: List[bpy.types.EditBone], mesh_objects: List[bpy.types.Object], head_tail: float, spring_length_ratio: float, vertex_shift: float):

    targets = build_targets(breast_bones, mesh_objects, head_tail)

    for target in targets:
        apex_vertex, base_vertices = to_pyramid_vertices(target, vertex_shift)

        pyramid_mesh = bpy.data.meshes.new(f'mmd_uuunyaa_physics_{target.bone_name}')
        pyramid_mesh.from_pydata([
            apex_vertex * spring_length_ratio,
            apex_vertex,
            *base_vertices
        ], [
            [0, 1]
        ], [
            [1, 2, 3],
            [1, 3, 4],
            [1, 4, 5],
            [1, 5, 2],
        ]) 
        pyramid_mesh.update()
        pyramid_mesh_object = bpy.data.objects.new(f'mmd_uuunyaa_physics_{target.bone_name}', pyramid_mesh)
        bpy.context.scene.collection.objects.link(pyramid_mesh_object)
        pyramid_mesh_object.location = target.origin
        pyramid_mesh_object.hide_render = True
        pyramid_mesh_object.display_type = 'WIRE'

        pin_vertex_group: bpy.types.VertexGroup = pyramid_mesh_object.vertex_groups.new(name='mmd_uuunyaa_physics_cloth_pin')
        pin_vertex_group.add([0], 0.4, 'REPLACE')
        pin_vertex_group.add([2, 3, 4, 5], 0.8, 'REPLACE')

        mesh_editor = MeshEditor(pyramid_mesh_object)
        mesh_editor.edit_cloth_modifier(
            'mmd_uuunyaa_physics_cloth',
            vertex_group_mass=pin_vertex_group.name,
            time_scale=0.5,
            bending_model='LINEAR'
        )


def to_pyramid_vertices(target, vertex_shift):
    deform_mesh: bpy.types.Mesh = target.deform_mesh_object.data
    deform_bm: bmesh.types.BMesh = bmesh.new()
    deform_bm.from_mesh(deform_mesh)

    apex_vertex, deform_vertex_index_weights = find_apex_vertex(deform_bm, target)
    base_vertices = find_base_vertices(deform_bm, target, deform_vertex_index_weights, vertex_shift)

    deform_bm.free()

    return apex_vertex, base_vertices


def find_base_vertices(deform_bm, target, deform_vertex_index_weights, vertex_shift):
    ortho_projection_matrix = Matrix.OrthoProjection(target.direction, 4)

    f_l = 1
    intrinsic_matrix = Matrix([
        [f_l, 0.0, 0.0, 0.0],
        [0.0, f_l, 0.0, 0.0],
        [0.0, 0.0, f_l, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    wide_projection_matrix = intrinsic_matrix @ ortho_projection_matrix @ Matrix.Translation(-target.origin)

    wide_project_vertices: List[Vector] = []
    wide_project_2d_vertices: Set[Tuple[float, float]] = set()

    deform_bm.verts.ensure_lookup_table()
    for deform_vertex_index, deform_vertex_weight in deform_vertex_index_weights.items():
        deform_vertex: Vector = deform_bm.verts[deform_vertex_index].co
        wide_project_3d_vertex = wide_projection_matrix @ deform_vertex
        wide_project_2d_vertex = wide_project_3d_vertex / wide_project_3d_vertex[2]

        wide_project_2d_vertices.add(wide_project_2d_vertex[0:2])
        wide_project_vertices.append(wide_project_3d_vertex * (deform_vertex_weight**vertex_shift))

    box_fit_angle: float = mathutils.geometry.box_fit_2d(list(wide_project_2d_vertices))

    x_min = float('+inf')
    x_max = float('-inf')
    z_min = float('+inf')
    z_max = float('-inf')

    rotate_matrix = Matrix.Rotation(+box_fit_angle, 4, target.direction) @ ortho_projection_matrix

    for vertex in wide_project_vertices:
        rotate_vertex = rotate_matrix @ vertex

        if x_min > rotate_vertex.x:
            x_min = rotate_vertex.x

        if x_max < rotate_vertex.x:
            x_max = rotate_vertex.x

        if z_min > rotate_vertex.z:
            z_min = rotate_vertex.z

        if z_max < rotate_vertex.z:
            z_max = rotate_vertex.z

    front_vector = Vector([0, -1, 0])
    rotate_matrix_invert = Matrix.Rotation(-box_fit_angle, 4, front_vector) @ Matrix.OrthoProjection(front_vector, 4)

    base_vertices = [
        rotate_matrix_invert @ Vector([x_min, 0, 0]),
        rotate_matrix_invert @ Vector([0, 0, z_min]),
        rotate_matrix_invert @ Vector([x_max, 0, 0]),
        rotate_matrix_invert @ Vector([0, 0, z_max]),
    ]

    return base_vertices


def find_apex_vertex(deform_bm, target):
    deform_layer = deform_bm.verts.layers.deform.verify()

    vertex_group_index = target.vertex_group.index

    deform_vertex_index_weights: Dict[int, float] = {}

    mesh_max_weight = 0.0

    apex_location: Union[Vector, None] = None

    tri_loops: Tuple[bmesh.types.BMLoop, bmesh.types.BMLoop, bmesh.types.BMLoop]
    for tri_loops in deform_bm.calc_loop_triangles():
        vertex_weights = [l.vert[deform_layer].get(vertex_group_index, 0.0) for l in tri_loops]
        loop_max_weight: float = max(vertex_weights)
        if loop_max_weight == 0:
            continue

        if mesh_max_weight < loop_max_weight:
            mesh_max_weight = loop_max_weight

        intersection: Vector = mathutils.geometry.intersect_ray_tri(
            tri_loops[0].vert.co, tri_loops[1].vert.co, tri_loops[2].vert.co,
            target.direction, target.origin
        )

        for index in range(3):
            if vertex_weights[index] == 0:
                continue
            deform_vertex_index_weights[tri_loops[index].vert.index] = vertex_weights[index]

        if intersection is None:
            continue

        apex_location = intersection

    if apex_location is None:
        raise MessageException(f'The intersection of {target.bone_name} and {target.deform_mesh_object.name} not found.') from None

    return (
        apex_location - target.origin,
        {k: v/mesh_max_weight for k, v in deform_vertex_index_weights.items()}
    )


def build_targets(breast_bones, mesh_objects, head_tail):
    targets: List[Target] = []

    for breast_bone in breast_bones:
        breast_bone_direction_vector: Vector = breast_bone.vector.normalized()

        bone_name = breast_bone.name
        origin: Vector
        direction: Vector

        if breast_bone_direction_vector.z < -0.6:
            if not breast_bone.use_connect:
                raise MessageException('Unsupported breast bone structure.') from None

            direction = breast_bone.parent.vector.normalized()
            origin = breast_bone.parent.head + breast_bone.vector / 2 + head_tail * breast_bone.parent.vector

        elif -0.4 < breast_bone_direction_vector.z < +0.4:
            direction = breast_bone_direction_vector
            origin = breast_bone.head + head_tail * breast_bone.vector

        else:
            raise MessageException(f'Unsupported breast bone structure. too shallow angle {breast_bone_direction_vector.z}') from None

        for mesh_object in mesh_objects:
            vertex_group = mesh_object.vertex_groups.get(bone_name)
            if vertex_group is None:
                continue

            targets.append(Target(
                bone_name,
                mesh_object,
                vertex_group,
                origin,
                direction,
            ))

    return targets

    # mathutils.geometry.intersect_ray_tri(v1, v2, v3, ray, orig, clip=True)


class ConvertBreastBoneToClothOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_breast_bone_to_cloth'
    bl_label = _('Convert Breast Bone to Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    head_tail: bpy.props.FloatProperty(name=_('Head/Tail'), default=0.5, min=0.0, max=1.0)
    spring_length_ratio: bpy.props.FloatProperty(name=_('Spring Length Ratio'), default=5.0, min=1.0, max=100.0)
    vertex_shift: bpy.props.FloatProperty(name=_('Vertex Shift'), default=0.1, min=0.0, max=100.0)

    @ classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'EDIT_ARMATURE':
            return False

        if len(context.selected_bones) == 0:
            # At least one bone must be selected.
            return False

        for obj in context.selected_objects:
            # At least one mesh must be selected.
            if obj.type == 'MESH':
                return True

        return False

    def execute(self, context: bpy.types.Context):
        try:
            target_edit_bones: List[bpy.types.EditBone] = [b for b in context.selected_editable_bones if b.use_deform]
            target_mesh_objects: List[bpy.types.Object] = [o for o in context.selected_objects if o.type == 'MESH' and not o.hide]

            convert(
                target_edit_bones,
                target_mesh_objects,
                self.head_tail,
                self.spring_length_ratio,
                self.vertex_shift
            )

        except MessageException as ex:
            self.report(type={'ERROR'}, message=str(ex))
            return {'CANCELLED'}

        return {'FINISHED'}
