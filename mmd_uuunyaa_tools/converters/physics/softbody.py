# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Tuple, Union

import bmesh
import bpy
import mathutils
import numpy as np
from mathutils import Matrix, Vector
from mmd_uuunyaa_tools.editors import ArmatureEditor, MeshEditor
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import MessageException


class BreastBoneDirection(Enum):
    UNKNOWN = 'Unknown'
    DOWN = 'Down'
    FLAT = 'Flat'


@dataclass
class Target:
    bone_name: str
    parent_bone_name: str
    deform_mesh_object: bpy.types.Object
    vertex_group: bpy.types.VertexGroup
    origin: Vector
    direction: Vector


@dataclass
class TargetA:
    bone_name: str
    parent_bone_name: str
    deform_mesh_object: bpy.types.Object
    pyramid_mesh_object: bpy.types.Object


STRING = 0
APEX = 1
BASE_A = 2
BASE_B = 3
BASE_C = 4
BASE_D = 5

PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME = 'physics_pyramid_cloth_target_bone'
PYRAMID_CLOTH_PARENT_BONE_PROPERTY_NAME = 'physics_pyramid_cloth_parent_bone'


def add_pyramid_mesh(breast_bones: List[bpy.types.EditBone], mesh_objects: List[bpy.types.Object], head_tail: float, spring_length_ratio: float, base_area_factor: float):
    targets = build_targets(breast_bones, mesh_objects, head_tail)

    if len(targets) == 0:
        raise MessageException(_('Target bones not found.')) from None

    for target in targets:
        pyramid_mesh = build_pyramid_mesh(target, spring_length_ratio, base_area_factor)
        pyramid_mesh[PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME] = target.bone_name
        pyramid_mesh[PYRAMID_CLOTH_PARENT_BONE_PROPERTY_NAME] = target.parent_bone_name
        bpy.context.scene.collection.objects.link(pyramid_mesh)


def build_pyramid_mesh(target: Target, spring_length_ratio: float, base_area_factor: float):
    deform_bm: bmesh.types.BMesh = bmesh.new()
    deform_bm.from_object(target.deform_mesh_object, bpy.context.evaluated_depsgraph_get())

    apex_vertex, base_vertices, _deform_vertex_index_weights = to_pyramid_vertices(deform_bm, target, base_area_factor)
    vertices: List[Vector] = [
        apex_vertex * spring_length_ratio,
        apex_vertex,
        *base_vertices
    ]

    pyramid_mesh = bpy.data.meshes.new(f'physics_pyramid_cloth_{target.bone_name}')
    pyramid_mesh.from_pydata(vertices, [
        [STRING, APEX]
    ], [
        [APEX, BASE_A, BASE_B],
        [APEX, BASE_B, BASE_C],
        [APEX, BASE_C, BASE_D],
        [APEX, BASE_D, BASE_A],
    ])
    pyramid_mesh.update()

    deform_bm.clear()

    pyramid_mesh_object = bpy.data.objects.new(f'physics_pyramid_cloth_{target.bone_name}', pyramid_mesh)
    pyramid_mesh_object.matrix_basis = Matrix.Translation(target.origin)
    pyramid_mesh_object.hide_render = True
    pyramid_mesh_object.display_type = 'WIRE'

    mesh_editor = MeshEditor(pyramid_mesh_object)
    mesh_editor.edit_vertex_group('string', [([STRING], 1.0)])
    mesh_editor.edit_vertex_group('apex', [([APEX], 1.0)])
    mesh_editor.edit_vertex_group('base_a', [([BASE_A], 1.0)])
    mesh_editor.edit_vertex_group('base_b', [([BASE_B], 1.0)])
    mesh_editor.edit_vertex_group('base_c', [([BASE_C], 1.0)])
    mesh_editor.edit_vertex_group('base_d', [([BASE_D], 1.0)])
    mesh_editor.edit_cloth_modifier(
        'physics_pyramid_cloth',
        vertex_group_mass=mesh_editor.edit_vertex_group('physics_pyramid_cloth_pin', [
            ([STRING], 0.6),  # 0.4 - 0.6
            ([APEX], 0.4),  # 0.4 - 0.6
            ([BASE_A, BASE_B, BASE_C, BASE_D], 0.8),  # 0.8 - 0.9
        ]).name,
        time_scale=0.5,
        bending_model='LINEAR'
    )

    return pyramid_mesh_object


