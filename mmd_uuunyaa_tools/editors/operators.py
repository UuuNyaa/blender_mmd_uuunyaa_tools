# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
from typing import Callable, Dict, Iterable, List, Tuple, Union

import bpy
import rna_prop_ui
from mathutils import Vector
from mmd_uuunyaa_tools.utilities import import_mmd_tools

metarig_mmd_tail_bone_names: Dict[str, str] = {
    'shoulder.L': '肩.L',
    'shoulder.R': '肩.R',
    'forearm.L': '手捩.L',
    'forearm.R': '手捩.R',
    'hand.L': '手首.L',
    'hand.R': '手首.R',
    'thumb.01.L': '親指０.L',
    'thumb.01.R': '親指０.R',
    'thumb.02.L': '親指１.L',
    'thumb.02.R': '親指１.R',
    'thumb.03.L': '親指２.L',
    'thumb.03.R': '親指２.R',
    'f_index.01.L': '人指１.L',
    'f_index.01.R': '人指１.R',
    'f_index.02.L': '人指２.L',
    'f_index.02.R': '人指２.R',
    'f_index.03.L': '人指３.L',
    'f_index.03.R': '人指３.R',
    'f_middle.01.L': '中指１.L',
    'f_middle.01.R': '中指１.R',
    'f_middle.02.L': '中指２.L',
    'f_middle.02.R': '中指２.R',
    'f_middle.03.L': '中指３.L',
    'f_middle.03.R': '中指３.R',
    'f_ring.01.L': '薬指１.L',
    'f_ring.01.R': '薬指１.R',
    'f_ring.02.L': '薬指２.L',
    'f_ring.02.R': '薬指２.R',
    'f_ring.03.L': '薬指３.L',
    'f_ring.03.R': '薬指３.R',
    'f_pinky.01.L': '小指１.L',
    'f_pinky.01.R': '小指１.R',
    'f_pinky.02.L': '小指２.L',
    'f_pinky.02.R': '小指２.R',
    'f_pinky.03.L': '小指３.L',
    'f_pinky.03.R': '小指３.R',
    'thigh.L': '足.L',
    'thigh.R': '足.R',
    'shin.L': 'ひざ.L',
    'shin.R': 'ひざ.R',
    'foot.L': '足首.L',
    'foot.R': '足首.R',
    'toe.L': 'つま先.L',
    'toe.R': 'つま先.R',
    'spine.001': '上半身',
    'spine.003': '上半身2',
    'spine.005': '首',
    'spine.006': '頭',
}


metarig_mmd_head_bone_names: Dict[str, str] = {
    'shoulder.L': '肩.L',
    'shoulder.R': '肩.R',
    'upper_arm.L': '腕.L',
    'upper_arm.R': '腕.R',
    'forearm.L': 'ひじ.L',
    'forearm.R': 'ひじ.R',
    'thumb.01.L': '親指０.L',
    'thumb.01.R': '親指０.R',
    'f_index.01.L': '人指１.L',
    'f_index.01.R': '人指１.R',
    'f_middle.01.L': '中指１.L',
    'f_middle.01.R': '中指１.R',
    'f_ring.01.L': '薬指１.L',
    'f_ring.01.R': '薬指１.R',
    'f_pinky.01.L': '小指１.L',
    'f_pinky.01.R': '小指１.R',
    'thigh.L': '足.L',
    'thigh.R': '足.R',
    'face': '頭',
}


pose_bone_mapping: Dict[str, str] = {
    'root': '全ての親',
    'center': 'センター',
    'groove': 'グルーブ',
    'torso': '上半身',
    'chest': '上半身2',
    'neck': '首',
    'head': '頭',

    'shoulder.L': '左肩',
    'upper_arm_fk.L': '左腕',
    'forearm_fk.L': '左ひじ',
    'hand_fk.L': '左手首',
    'thumb.01.L': '左親指０',
    'thumb.02.L': '左親指１',
    'thumb.03.L': '左親指２',
    'f_index.01.L': '左人指１',
    'f_index.02.L': '左人指２',
    'f_index.03.L': '左人指３',
    'f_middle.01.L': '左中指１',
    'f_middle.02.L': '左中指２',
    'f_middle.03.L': '左中指３',
    'f_ring.01.L': '左薬指１',
    'f_ring.02.L': '左薬指２',
    'f_ring.03.L': '左薬指３',
    'f_pinky.01.L': '左小指１',
    'f_pinky.02.L': '左小指２',
    'f_pinky.03.L': '左小指３',

    'shoulder.R': '右肩',
    'upper_arm_fk.R': '右腕',
    'forearm_fk.R': '右ひじ',
    'hand_fk.R': '右手首',
    'thumb.01.R': '右親指０',
    'thumb.02.R': '右親指１',
    'thumb.03.R': '右親指２',
    'f_index.01.R': '右人指１',
    'f_index.02.R': '右人指２',
    'f_index.03.R': '右人指３',
    'f_middle.01.R': '右中指１',
    'f_middle.02.R': '右中指２',
    'f_middle.03.R': '右中指３',
    'f_ring.01.R': '右薬指１',
    'f_ring.02.R': '右薬指２',
    'f_ring.03.R': '右薬指３',
    'f_pinky.01.R': '右小指１',
    'f_pinky.02.R': '右小指２',
    'f_pinky.03.R': '右小指３',

    'spine_fk': '下半身',
    'thigh_fk.L': '左足',
    'shin_fk.L': '左ひざ',
    'foot_fk.L': '左足首',
    'foot_ik.L': '左足ＩＫ',
    'toe.L': '左つま先ＩＫ',

    'thigh_fk.R': '右足',
    'shin_fk.R': '右ひざ',
    'foot_fk.R': '右足首',
    'foot_ik.R': '右足ＩＫ',
    'toe.R': '右つま先ＩＫ',
}


