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
from mmd_uuunyaa_tools.editors import MeshEditor
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import MessageException


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


POINT = 0
APEX = 1
BASE_A = 2
BASE_B = 3
BASE_C = 4
BASE_D = 5


def convert(breast_bones: List[bpy.types.EditBone], mesh_objects: List[bpy.types.Object], head_tail: float, spring_length_ratio: float, base_area_factor: float):

    targets = build_targets(breast_bones, mesh_objects, head_tail)

    if len(targets) == 0:
        raise MessageException(_('Target bones not found.')) from None

    for target in targets:
        apex_vertex, base_vertices = to_pyramid_vertices(target, base_area_factor)
        vertices: List[Vector] = [
            apex_vertex * spring_length_ratio,
            apex_vertex,
            *base_vertices
        ]

        pyramid_armature = bpy.data.armatures.new(f'mmd_uuunyaa_physics_{target.bone_name}')
        pyramid_armature_object = bpy.data.objects.new(f'mmd_uuunyaa_physics_{target.bone_name}', pyramid_armature)
        bpy.context.scene.collection.objects.link(pyramid_armature_object)
        pyramid_armature_object.location = target.origin

        bpy.context.selected_objects.append(pyramid_armature_object)
        bpy.context.view_layer.objects.active = pyramid_armature_object
        bpy.ops.object.mode_set(mode='EDIT')

        bone_length = vertices[APEX].length * 0.1
        bone_vector = target.direction * bone_length

        base_bone = pyramid_armature.edit_bones.new(f'mmd_uuunyaa_physics_base_{target.bone_name}')
        base_bone.head = Vector((0, 0, 0))
        base_bone.tail = Vector((0, 0, 0)) + bone_vector

        apex_bone = pyramid_armature.edit_bones.new(f'mmd_uuunyaa_physics_point_{target.bone_name}')
        apex_bone.parent = base_bone
        apex_bone.head = vertices[APEX] - bone_vector
        apex_bone.tail = vertices[APEX]

        base_a_bone = pyramid_armature.edit_bones.new(f'mmd_uuunyaa_physics_base_a_{target.bone_name}')
        base_a_bone.parent = base_bone
        base_a_bone.head = vertices[BASE_A]
        base_a_bone.tail = vertices[BASE_A] + bone_vector

        base_b_bone = pyramid_armature.edit_bones.new(f'mmd_uuunyaa_physics_base_b_{target.bone_name}')
        base_b_bone.parent = base_bone
        base_b_bone.head = vertices[BASE_B]
        base_b_bone.tail = vertices[BASE_B] + bone_vector

        base_c_bone = pyramid_armature.edit_bones.new(f'mmd_uuunyaa_physics_base_c_{target.bone_name}')
        base_c_bone.parent = base_bone
        base_c_bone.head = vertices[BASE_C]
        base_c_bone.tail = vertices[BASE_C] + bone_vector

        base_d_bone = pyramid_armature.edit_bones.new(f'mmd_uuunyaa_physics_base_d_{target.bone_name}')
        base_d_bone.parent = base_bone
        base_d_bone.head = vertices[BASE_D]
        base_d_bone.tail = vertices[BASE_D] + bone_vector
        pyramid_armature_object.update_from_editmode()

        pyramid_mesh = bpy.data.meshes.new(f'mmd_uuunyaa_physics_cloth_{target.bone_name}')
        pyramid_mesh.from_pydata(vertices, [
            [POINT, APEX]
        ], [
            [APEX, BASE_A, BASE_B],
            [APEX, BASE_B, BASE_C],
            [APEX, BASE_C, BASE_D],
            [APEX, BASE_D, BASE_A],
        ])
        pyramid_mesh.update()

        pyramid_mesh_object = bpy.data.objects.new(f'mmd_uuunyaa_physics_cloth_{target.bone_name}', pyramid_mesh)
        bpy.context.scene.collection.objects.link(pyramid_mesh_object)
        pyramid_mesh_object.parent = pyramid_armature_object
        pyramid_mesh_object.parent_type = 'BONE'
        pyramid_mesh_object.parent_bone = base_bone.name
        pyramid_mesh_object.matrix_basis = base_bone.matrix.inverted() @ Matrix.Translation(-bone_vector)
        pyramid_mesh_object.hide_render = True
        pyramid_mesh_object.display_type = 'WIRE'

        mesh_editor = MeshEditor(pyramid_mesh_object)
        mesh_editor.edit_vertex_group('mmd_uuunyaa_point', [([POINT], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_apex', [([APEX], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_a', [([BASE_A], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_b', [([BASE_B], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_c', [([BASE_C], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_d', [([BASE_D], 1.0)])
        mesh_editor.edit_cloth_modifier(
            'mmd_uuunyaa_physics_cloth',
            vertex_group_mass=mesh_editor.edit_vertex_group('mmd_uuunyaa_physics_cloth_pin', [
                ([POINT], 0.6),  # 0.4 - 0.6
                ([APEX], 0.4),  # 0.4 - 0.6
                ([BASE_A, BASE_B, BASE_C, BASE_D], 0.8),  # 0.8 - 0.9
            ]).name,
            time_scale=0.5,
            bending_model='LINEAR'
        )


def to_pyramid_vertices(target: Target, base_area_factor: float) -> Tuple[Vector, List[Vector]]:
    deform_mesh: bpy.types.Mesh = target.deform_mesh_object.data
    deform_bm: bmesh.types.BMesh = bmesh.new()
    deform_bm.from_mesh(deform_mesh)

    apex_vertex, deform_vertex_index_weights = find_apex_vertex(deform_bm, target)
    base_vertices = find_base_vertices(deform_bm, target, deform_vertex_index_weights, base_area_factor)

    deform_bm.free()

    return apex_vertex, base_vertices


def find_base_vertices(deform_bm: bmesh.types.BMesh, target: Target, deform_vertex_index_weights: Dict[int, float], base_area_factor: float) -> List[Vector]:
    ortho_projection_matrix = Matrix.OrthoProjection(target.direction, 4)

    f_l = 1
    intrinsic_matrix = Matrix([
        [f_l, 0.0, 0.0, 0.0],
        [0.0, f_l, 0.0, 0.0],
        [0.0, 0.0, f_l, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    wide_projection_matrix: Matrix = intrinsic_matrix @ ortho_projection_matrix @ Matrix.Translation(-target.origin)

    wide_project_2d_vertices: Set[Tuple[float, float]] = set()
    wide_project_3d_vertices: List[Vector] = []

    deform_bm.verts.ensure_lookup_table()
    for deform_vertex_index, deform_vertex_weight in deform_vertex_index_weights.items():
        deform_vertex = deform_bm.verts[deform_vertex_index].co
        wide_project_3d_vertex = wide_projection_matrix @ deform_vertex
        wide_project_2d_vertex = wide_project_3d_vertex / wide_project_3d_vertex[2]

        wide_project_2d_vertices.add(wide_project_2d_vertex[0:2])
        wide_project_3d_vertices.append(wide_project_3d_vertex * (deform_vertex_weight**base_area_factor))

    box_fit_angle: float = mathutils.geometry.box_fit_2d(list(wide_project_2d_vertices))
    rotate_matrix: Matrix = Matrix.Rotation(+box_fit_angle, 4, target.direction) @ ortho_projection_matrix

    x_min = float('+inf')
    x_max = float('-inf')
    z_min = float('+inf')
    z_max = float('-inf')

    for vertex in wide_project_3d_vertices:
        rotate_vertex: Vector = rotate_matrix @ vertex

        if x_min > rotate_vertex.x:
            x_min = rotate_vertex.x

        if x_max < rotate_vertex.x:
            x_max = rotate_vertex.x

        if z_min > rotate_vertex.z:
            z_min = rotate_vertex.z

        if z_max < rotate_vertex.z:
            z_max = rotate_vertex.z

    front_vector = Vector([0, -1, 0])
    rotate_matrix_invert: Matrix = Matrix.Rotation(-box_fit_angle, 4, front_vector) @ Matrix.OrthoProjection(front_vector, 4)

    base_vertices: List[Vector] = [
        rotate_matrix_invert @ Vector([x_min, 0, 0]),
        rotate_matrix_invert @ Vector([0, 0, z_min]),
        rotate_matrix_invert @ Vector([x_max, 0, 0]),
        rotate_matrix_invert @ Vector([0, 0, z_max]),
    ]

    return base_vertices


def find_apex_vertex(deform_bm: bmesh.types.BMesh, target: Target) -> Tuple[Vector, Dict[int, float]]:
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


def build_targets(breast_bones: List[bpy.types.EditBone], mesh_objects: List[bpy.types.Object], head_tail: float) -> List[Target]:
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


class ConvertBreastBoneToClothOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_breast_bone_to_cloth'
    bl_label = _('Convert Breast Bone to Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    head_tail: bpy.props.FloatProperty(name=_('Head/Tail'), default=0.5, min=0.0, max=1.0, step=10)
    spring_length_ratio: bpy.props.FloatProperty(name=_('Spring Length Ratio'), default=5.0, min=1.0, max=100.0, step=10)
    base_area_factor: bpy.props.FloatProperty(name=_('Vertex Shift'), default=0.1, min=0.0, max=100.0, step=10)

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
                self.base_area_factor
            )

        except MessageException as ex:
            self.report(type={'ERROR'}, message=str(ex))
            return {'CANCELLED'}

        return {'FINISHED'}