def assign_pyramid_weights(
    pyramid_mesh_objects: List[bpy.types.Object],
    deform_mesh_objects: List[bpy.types.Object]
):
    for pyramid_mesh_object in pyramid_mesh_objects:
        target_bone_name = pyramid_mesh_object[PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME]
        parent_bone_name = pyramid_mesh_object[PYRAMID_CLOTH_PARENT_BONE_PROPERTY_NAME]

        pyramid_armature_object = pyramid_mesh_object.parent

        for deform_mesh_object in deform_mesh_objects:
            vertex_group = deform_mesh_object.vertex_groups.get(target_bone_name)
            if vertex_group is None:
                continue

            assign_weights(
                pyramid_armature_object,
                TargetA(
                    target_bone_name,
                    parent_bone_name,
                    deform_mesh_object,
                    pyramid_mesh_object,
                )
            )


def convert_pyramid_mesh_to_cloth(
    pyramid_mesh_objects: List[bpy.types.Object],
    deform_mesh_objects: List[bpy.types.Object]
):
    targets: List[TargetA] = []

    for pyramid_mesh_object in pyramid_mesh_objects:
        target_bone_name = pyramid_mesh_object[PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME]
        parent_bone_name = pyramid_mesh_object[PYRAMID_CLOTH_PARENT_BONE_PROPERTY_NAME]

        for deform_mesh_object in deform_mesh_objects:
            vertex_group = deform_mesh_object.vertex_groups.get(target_bone_name)
            if vertex_group is None:
                continue

            targets.append(TargetA(
                target_bone_name,
                parent_bone_name,
                deform_mesh_object,
                pyramid_mesh_object,
            ))

    for target in targets:
        bpy.ops.object.mode_set(mode='OBJECT')
        pyramid_mesh_object = target.pyramid_mesh_object
        pyramid_mesh: bpy.types.Mesh = pyramid_mesh_object.data
        target_bone_name = target.bone_name
        vertices: List[Vector] = [v.co for v in pyramid_mesh.vertices]

        origin: Vector = pyramid_mesh_object.location.copy()
        direction: Vector = vertices[APEX].normalized()

        pyramid_armature = bpy.data.armatures.new(f'physics_pyramid_{target_bone_name}')
        pyramid_armature_object = bpy.data.objects.new(f'physics_pyramid_{target_bone_name}', pyramid_armature)
        bpy.context.scene.collection.objects.link(pyramid_armature_object)
        pyramid_armature_object.location = origin

        bpy.context.selected_objects.append(pyramid_armature_object)
        bpy.context.view_layer.objects.active = pyramid_armature_object

        bpy.ops.object.mode_set(mode='EDIT')

        bone_length = vertices[APEX].length / 4.5
        bone_vector = direction * bone_length

        # Move the apex vertex into the mesh
        pyramid_mesh.vertices[APEX].co -= bone_vector
        pyramid_mesh.update()

        base_bone_name = f'physics_pyramid_base_{target_bone_name}'
        apex_bone_name = f'physics_pyramid_apex_{target_bone_name}'
        base_a_bone_name = f'physics_pyramid_base_a_{target_bone_name}'
        base_b_bone_name = f'physics_pyramid_base_b_{target_bone_name}'
        base_c_bone_name = f'physics_pyramid_base_c_{target_bone_name}'
        base_d_bone_name = f'physics_pyramid_base_d_{target_bone_name}'

        def create_bones():
            base_bone = pyramid_armature.edit_bones.new(base_bone_name)
            base_bone.head = Vector((0, 0, 0))
            base_bone.tail = Vector((0, 0, 0)) + bone_vector

            apex_bone = pyramid_armature.edit_bones.new(apex_bone_name)
            apex_bone.parent = base_bone
            apex_bone.head = vertices[APEX]
            apex_bone.tail = vertices[APEX] + bone_vector

            base_a_bone = pyramid_armature.edit_bones.new(base_a_bone_name)
            base_a_bone.parent = base_bone
            base_a_bone.head = vertices[BASE_A]
            base_a_bone.tail = vertices[BASE_A] + bone_vector

            base_b_bone = pyramid_armature.edit_bones.new(base_b_bone_name)
            base_b_bone.parent = base_bone
            base_b_bone.head = vertices[BASE_B]
            base_b_bone.tail = vertices[BASE_B] + bone_vector

            base_c_bone = pyramid_armature.edit_bones.new(base_c_bone_name)
            base_c_bone.parent = base_bone
            base_c_bone.head = vertices[BASE_C]
            base_c_bone.tail = vertices[BASE_C] + bone_vector

            base_d_bone = pyramid_armature.edit_bones.new(base_d_bone_name)
            base_d_bone.parent = base_bone
            base_d_bone.head = vertices[BASE_D]
            base_d_bone.tail = vertices[BASE_D] + bone_vector

        create_bones()

        bpy.ops.object.mode_set(mode='OBJECT')

        pyramid_mesh_object.parent = pyramid_armature_object
        pyramid_mesh_object.parent_type = 'BONE'
        pyramid_mesh_object.parent_bone = base_bone_name
        pyramid_mesh_object.matrix_basis = pyramid_armature.bones[base_bone_name].matrix_local.inverted() @ Matrix.Translation(-bone_vector)
        pyramid_mesh_object.hide_render = True
        pyramid_mesh_object.display_type = 'WIRE'

        bpy.ops.object.mode_set(mode='POSE')

        armature_editor = ArmatureEditor(pyramid_armature_object)
        pose_bones = armature_editor.pose_bones
        armature_editor.add_copy_location_constraint(pose_bones[apex_bone_name], pyramid_mesh_object, 'apex', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_a_bone_name], pyramid_mesh_object, 'base_a', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_b_bone_name], pyramid_mesh_object, 'base_b', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_c_bone_name], pyramid_mesh_object, 'base_c', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_d_bone_name], pyramid_mesh_object, 'base_d', 'WORLD')

        bpy.ops.object.mode_set(mode='EDIT')
        assign_weights(pyramid_armature_object, target)

        bpy.ops.object.mode_set(mode='OBJECT')


