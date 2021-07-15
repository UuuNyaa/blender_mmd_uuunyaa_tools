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
    deform_mesh_object: bpy.types.Object
    vertex_group: bpy.types.VertexGroup
    origin: Vector
    direction: Vector


STRING = 0
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
        deform_bm: bmesh.types.BMesh = bmesh.new()
        deform_bm.from_object(target.deform_mesh_object, bpy.context.evaluated_depsgraph_get())

        apex_vertex, base_vertices, deform_vertex_index_weights = to_pyramid_vertices(deform_bm, target, base_area_factor)
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

        bone_length = vertices[APEX].length / 4.5
        bone_vector = target.direction * bone_length

        # Move the apex vertex into the mesh
        vertices[APEX] -= bone_vector

        base_bone_name = f'mmd_uuunyaa_physics_base_{target.bone_name}'
        base_bone = pyramid_armature.edit_bones.new(base_bone_name)
        base_bone.head = Vector((0, 0, 0))
        base_bone.tail = Vector((0, 0, 0)) + bone_vector

        apex_bone_name = f'mmd_uuunyaa_physics_apex_{target.bone_name}'
        apex_bone = pyramid_armature.edit_bones.new(apex_bone_name)
        apex_bone.parent = base_bone
        apex_bone.head = vertices[APEX]
        apex_bone.tail = vertices[APEX] + bone_vector

        base_a_bone_name = f'mmd_uuunyaa_physics_base_a_{target.bone_name}'
        base_a_bone = pyramid_armature.edit_bones.new(base_a_bone_name)
        base_a_bone.parent = base_bone
        base_a_bone.head = vertices[BASE_A]
        base_a_bone.tail = vertices[BASE_A] + bone_vector

        base_b_bone_name = f'mmd_uuunyaa_physics_base_b_{target.bone_name}'
        base_b_bone = pyramid_armature.edit_bones.new(base_b_bone_name)
        base_b_bone.parent = base_bone
        base_b_bone.head = vertices[BASE_B]
        base_b_bone.tail = vertices[BASE_B] + bone_vector

        base_c_bone_name = f'mmd_uuunyaa_physics_base_c_{target.bone_name}'
        base_c_bone = pyramid_armature.edit_bones.new(base_c_bone_name)
        base_c_bone.parent = base_bone
        base_c_bone.head = vertices[BASE_C]
        base_c_bone.tail = vertices[BASE_C] + bone_vector

        base_d_bone_name = f'mmd_uuunyaa_physics_base_d_{target.bone_name}'
        base_d_bone = pyramid_armature.edit_bones.new(base_d_bone_name)
        base_d_bone.parent = base_bone
        base_d_bone.head = vertices[BASE_D]
        base_d_bone.tail = vertices[BASE_D] + bone_vector
        pyramid_armature_object.update_from_editmode()

        pyramid_mesh = bpy.data.meshes.new(f'mmd_uuunyaa_physics_cloth_{target.bone_name}')
        pyramid_mesh.from_pydata(vertices, [
            [STRING, APEX]
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
        mesh_editor.edit_vertex_group('mmd_uuunyaa_string', [([STRING], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_apex', [([APEX], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_a', [([BASE_A], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_b', [([BASE_B], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_c', [([BASE_C], 1.0)])
        mesh_editor.edit_vertex_group('mmd_uuunyaa_base_d', [([BASE_D], 1.0)])
        mesh_editor.edit_cloth_modifier(
            'mmd_uuunyaa_physics_cloth',
            vertex_group_mass=mesh_editor.edit_vertex_group('mmd_uuunyaa_physics_cloth_pin', [
                ([STRING], 0.6),  # 0.4 - 0.6
                ([APEX], 0.4),  # 0.4 - 0.6
                ([BASE_A, BASE_B, BASE_C, BASE_D], 0.8),  # 0.8 - 0.9
            ]).name,
            time_scale=0.5,
            bending_model='LINEAR'
        )

        bpy.ops.object.mode_set(mode='POSE')

        armature_editor = ArmatureEditor(pyramid_armature_object)
        pose_bones = armature_editor.pose_bones
        armature_editor.add_copy_location_constraint(pose_bones[apex_bone_name], pyramid_mesh_object, 'mmd_uuunyaa_apex', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_a_bone_name], pyramid_mesh_object, 'mmd_uuunyaa_base_a', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_b_bone_name], pyramid_mesh_object, 'mmd_uuunyaa_base_b', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_c_bone_name], pyramid_mesh_object, 'mmd_uuunyaa_base_c', 'WORLD')
        armature_editor.add_copy_location_constraint(pose_bones[base_d_bone_name], pyramid_mesh_object, 'mmd_uuunyaa_base_d', 'WORLD')

        bpy.ops.object.mode_set(mode='EDIT')

        deform_bm.verts.ensure_lookup_table()
        deform_vertex_count = len(deform_vertex_index_weights)

        vertex_kdtree = mathutils.kdtree.KDTree(deform_vertex_count)
        for index in deform_vertex_index_weights:
            vertex_kdtree.insert(deform_bm.verts[index].co, index)
        vertex_kdtree.balance()

        adjacencies, vid2uid = build_adjacencies(deform_bm.verts, deform_vertex_index_weights, vertex_kdtree)

        # unified vertex id to numpy id
        uid2nid: Dict[int, int] = {uid: nid for nid, uid in enumerate(set(vid2uid.values()))}
        uid2vids: Dict[int, List[int]] = {uid: [vid for vid in vid2uid if vid2uid[vid] == uid] for uid in vid2uid.values()}
        nid2uid: Dict[int, int] = {v: k for k, v in uid2nid.items()}

        sink_nids: Set[int] = set()

        for index, weight in deform_vertex_index_weights.items():
            if weight > 0:
                continue
            uid = vid2uid[index]
            sink_nids.add(uid2nid[uid])

        nid_count = len(uid2nid)

        adjacency_matrix = np.zeros((nid_count, nid_count))

        for (from_uid, to_uid), distance in adjacencies.items():
            adjacency_matrix[uid2nid[from_uid], uid2nid[to_uid]] = 1/distance
            adjacency_matrix[uid2nid[to_uid], uid2nid[from_uid]] = 1/distance

        # np.set_printoptions(precision=3, suppress=True)

        def collect_nid_weights(position: Vector):
            nid_weights: Dict[int, float] = {}
            min_distance = None
            for _, near_vid, distance in vertex_kdtree.find_n(position, 16):
                if min_distance is None:
                    min_distance = distance

                weight = math.exp(1-distance/min_distance)
                if weight < 0.5:
                    break

                nid_weights[uid2nid[vid2uid[near_vid]]] = weight
            return nid_weights

        degree_matrix = np.diag(np.sum(adjacency_matrix, axis=1))
        laplacian_matrix = degree_matrix - adjacency_matrix
        eigen_values, eigen_vector = np.linalg.eigh(laplacian_matrix)

        weights = np.zeros(nid_count)
        diffusion = np.exp(-eigen_values/np.average(eigen_values))

        bone_name_nid_weights: Dict[str:Dict[int, float]] = {
            apex_bone_name: collect_nid_weights(pose_bones[apex_bone_name].tail + target.origin),
            base_a_bone_name: collect_nid_weights(pose_bones[base_a_bone_name].head + target.origin),
            base_b_bone_name: collect_nid_weights(pose_bones[base_b_bone_name].head + target.origin),
            base_c_bone_name: collect_nid_weights(pose_bones[base_c_bone_name].head + target.origin),
            base_d_bone_name: collect_nid_weights(pose_bones[base_d_bone_name].head + target.origin),
        }

        mesh_editor = MeshEditor(target.deform_mesh_object)
        for bone_name in bone_name_nid_weights:
            in_nid_weights = {
                nid: (weight * 10 if b == bone_name else -weight)
                for b, n2w in bone_name_nid_weights.items()
                for nid, weight in n2w.items()
            }
            # for _ in range(100):
            #     for nid, weight in in_nid_weights.items():
            #         weights[nid] = weight

            #     for nid in sink_nids:
            #         weights[nid] = 0

            #     weights = eigen_vector.T @ weights
            #     weights = weights * diffusion
            #     weights = eigen_vector @ weights

            # for _ in range(10):
            #     for nid, weight in in_nid_weights.items():
            #         if weight < 0:
            #             weights[nid] = weight

            #     weights = eigen_vector.T @ weights
            #     weights = weights * diffusion
            #     weights = eigen_vector @ weights

            #     for nid in sink_nids:
            #         weights[nid] = 0

            for nid, weight in in_nid_weights.items():
                weights[nid] = weight

            for nid in sink_nids:
                weights[nid] = 0.5

            # normalize
            weights = weights/np.max(weights)

            mesh_editor.edit_vertex_group(bone_name, [
                (uid2vids[nid2uid[nid]], weights[nid].item()) for nid in range(nid_count)
            ])

        # print(f'deform_vertex_count={deform_vertex_count}')
        print(f'adjacency_matrix={adjacency_matrix.shape}')
        # print(f'deform_vertex_count={deform_vertex_count}')
        # print(eigen_values)
        # print(eigen_vector)

        np.savetxt('/home/hobby/Workspace/Develop/jupyter/L.txt', laplacian_matrix)
        np.savetxt('/home/hobby/Workspace/Develop/jupyter/A.txt', adjacency_matrix)
        np.savetxt('/home/hobby/Workspace/Develop/jupyter/D.txt', eigen_values)
        np.savetxt('/home/hobby/Workspace/Develop/jupyter/V.txt', eigen_vector)
        np.savetxt('/home/hobby/Workspace/Develop/jupyter/Sink.txt', np.array(list(sink_nids)))

        deform_bm.free()


def build_adjacencies(
    vertices: List[bmesh.types.BMVert],
    deform_vertex_index_weights: Dict[int, float],
    vertex_kdtree: mathutils.kdtree.KDTree
):
    # vertex id to unified vertex id
    vid2uid: Dict[int, int] = {}

    # build adjacency dictionary
    adjacencies: Dict[Tuple[int, int], float] = {}
    for from_vid in deform_vertex_index_weights:
        from_vert: bmesh.types.BMVert = vertices[from_vid]

        link_vids: List[int] = [e.other_vert(from_vert).index for e in from_vert.link_edges]

        if len(link_vids) == 0:
            continue

        link_vert_distances: List[float] = [(vertices[vid].co - from_vert.co).length for vid in link_vids]
        link_vert_min_distance: float = min(link_vert_distances)
        link_vert_max_distance: float = max(link_vert_distances)

        # collect unified vertices
        for _, near_vid, distance in sorted(
            vertex_kdtree.find_range(from_vert.co, link_vert_max_distance),
            lambda v: -deform_vertex_index_weights[v[1]]
        ):
            if from_vid == near_vid:
                continue

            if distance < link_vert_min_distance:
                if from_vid in vid2uid:
                    vid2uid.setdefault(near_vid, vid2uid[from_vid])
                elif near_vid in vid2uid:
                    vid2uid[from_vid] = vid2uid[near_vid]
                else:
                    vid2uid[from_vid] = from_vid
                    vid2uid[near_vid] = from_vid

                continue

            if near_vid not in link_vids:
                continue

            from_uid = vid2uid.setdefault(from_vid, from_vid)
            near_uid = vid2uid.setdefault(near_vid, near_vid)

            if from_uid == near_uid:
                continue

            adjacencies[(from_uid, near_uid)] = distance

    return adjacencies, vid2uid


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