class MMDArmatureClean(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_clean'
    bl_label = 'Clean MMD Armature'
    bl_description = 'Clean MMD armature.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        active_object = context.active_object
        if active_object is None:
            return False

        if active_object.type != 'ARMATURE':
            return False

        if active_object.mode != 'OBJECT':
            return False

        if active_object.data is None:
            return False

        return True

    def clean_armature(self, mmd_armature: bpy.types.Armature):
        def to_distance(left: Vector, right: Vector) -> float:
            return (left - right).length

        def extend_toward_tail(bone: bpy.types.EditBone, factor: float) -> Vector:
            return bone.head + (bone.tail - bone.head) * factor

        def if_far_then_set(target: bpy.types.EditBone, head=None, tail=None, distance_factor: float = 0.5):
            length = target.length
            threshold = length * distance_factor

            if head is not None:
                if to_distance(target.head, head) > threshold:
                    target.head = head

            if tail is not None:
                if to_distance(target.tail, tail) > threshold:
                    target.tail = tail

        mmd_bones = mmd_armature.edit_bones

        if_far_then_set(mmd_bones['親指２.R'], tail=extend_toward_tail(mmd_bones['親指１.R'], 1.8))
        if_far_then_set(mmd_bones['人指３.R'], tail=extend_toward_tail(mmd_bones['人指２.R'], 1.8))
        if_far_then_set(mmd_bones['中指３.R'], tail=extend_toward_tail(mmd_bones['中指２.R'], 1.8))
        if_far_then_set(mmd_bones['薬指３.R'], tail=extend_toward_tail(mmd_bones['薬指２.R'], 1.8))
        if_far_then_set(mmd_bones['小指３.R'], tail=extend_toward_tail(mmd_bones['小指２.R'], 1.8))
        if_far_then_set(mmd_bones['手首.R'], tail=extend_toward_tail(mmd_bones['ひじ.R'], 1.3))

        if_far_then_set(mmd_bones['親指２.L'], tail=extend_toward_tail(mmd_bones['親指１.L'], 1.8))
        if_far_then_set(mmd_bones['人指３.L'], tail=extend_toward_tail(mmd_bones['人指２.L'], 1.8))
        if_far_then_set(mmd_bones['中指３.L'], tail=extend_toward_tail(mmd_bones['中指２.L'], 1.8))
        if_far_then_set(mmd_bones['薬指３.L'], tail=extend_toward_tail(mmd_bones['薬指２.L'], 1.8))
        if_far_then_set(mmd_bones['小指３.L'], tail=extend_toward_tail(mmd_bones['小指２.L'], 1.8))
        if_far_then_set(mmd_bones['手首.L'], tail=extend_toward_tail(mmd_bones['ひじ.L'], 1.3))

    def execute(self, context: bpy.types.Context):
        bpy.ops.object.mode_set(mode='EDIT')

        self.clean_armature(bpy.context.active_object.data)

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class MMDArmatureAddMetarig(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_add_metarig'
    bl_label = 'Add Human (metarig) from MMD Armature'
    bl_description = 'Add human (metarig) from MMD armature.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        active_object = context.active_object
        if active_object is None:
            return False

        if active_object.type != 'ARMATURE':
            return False

        if active_object.mode != 'OBJECT':
            return False

        if active_object.data is None:
            return False

        return True

    def create_metarig_object(self) -> bpy.types.Object:
        original_cursor_location = bpy.context.scene.cursor.location
        try:
            # Rigifyのメタリグはどこに置いたとしても、
            # 生成ボタンをおすと(0, 0, 0)にRigifyArmatureが生成される。
            # よってメタリグも(0, 0, 0)に生成するようにする。
            bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
            bpy.ops.object.armature_human_metarig_add()
            return bpy.context.object
        finally:
            bpy.context.scene.cursor.location = original_cursor_location

    def fit_scale(self, metarig_object: bpy.types.Object, mmd_object: bpy.types.Object):
        rigify_height = metarig_object.data.bones['spine.006'].tail_local[2]
        mmd_height = mmd_object.data.bones['頭'].tail_local[2]

        scale = mmd_height / rigify_height
        metarig_object.scale = (scale, scale, scale)
        bpy.ops.object.transform_apply(scale=True)

    def fit_bones(self, metarig_bones: bpy.types.ArmatureEditBones, mmd_bones: bpy.types.ArmatureEditBones):
        def to_center(v1: Vector, v2: Vector) -> Vector:
            return (v1 + v2) / 2

        def to_bone_center(bone: bpy.types.EditBone) -> Vector:
            return to_center(bone.head, bone.tail)

        for bone_name in metarig_mmd_head_bone_names.keys():
            mmd_bone = mmd_bones[metarig_mmd_head_bone_names[bone_name]]
            metarig_bones[bone_name].head = mmd_bone.head

        for bone_name in metarig_mmd_tail_bone_names.keys():
            mmd_bone = mmd_bones[metarig_mmd_tail_bone_names[bone_name]]
            metarig_bones[bone_name].tail = mmd_bone.tail

        metarig_bones['spine.004'].tail = to_bone_center(mmd_bones['首'])
        metarig_bones['spine.004'].head = mmd_bones['首'].head
        metarig_bones['spine'].tail = mmd_bones['下半身'].head
        metarig_bones['spine.002'].tail = to_bone_center(mmd_bones['上半身2'])
        metarig_bones['face'].tail = to_bone_center(mmd_bones['頭'])

        下半身_tail = mmd_bones['下半身'].tail
        metarig_bones['spine'].head = 下半身_tail
        metarig_bones['pelvis.L'].head = 下半身_tail
        metarig_bones['pelvis.R'].head = 下半身_tail
        metarig_bones['pelvis.L'].tail[1:3] = [下半身_tail[1]-metarig_bones['spine'].length/2, mmd_bones['下半身'].head[2]]
        metarig_bones['pelvis.R'].tail[1:3] = [下半身_tail[1]-metarig_bones['spine'].length/2, mmd_bones['下半身'].head[2]]

        ひざ_L_length = mmd_bones['ひざ.L'].length
        metarig_bones['heel.02.L'].tail = mmd_bones['ひざ.L'].tail + Vector([+ひざ_L_length / 6, +ひざ_L_length / 8, +0.0])
        metarig_bones['heel.02.L'].head = mmd_bones['ひざ.L'].tail + Vector([-ひざ_L_length / 6, +ひざ_L_length / 8, +0.0])

        ひざ_R_length = mmd_bones['ひざ.R'].length
        metarig_bones['heel.02.R'].tail = mmd_bones['ひざ.R'].tail + Vector([-ひざ_R_length / 6, +ひざ_R_length / 8, +0.0])
        metarig_bones['heel.02.R'].head = mmd_bones['ひざ.R'].tail + Vector([+ひざ_R_length / 6, +ひざ_R_length / 8, +0.0])

        # tail
        metarig_bones['palm.01.L'].tail = mmd_bones['人指１.L'].head
        metarig_bones['palm.02.L'].tail = mmd_bones['中指１.L'].head
        metarig_bones['palm.03.L'].tail = mmd_bones['薬指１.L'].head
        metarig_bones['palm.04.L'].tail = mmd_bones['小指１.L'].head
        metarig_bones['palm.01.R'].tail = mmd_bones['人指１.R'].head
        metarig_bones['palm.02.R'].tail = mmd_bones['中指１.R'].head
        metarig_bones['palm.03.R'].tail = mmd_bones['薬指１.R'].head
        metarig_bones['palm.04.R'].tail = mmd_bones['小指１.R'].head

        足首_L = mmd_bones['足首.L']
        metarig_bones['toe.L'].tail = 足首_L.tail + Vector([+0.0, -足首_L.length / 2, +0.0])

        足首_R = mmd_bones['足首.R']
        metarig_bones['toe.R'].tail = 足首_R.tail + Vector([+0.0, -足首_R.length / 2, +0.0])

        # head
        手捩_L_tail = mmd_bones['手捩.L'].tail
        metarig_bones['palm.01.L'].head = to_center(mmd_bones['人指１.L'].head, 手捩_L_tail)
        metarig_bones['palm.02.L'].head = to_center(mmd_bones['中指１.L'].head, 手捩_L_tail)
        metarig_bones['palm.03.L'].head = to_center(mmd_bones['薬指１.L'].head, 手捩_L_tail)
        metarig_bones['palm.04.L'].head = to_center(mmd_bones['小指１.L'].head, 手捩_L_tail)

        手捩_R_tail = mmd_bones['手捩.R'].tail
        metarig_bones['palm.01.R'].head = to_center(mmd_bones['人指１.R'].head, 手捩_R_tail)
        metarig_bones['palm.02.R'].head = to_center(mmd_bones['中指１.R'].head, 手捩_R_tail)
        metarig_bones['palm.03.R'].head = to_center(mmd_bones['薬指１.R'].head, 手捩_R_tail)
        metarig_bones['palm.04.R'].head = to_center(mmd_bones['小指１.R'].head, 手捩_R_tail)

        # fix straight finger bend problem
        # https://blenderartists.org/t/rigify-fingers-issue/1218987
        # limbs.super_finger
        metarig_bones['thumb.01.L'].roll += math.radians(-45)
        metarig_bones['thumb.02.L'].roll += math.radians(-45)
        metarig_bones['thumb.03.L'].roll += math.radians(-45)
        metarig_bones['f_index.01.L'].roll += math.radians(-45)
        metarig_bones['f_index.02.L'].roll += math.radians(-45)
        metarig_bones['f_index.03.L'].roll += math.radians(-45)
        metarig_bones['f_middle.01.L'].roll += math.radians(-45)
        metarig_bones['f_middle.02.L'].roll += math.radians(-45)
        metarig_bones['f_middle.03.L'].roll += math.radians(-45)
        metarig_bones['f_ring.01.L'].roll += math.radians(-45)
        metarig_bones['f_ring.02.L'].roll += math.radians(-45)
        metarig_bones['f_ring.03.L'].roll += math.radians(-45)
        metarig_bones['f_pinky.01.L'].roll += math.radians(-45)
        metarig_bones['f_pinky.02.L'].roll += math.radians(-45)
        metarig_bones['f_pinky.03.L'].roll += math.radians(-45)

        metarig_bones['thumb.01.R'].roll += math.radians(+45)
        metarig_bones['thumb.02.R'].roll += math.radians(+45)
        metarig_bones['thumb.03.R'].roll += math.radians(+45)
        metarig_bones['f_index.01.R'].roll += math.radians(+45)
        metarig_bones['f_index.02.R'].roll += math.radians(+45)
        metarig_bones['f_index.03.R'].roll += math.radians(+45)
        metarig_bones['f_middle.01.R'].roll += math.radians(+45)
        metarig_bones['f_middle.02.R'].roll += math.radians(+45)
        metarig_bones['f_middle.03.R'].roll += math.radians(+45)
        metarig_bones['f_ring.01.R'].roll += math.radians(+45)
        metarig_bones['f_ring.02.R'].roll += math.radians(+45)
        metarig_bones['f_ring.03.R'].roll += math.radians(+45)
        metarig_bones['f_pinky.01.R'].roll += math.radians(+45)
        metarig_bones['f_pinky.02.R'].roll += math.radians(+45)
        metarig_bones['f_pinky.03.R'].roll += math.radians(+45)

        # fix elbow pole problem
        # https://blenderartists.org/t/rigify-elbow-problem/565285
        metarig_bones['upper_arm.L'].tail += Vector([0, +0.001, 0])
        metarig_bones['upper_arm.R'].tail += Vector([0, +0.001, 0])

        # remove unused mmd_bones
        metarig_face = metarig_bones['face']
        remove_metarig_bones = [
            metarig_bones['breast.L'],
            metarig_bones['breast.R'],
            metarig_face,
            *metarig_face.children_recursive,
        ]
        for metarig_bone in remove_metarig_bones:
            metarig_bones.remove(metarig_bone)

    def pose_bones(self, metarig_bones: Dict[str, bpy.types.PoseBone], mmd_bones: Dict[str, bpy.types.PoseBone]):
        # fix straight finger bend problem
        # https://blenderartists.org/t/rigify-fingers-issue/1218987
        # limbs.super_finger
        metarig_bones['thumb.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['thumb.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_index.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_index.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_middle.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_middle.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_ring.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_ring.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_pinky.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_pinky.01.R'].rigify_parameters.primary_rotation_axis = 'X'

        # fix straight arm IK problem
        # limbs.super_limb
        metarig_bones['upper_arm.L'].rigify_parameters.rotation_axis = 'x'
        metarig_bones['upper_arm.R'].rigify_parameters.rotation_axis = 'x'

    def execute(self, context: bpy.types.Context):
        mmd_object = context.active_object
        metarig_object = self.create_metarig_object()
        self.fit_scale(metarig_object, mmd_object)

        mmd_object.select = True
        metarig_object.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        self.fit_bones(metarig_object.data.edit_bones, mmd_object.data.edit_bones)

        bpy.ops.object.mode_set(mode='POSE')
        self.pose_bones(metarig_object.pose.bones, mmd_object.pose.bones)

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


def add_influence_driver(constraint: bpy.types.Constraint, target, data_path, invert=False):
    driver: bpy.types.Driver = constraint.driver_add('influence').driver
    variable: bpy.types.DriverVariable = driver.variables.new()
    variable.name = 'mmd_rigify_influence'
    variable.targets[0].id = target
    variable.targets[0].data_path = data_path
    driver.expression = ('-' if invert else '+') + variable.name


def copy_local(org_armature_object, pose_bones, mmd_name, org_name, influence_data_path):
    constraint = pose_bones[mmd_name].constraints.new('COPY_TRANSFORMS')
    constraint.name = 'mmd_rigify_copy_transforms'
    constraint.target = org_armature_object
    constraint.subtarget = org_name
    constraint.target_space = 'LOCAL'
    constraint.owner_space = 'LOCAL'

    add_influence_driver(constraint, org_armature_object, influence_data_path)


def copy_parent(org_armature_object, pose_bones, mmd_name, org_name, influence_data_path):
    constraint = pose_bones[mmd_name].constraints.new('COPY_TRANSFORMS')
    constraint.name = 'mmd_rigify_copy_transforms'
    constraint.target = org_armature_object
    constraint.subtarget = org_name
    constraint.target_space = 'LOCAL_WITH_PARENT'
    constraint.owner_space = 'LOCAL_WITH_PARENT'

    add_influence_driver(constraint, org_armature_object, influence_data_path)


def copy_spine(org_armature_object, pose_bones, mmd_name, org_name, influence_data_path):
    mmd_bone = pose_bones[mmd_name]
    constraint = mmd_bone.constraints.new('COPY_LOCATION')
    constraint.name = 'mmd_rigify_copy_location'
    constraint.target = org_armature_object
    constraint.subtarget = 'ORG-spine.001'
    constraint.target_space = 'WORLD'
    constraint.owner_space = 'WORLD'
    add_influence_driver(constraint, org_armature_object, influence_data_path)

    constraint = mmd_bone.constraints.new('COPY_ROTATION')
    constraint.name = 'mmd_rigify_copy_rotation'
    constraint.target = org_armature_object
    constraint.subtarget = 'ORG-spine'
    constraint.target_space = 'LOCAL'
    constraint.owner_space = 'LOCAL'
    constraint.invert_x = False
    constraint.invert_y = True
    constraint.invert_z = True
    add_influence_driver(constraint, org_armature_object, influence_data_path)


def copy_toe(org_armature_object, pose_bones, mmd_name, org_name, influence_data_path):
    mmd_bone = pose_bones[mmd_name]
    constraint = mmd_bone.constraints.new('COPY_LOCATION')
    constraint.name = 'mmd_rigify_copy_location'
    constraint.target = org_armature_object
    constraint.subtarget = org_name
    constraint.target_space = 'LOCAL'
    constraint.owner_space = 'LOCAL'
    add_influence_driver(constraint, org_armature_object, influence_data_path)

    constraint = mmd_bone.constraints.new('COPY_ROTATION')
    constraint.name = 'mmd_rigify_copy_rotation'
    constraint.target = org_armature_object
    constraint.subtarget = org_name
    constraint.target_space = 'LOCAL'
    constraint.owner_space = 'LOCAL'
    constraint.invert_x = True
    constraint.invert_y = False
    constraint.invert_z = False
    add_influence_driver(constraint, org_armature_object, influence_data_path)


bind_bone_mapping: List[Tuple[str, str, str, Callable]] = [
    ('センター', 'center', 'torso_influence', copy_parent),
    ('グルーブ', 'groove', 'torso_influence', copy_parent),
    ('上半身', 'ORG-spine.001', 'torso_influence', copy_parent),
    ('上半身2', 'ORG-spine.002', 'torso_influence', copy_parent),
    ('首', 'ORG-spine.005', 'torso_influence', copy_parent),
    ('頭', 'ORG-spine.006', 'torso_influence', copy_parent),

    ('肩.L', 'ORG-shoulder.L', 'torso_influence', copy_parent),
    ('腕.L', 'ORG-upper_arm.L', 'arm_l_influence', copy_local),
    ('ひじ.L', 'ORG-forearm.L', 'arm_l_influence', copy_local),
    ('手首.L', 'ORG-hand.L', 'arm_l_influence', copy_local),
    ('親指０.L', 'ORG-thumb.01.L', 'arm_l_influence', copy_local),
    ('親指１.L', 'ORG-thumb.02.L', 'arm_l_influence', copy_local),
    ('親指２.L', 'ORG-thumb.03.L', 'arm_l_influence', copy_local),
    ('人指０.L', 'ORG-palm.01.L', 'arm_l_influence', copy_local),
    ('人指１.L', 'ORG-f_index.01.L', 'arm_l_influence', copy_local),
    ('人指２.L', 'ORG-f_index.02.L', 'arm_l_influence', copy_local),
    ('人指３.L', 'ORG-f_index.03.L', 'arm_l_influence', copy_local),
    ('中指０.L', 'ORG-palm.02.L', 'arm_l_influence', copy_local),
    ('中指１.L', 'ORG-f_middle.01.L', 'arm_l_influence', copy_local),
    ('中指２.L', 'ORG-f_middle.02.L', 'arm_l_influence', copy_local),
    ('中指３.L', 'ORG-f_middle.03.L', 'arm_l_influence', copy_local),
    ('薬指０.L', 'ORG-palm.03.L', 'arm_l_influence', copy_local),
    ('薬指１.L', 'ORG-f_ring.01.L', 'arm_l_influence', copy_local),
    ('薬指２.L', 'ORG-f_ring.02.L', 'arm_l_influence', copy_local),
    ('薬指３.L', 'ORG-f_ring.03.L', 'arm_l_influence', copy_local),
    ('小指０.L', 'ORG-palm.04.L', 'arm_l_influence', copy_local),
    ('小指１.L', 'ORG-f_pinky.01.L', 'arm_l_influence', copy_local),
    ('小指２.L', 'ORG-f_pinky.02.L', 'arm_l_influence', copy_local),
    ('小指３.L', 'ORG-f_pinky.03.L', 'arm_l_influence', copy_local),

    ('肩.R', 'ORG-shoulder.R', 'torso_influence', copy_parent),
    ('腕.R', 'ORG-upper_arm.R', 'arm_r_influence', copy_local),
    ('ひじ.R', 'ORG-forearm.R', 'arm_r_influence', copy_local),
    ('手首.R', 'ORG-hand.R', 'arm_r_influence', copy_local),
    ('親指０.R', 'ORG-thumb.01.R', 'arm_r_influence', copy_local),
    ('親指１.R', 'ORG-thumb.02.R', 'arm_r_influence', copy_local),
    ('親指２.R', 'ORG-thumb.03.R', 'arm_r_influence', copy_local),
    ('人指０.R', 'ORG-palm.01.R', 'arm_r_influence', copy_local),
    ('人指１.R', 'ORG-f_index.01.R', 'arm_r_influence', copy_local),
    ('人指２.R', 'ORG-f_index.02.R', 'arm_r_influence', copy_local),
    ('人指３.R', 'ORG-f_index.03.R', 'arm_r_influence', copy_local),
    ('中指０.R', 'ORG-palm.02.R', 'arm_r_influence', copy_local),
    ('中指１.R', 'ORG-f_middle.01.R', 'arm_r_influence', copy_local),
    ('中指２.R', 'ORG-f_middle.02.R', 'arm_r_influence', copy_local),
    ('中指３.R', 'ORG-f_middle.03.R', 'arm_r_influence', copy_local),
    ('薬指０.R', 'ORG-palm.03.R', 'arm_r_influence', copy_local),
    ('薬指１.R', 'ORG-f_ring.01.R', 'arm_r_influence', copy_local),
    ('薬指２.R', 'ORG-f_ring.02.R', 'arm_r_influence', copy_local),
    ('薬指３.R', 'ORG-f_ring.03.R', 'arm_r_influence', copy_local),
    ('小指０.R', 'ORG-palm.04.R', 'arm_r_influence', copy_local),
    ('小指１.R', 'ORG-f_pinky.01.R', 'arm_r_influence', copy_local),
    ('小指２.R', 'ORG-f_pinky.02.R', 'arm_r_influence', copy_local),
    ('小指３.R', 'ORG-f_pinky.03.R', 'arm_r_influence', copy_local),


    ('下半身', 'ORG-spine', 'torso_influence', copy_spine),
    ('足.L', 'ORG-thigh.L', 'leg_l_influence', copy_local),
    ('ひざ.L', 'ORG-shin.L', 'leg_l_influence', copy_local),
    ('足首.L', 'ORG-foot.L', 'leg_l_influence', copy_local),
    ('足ＩＫ.L', 'ORG-foot.L', 'leg_l_influence', copy_parent),
    ('足先EX.L', 'ORG-toe.L', 'leg_l_influence', copy_toe),

    ('足.R', 'ORG-thigh.R', 'leg_r_influence', copy_local),
    ('ひざ.R', 'ORG-shin.R', 'leg_r_influence', copy_local),
    ('足首.R', 'ORG-foot.R', 'leg_r_influence', copy_local),
    ('足ＩＫ.R', 'ORG-foot.R', 'leg_r_influence', copy_parent),
    ('足先EX.R', 'ORG-toe.R', 'leg_r_influence', copy_toe),

]


class MMDRigifyIntegrate(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_rigify_integrate'
    bl_label = 'Integrate Rigify and MMD Armatures'
    bl_description = 'Integrate Rigify and MMD armatures.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def find_armature_objects(cls, objects: Iterable[bpy.types.Object]) -> (Union[bpy.types.Object, None], Union[bpy.types.Object, None]):
        mmd_tools = import_mmd_tools()

        rigify_object: Union[bpy.types.Object, None] = None
        mmd_object: Union[bpy.types.Object, None] = None

        for obj in objects:
            if 'rig_id' in obj.data:
                rigify_object = obj
                continue

            mmd_root = mmd_tools.core.model.Model.findRoot(obj)
            if mmd_root is not None:
                mmd_object = obj
                continue

        return (rigify_object, mmd_object)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) != 2:
            return False

        rigify_object, mmd_object = cls.find_armature_objects(selected_objects)

        return mmd_object is not None and rigify_object is not None

    def edit_bones(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: bpy.types.Object):
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones
        mmd_edit_bones: bpy.types.ArmatureEditBones = mmd_armature_object.data.edit_bones

        center_bone = rig_edit_bones.new('center')
        center_bone.layers = [i == 4 for i in range(32)]
        center_bone.head = mmd_edit_bones['センター'].head
        center_bone.tail = mmd_edit_bones['センター'].tail

        groove_bone = rig_edit_bones.new('groove')
        groove_bone.layers = [i == 4 for i in range(32)]
        groove_bone.head = mmd_edit_bones['グルーブ'].head
        groove_bone.tail = mmd_edit_bones['グルーブ'].tail

        torso_bone = rig_edit_bones['torso']
        torso_bone.head = mmd_edit_bones['上半身'].head
        torso_bone.tail[2] = torso_bone.head[2]

        center_bone.parent = rig_edit_bones['MCH-torso.parent']
        groove_bone.parent = center_bone
        torso_bone.parent = groove_bone

    def imitate_mmd_behavior(self, rigify_armature_object: bpy.types.Object):
        """Imitate the behavior of MMD armature as much as possible."""
        pose_bones = rigify_armature_object.pose.bones

        pose_bones["upper_arm_parent.L"]["IK_FK"] = 1.000
        pose_bones["upper_arm_parent.R"]["IK_FK"] = 1.000
        pose_bones['upper_arm_parent.L']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.R']['IK_Stretch'] = 0.000

        pose_bones['thigh_parent.L']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.R']['IK_Stretch'] = 0.000

        pose_bones['thigh_parent.L']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.R']['IK_parent'] = 1  # root

        # torso hack
        pose_bones["torso"]["neck_follow"] = 1.000  # follow chest
        pose_bones["torso"]["head_follow"] = 1.000  # follow chest

        bones: bpy.types.ArmatureBones = rigify_armature_object.data.bones

        # 上半身２
        pose_bones["MCH-spine.003"].constraints['Copy Transforms'].influence = 0.000
        pose_bones["MCH-spine.002"].constraints['Copy Transforms'].influence = 1.000

        # 上半身
        bones["tweak_spine.001"].use_inherit_rotation = False

        # 下半身
        bones["spine_fk"].use_inherit_rotation = False

    def fit_bone_rotations(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: bpy.types.Object):
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones
        mmd_edit_bones: bpy.types.ArmatureEditBones = mmd_armature_object.data.edit_bones

        for mmd_name, org_name, _, _ in bind_bone_mapping:
            if mmd_name not in mmd_edit_bones:
                continue
            mmd_edit_bones[mmd_name].roll = rig_edit_bones[org_name].roll

    def pose_bone_constraints(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: bpy.types.Object):
        rig_pose_bones: Dict[str, bpy.types.PoseBone] = rigify_armature_object.pose.bones
        rig_bone_groups = rigify_armature_object.pose.bone_groups
        mmd_pose_bones: Dict[str, bpy.types.PoseBone] = mmd_armature_object.pose.bones

        rig_pose_bones['center'].bone_group = rig_bone_groups['Tweak']
        rig_pose_bones['groove'].bone_group = rig_bone_groups['Tweak']

        torso_pose_bone = rig_pose_bones['torso']
        for influence_prop_name in set([g for _, _, g, _ in bind_bone_mapping]):
            rna_prop_ui.rna_idprop_ui_create(
                torso_pose_bone,
                influence_prop_name,
                default=0.000,
                min=0.000, max=1.000,
                soft_min=None, soft_max=None,
                description=None,
                overridable=True,
                subtype=None
            )

        for mmd_name, org_name, influence_prop_name, edit in bind_bone_mapping:
            if mmd_name not in mmd_pose_bones:
                continue

            mmd_pose_bone = mmd_pose_bones[mmd_name]
            for constraint in mmd_pose_bone.constraints:
                if constraint.name.startswith('mmd_rigify_'):
                    mmd_pose_bone.constraints.remove(constraint)

            edit(rigify_armature_object, mmd_pose_bones, mmd_name, org_name, f'pose.bones["torso"]["{influence_prop_name}"]')

    def assign_mmd_bone_names(self, rigify_armature_object: bpy.types.Object):
        pose_bones = rigify_armature_object.pose.bones

        mmd_bone_names = set(pose_bone_mapping.values())

        # clear mmd pose bone names
        for pose_bone in pose_bones:
            if pose_bone.mmd_bone.name_j not in mmd_bone_names:
                continue

            pose_bone.mmd_bone.name_j = ''

        for name_rigify, name_mmd in pose_bone_mapping.items():
            if name_rigify not in pose_bones:
                continue

            pose_bones[name_rigify].mmd_bone.name_j = name_mmd

    def change_mmd_bone_layer(self, mmd_armature_object: bpy.types.Object):
        mmd_bones: Dict[str, bpy.types.Bone] = mmd_armature_object.data.bones
        for mmd_name, _, _, _ in bind_bone_mapping:
            if mmd_name not in mmd_bones:
                continue
            mmd_bones[mmd_name].layers[23] = True

    def execute(self, context: bpy.types.Context):
        rigify_armature_object, mmd_armature_object = self.find_armature_objects(bpy.context.selected_objects)

        bpy.ops.object.mode_set(mode='EDIT')
        self.edit_bones(rigify_armature_object, mmd_armature_object)
        self.fit_bone_rotations(rigify_armature_object, mmd_armature_object)

        bpy.ops.object.mode_set(mode='POSE')
        self.imitate_mmd_behavior(rigify_armature_object)
        self.assign_mmd_bone_names(rigify_armature_object)
        self.pose_bone_constraints(rigify_armature_object, mmd_armature_object)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.change_mmd_bone_layer(mmd_armature_object)

        return {'FINISHED'}


class OperatorPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_mmd_rigify'
    bl_label = 'UuuNyaa MMD Rigify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_context = ''

    @ classmethod
    def poll(cls, context):
        if not context.object:
            return False

        return context.object.type == 'ARMATURE' and context.active_object.data.get('rig_id') is not None

    def draw(self, context: bpy.types.Context):
        torso_pose_bone = bpy.context.active_object.pose.bones['torso']
        if 'torso_influence' not in torso_pose_bone:
            return

        layout = self.layout
        col = layout.column()
        col.label(text='Influences:')
        row = col.row()
        row.prop(torso_pose_bone, '["torso_influence"]', text='Torso', slider=True)

        row = col.row()
        row.prop(torso_pose_bone, '["arm_l_influence"]', text='Arm.L', slider=True)
        row.prop(torso_pose_bone, '["arm_r_influence"]', text='Arm.R', slider=True)
        row = col.row()
        row.prop(torso_pose_bone, '["leg_l_influence"]', text='Leg.L', slider=True)
        row.prop(torso_pose_bone, '["leg_r_influence"]', text='Leg.R', slider=True)


class MMDArmatureAssignBoneNames(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_assign_bone_names'
    bl_label = 'Assign MMD Compatible Bone Names'
    bl_description = 'Assign MMD compatible bone names.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        active_object = bpy.context.active_object

        if active_object is None:
            return False

        if active_object.type != 'ARMATURE':
            return False

        if active_object.mode != 'OBJECT':
            return False

        return True

    def execute(self, context: bpy.types.Context):
        mmd_armature_object = bpy.context.active_object

        pose_bones = mmd_armature_object.pose.bones

        mmd_bone_names = set(pose_bone_mapping.values())

        # clear mmd pose bone names
        for pose_bone in pose_bones:
            if pose_bone.mmd_bone.name_j not in mmd_bone_names:
                continue

            pose_bone.mmd_bone.name_j = ''

        for name_rigify, name_mmd in pose_bone_mapping.items():
            if name_rigify not in pose_bones:
                continue

            pose_bones[name_rigify].mmd_bone.name_j = name_mmd

        return {'FINISHED'}