def assign_weights(pyramid_armature_object: bpy.types.Object, target: TargetA):
    mesh_editor = MeshEditor(target.deform_mesh_object)

    deform_bmesh: bmesh.types.BMesh = bmesh.new()
    deform_bmesh.from_object(target.deform_mesh_object, bpy.context.evaluated_depsgraph_get())

    origin = pyramid_armature_object.location

    target_bone_name = target.bone_name
    apex_bone_name = f'physics_pyramid_apex_{target_bone_name}'
    base_a_bone_name = f'physics_pyramid_base_a_{target_bone_name}'
    base_b_bone_name = f'physics_pyramid_base_b_{target_bone_name}'
    base_c_bone_name = f'physics_pyramid_base_c_{target_bone_name}'
    base_d_bone_name = f'physics_pyramid_base_d_{target_bone_name}'

    pyramid_armature: bpy.types.Armature = pyramid_armature_object.data

    bone_length = pyramid_armature.bones[0].length

    vid2weight = to_vid2weight(deform_bmesh, mesh_editor.get_vertex_group(target_bone_name).index)

    adjacencies, vid2uid = build_adjacencies(deform_bmesh.verts, vid2weight)

    # unified vertex id to numpy id
    uid2nid: Dict[int, int] = {uid: nid for nid, uid in enumerate(set(vid2uid.values()))}
    uid2vids: Dict[int, List[int]] = {uid: [vid for vid in vid2uid if vid2uid[vid] == uid] for uid in vid2uid.values()}
    nid2uid: Dict[int, int] = {v: k for k, v in uid2nid.items()}

    sink_nids: Set[int] = set()

    for index, weight in vid2weight.items():
        if weight > 0:
            continue
        sink_nids.add(uid2nid[vid2uid[index]])

    nid_count = len(uid2nid)

    adjacency_matrix = np.zeros((nid_count, nid_count))
    for (from_uid, to_uid), span in adjacencies.items():
        magnitude = math.exp(-span)
        adjacency_matrix[uid2nid[from_uid], uid2nid[to_uid]] = magnitude
        adjacency_matrix[uid2nid[to_uid], uid2nid[from_uid]] = magnitude

        # np.set_printoptions(precision=3, suppress=True)

    deform_bmesh.verts.ensure_lookup_table()
    vertex_kdtree = mathutils.kdtree.KDTree(nid_count)
    for uid in uid2nid:
        if vid2weight[uid] == 0:
            continue
        vertex_kdtree.insert(deform_bmesh.verts[uid].co, uid)
    vertex_kdtree.balance()

    def collect_nid_weights(position: Vector, _xxx):
        nid_weights: Dict[int, float] = {}
        for _co, near_uid, near_span in vertex_kdtree.find_n(position, 4):
            weight = math.exp(-near_span)
            nid_weights[uid2nid[near_uid]] = weight
        return nid_weights

    bone_name_nid_weights: Dict[str:Dict[int, float]] = {
        apex_bone_name: collect_nid_weights(pyramid_armature.bones[apex_bone_name].tail_local + origin, bone_length),
        base_a_bone_name: collect_nid_weights(pyramid_armature.bones[base_a_bone_name].head_local + origin, bone_length),
        base_b_bone_name: collect_nid_weights(pyramid_armature.bones[base_b_bone_name].head_local + origin, bone_length),
        base_c_bone_name: collect_nid_weights(pyramid_armature.bones[base_c_bone_name].head_local + origin, bone_length),
        base_d_bone_name: collect_nid_weights(pyramid_armature.bones[base_d_bone_name].head_local + origin, bone_length),
    }

    degree_matrix = np.diag(np.sum(adjacency_matrix, axis=1))
    laplacian_matrix = degree_matrix - adjacency_matrix
    eigen_values, eigen_vector = np.linalg.eigh(laplacian_matrix)
    diffusion = np.exp(-eigen_values*5)

    for bone_name in bone_name_nid_weights:
        in_nid_weights = {
            nid: (weight*5 if b == bone_name else -weight)
            for b, n2w in bone_name_nid_weights.items()
            for nid, weight in n2w.items()
        }

        weights = np.zeros(nid_count)
        for _iteration in range(100):
            for nid, weight in in_nid_weights.items():
                weights[nid] = weight

            weights = eigen_vector.T @ weights
            weights = weights * diffusion
            weights = eigen_vector @ weights

            for nid in sink_nids:
                weights[nid] = 0

        # normalize
        weights[weights < 0] = 0
        # weights = weights / np.linalg.norm(weights)
        weights = weights / np.max(weights)

        mesh_editor.edit_vertex_group(bone_name, [
            (uid2vids[nid2uid[nid]], weights[nid].item()) for nid in range(nid_count)
        ])

    deform_bmesh.free()


def to_vid2weight(deform_bm: bmesh.types.BMesh, vertex_group_index) -> Dict[int, float]:
    vid2weight: Dict[int, float] = {}

    deform_layer = deform_bm.verts.layers.deform.verify()

    tri_loops: Tuple[bmesh.types.BMLoop, bmesh.types.BMLoop, bmesh.types.BMLoop]
    for tri_loops in deform_bm.calc_loop_triangles():
        loop_vid2weight = {l.vert.index: l.vert[deform_layer].get(vertex_group_index, 0.0) for l in tri_loops}
        if max(loop_vid2weight.values()) == 0:
            continue

        vid2weight.update(loop_vid2weight)

    return vid2weight


def build_adjacencies(
    vertices: bmesh.types.BMVertSeq,
    vid2weight: Dict[int, float]
) -> Tuple[Dict[Tuple[int, int], float], Dict[int, int]]:

    vertices.ensure_lookup_table()
    vertex_kdtree = mathutils.kdtree.KDTree(len(vid2weight))
    for vid in vid2weight:
        vertex_kdtree.insert(vertices[vid].co, vid)
    vertex_kdtree.balance()

    # vertex id to unified vertex id
    vid2uid_span: Dict[int, Tuple[int, float]] = {}

    # build adjacency dictionary
    adjacencies: Dict[Tuple[int, int], float] = {}

    for from_vid in vid2weight:
        from_vert: bmesh.types.BMVert = vertices[from_vid]

        link_vids: List[int] = [e.other_vert(from_vert).index for e in from_vert.link_edges]

        if len(link_vids) == 0:
            continue

        link_vert_spans: List[float] = [(vertices[vid].co - from_vert.co).length for vid in link_vids]
        link_vert_min_span: float = min(link_vert_spans)
        link_vert_max_span: float = max(link_vert_spans)

        from_uid, span = vid2uid_span.setdefault(from_vid, (from_vid, 0))
        if span > link_vert_min_span:
            vid2uid_span[from_vid] = (from_vid, 0)
            from_uid = from_vid

        # collect unified vertices
        for _co, near_vid, near_span in vertex_kdtree.find_range(from_vert.co, link_vert_max_span):
            if from_vid == near_vid:
                continue

            if near_span < link_vert_min_span:
                near_uid, span = vid2uid_span.setdefault(near_vid, (from_uid, near_span))
                if span > near_span:
                    vid2uid_span[near_vid] = (from_uid, near_span)
                    near_uid = from_uid
            elif near_vid not in link_vids:
                continue
            else:
                near_uid, _span = vid2uid_span.setdefault(near_vid, (near_vid, near_span))

            if from_uid == near_uid:
                continue

            adjacencies[(from_uid, near_uid)] = near_span

    vid2uid = {vid: uid for vid, (uid, _span) in vid2uid_span.items()}
    return {
        (vid2uid[from_xid], vid2uid[near_xid]): span
        for (from_xid, near_xid), span in adjacencies.items()
    }, vid2uid


def collect_near_vert_indices(link_vert_indices: List[int], near_vert_indices: List[int], index: int) -> bool:
    if len(link_vert_indices) == 0:
        return False

    if index in link_vert_indices:
        link_vert_indices.remove(index)

    near_vert_indices.append(index)
    return True


def to_pyramid_vertices(deform_bm: bmesh.types.BMesh, target: Target, base_area_factor: float) -> Tuple[Vector, List[Vector], Dict[int, float]]:
    apex_vertex, deform_vertex_index_weights = find_apex_vertex(deform_bm, target)
    base_vertices = find_base_vertices(deform_bm, target, deform_vertex_index_weights, base_area_factor)
    return apex_vertex, base_vertices, deform_vertex_index_weights


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
            # if vertex_weights[index] == 0:
            #     continue
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
        parent_bone_name: str
        origin: Vector
        direction: Vector

        if breast_bone_direction_vector.z < -0.6:
            if not breast_bone.use_connect:
                raise MessageException('Unsupported breast bone structure.') from None

            parent_bone_name = breast_bone.parent.parent.name
            direction = breast_bone.parent.vector.normalized()
            origin = breast_bone.parent.head + breast_bone.vector / 2 + head_tail * breast_bone.parent.vector

        elif -0.4 < breast_bone_direction_vector.z < +0.4:
            parent_bone_name = breast_bone.parent.name
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
                parent_bone_name,
                mesh_object,
                vertex_group,
                origin,
                direction,
            ))

    return targets


class AddPyramidMeshByBreastBoneOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.add_pyramid_mesh_by_breast_bone'
    bl_label = _('Add Pyramid Mesh by Breast Bone')
    bl_options = {'REGISTER', 'UNDO'}

    head_tail: bpy.props.FloatProperty(name=_('Head/Tail'), default=0.5, min=0.0, max=1.0, step=10)
    spring_length_ratio: bpy.props.FloatProperty(name=_('Spring Length Ratio'), default=5.0, min=1.0, max=100.0, step=10)
    base_area_factor: bpy.props.FloatProperty(name=_('Vertex Shift'), default=0.1, min=0.0, max=100.0, step=10)

    @classmethod
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

            add_pyramid_mesh(
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


class ConvertPyramidMeshToClothOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_pyramid_mesh_to_cloth'
    bl_label = _('Convert Pyramid Mesh to Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        pyramid_mesh_count = 0
        target_mesh_count = 0
        target_armature_count = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                if PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME in obj:
                    pyramid_mesh_count += 1
                else:
                    target_mesh_count += 1

            if obj.type == 'ARMATURE':
                target_armature_count += 1

            if pyramid_mesh_count > 0 and target_mesh_count > 0 and target_armature_count > 0:
                return True

        return False

    def execute(self, context: bpy.types.Context):
        try:
            armature_object: bpy.types.Armature
            pyramid_mesh_objects: List[bpy.types.Object] = []
            deform_mesh_objects: List[bpy.types.Object] = []

            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    if PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME in obj:
                        pyramid_mesh_objects.append(obj)
                    else:
                        deform_mesh_objects.append(obj)

                if obj.type == 'ARMATURE':
                    armature_object = obj

            convert_pyramid_mesh_to_cloth(
                pyramid_mesh_objects,
                deform_mesh_objects
            )

        except MessageException as ex:
            self.report(type={'ERROR'}, message=str(ex))
            return {'CANCELLED'}

        return {'FINISHED'}


class AssignPyramidWeightsOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.assign_pyramid_weights'
    bl_label = _('Assign Pyramid Weights')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        pyramid_mesh_count = 0
        target_mesh_count = 0
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            if PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME in obj:
                pyramid_mesh_count += 1
            else:
                target_mesh_count += 1

            if pyramid_mesh_count > 0 and target_mesh_count > 0:
                return True

        return False

    def execute(self, context: bpy.types.Context):
        try:
            pyramid_mesh_objects: List[bpy.types.Object] = []
            deform_mesh_objects: List[bpy.types.Object] = []

            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    continue

                if PYRAMID_CLOTH_TARGET_BONE_PROPERTY_NAME in obj:
                    pyramid_mesh_objects.append(obj)
                else:
                    deform_mesh_objects.append(obj)

            assign_pyramid_weights(
                pyramid_mesh_objects,
                deform_mesh_objects
            )

        except MessageException as ex:
            self.report(type={'ERROR'}, message=str(ex))
            return {'CANCELLED'}

        return {'FINISHED'}
