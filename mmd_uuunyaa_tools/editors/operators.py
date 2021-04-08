# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
from typing import Dict, Iterable, List, Union

import bpy
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


mmd_rigify_bone_names: Dict[str, str] = {
    '足首D.L': 'DEF-foot.L',
    '足首D.R': 'DEF-foot.R',
    '足先EX.L': 'DEF-toe.L',
    '足先EX.R': 'DEF-toe.R',

    '肩.L': 'DEF-shoulder.L',
    '肩.R': 'DEF-shoulder.R',
    '手首.L': 'DEF-hand.L',
    '手首.R': 'DEF-hand.R',
    '親指１.L': 'DEF-thumb.02.L',
    '親指１.R': 'DEF-thumb.02.R',
    '親指２.L': 'DEF-thumb.03.L',
    '親指２.R': 'DEF-thumb.03.R',
    '人指２.L': 'DEF-f_index.02.L',
    '人指２.R': 'DEF-f_index.02.R',
    '人指３.L': 'DEF-f_index.03.L',
    '人指３.R': 'DEF-f_index.03.R',
    '中指２.L': 'DEF-f_middle.02.L',
    '中指２.R': 'DEF-f_middle.02.R',
    '中指３.L': 'DEF-f_middle.03.L',
    '中指３.R': 'DEF-f_middle.03.R',
    '薬指２.L': 'DEF-f_ring.02.L',
    '薬指２.R': 'DEF-f_ring.02.R',
    '薬指３.L': 'DEF-f_ring.03.L',
    '薬指３.R': 'DEF-f_ring.03.R',
    '小指２.L': 'DEF-f_pinky.02.L',
    '小指２.R': 'DEF-f_pinky.02.R',
    '小指３.L': 'DEF-f_pinky.03.L',
    '小指３.R': 'DEF-f_pinky.03.R',

    '下半身': 'DEF-spine',
    '上半身': 'DEF-spine.001',
    '上半身2': 'DEF-spine.003',
    '首': 'DEF-spine.005',
    '頭': 'DEF-spine.006',

    '足D.L': 'DEF-thigh.L.001',
    '足D.R': 'DEF-thigh.R.001',
    'ひざD.L': 'DEF-shin.L.001',
    'ひざD.R': 'DEF-shin.R.001',

    '腕.L': 'DEF-upper_arm.L',
    '腕.R': 'DEF-upper_arm.R',
    '腕捩.L': 'DEF-upper_arm.L.001',
    '腕捩.R': 'DEF-upper_arm.R.001',
    'ひじ.L': 'DEF-forearm.L',
    'ひじ.R': 'DEF-forearm.R',
    '手捩.L': 'DEF-forearm.L.001',
    '手捩.R': 'DEF-forearm.R.001',
    '親指０.L': 'DEF-thumb.01.L',
    '親指０.R': 'DEF-thumb.01.R',
    '人指１.L': 'DEF-f_index.01.L',
    '人指１.R': 'DEF-f_index.01.R',
    '中指１.L': 'DEF-f_middle.01.L',
    '中指１.R': 'DEF-f_middle.01.R',
    '薬指１.L': 'DEF-f_ring.01.L',
    '薬指１.R': 'DEF-f_ring.01.R',
    '小指１.L': 'DEF-f_pinky.01.L',
    '小指１.R': 'DEF-f_pinky.01.R',
}


pose_bone_mappings: Dict[str, Dict[str, str]] = {
    'RIGIFY': {
        'root': '全ての親',
        'MCH-torso.parent': 'センター',
        'spine_fk.001': '上半身',
        'spine_fk.002': '上半身2',
        'neck': '首',
        'head': '頭',
        'shoulder.L': '左肩',
        'upper_arm_fk.L': '左腕',
        'forearm_fk.L': '左ひじ',
        'hand_fk.L': '左手首',
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
        'thumb.01.L': '左親指０',
        'thumb.02.L': '左親指１',
        'thumb.03.L': '左親指２',
        'shoulder.R': '右肩',
        'upper_arm_fk.R': '右腕',
        'forearm_fk.R': '右ひじ',
        'hand_fk.R': '右手首',
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
        'thumb.01.R': '右親指０',
        'thumb.02.R': '右親指１',
        'thumb.03.R': '右親指２',
        'groove': 'グルーブ',
        'torso': '下半身',
        'thigh_fk.L': '左足',
        'shin_fk.L': '左ひざ',
        'foot_fk.L': '左足首',
        'foot_ik.L': '左足ＩＫ',
        'toe.L': '左つま先ＩＫ',
        'thigh_fk.R': '右足',
        'shin_fk.R': '右ひざ',
        'foot_fk.R': '右足首',
        'foot_ik.R': '右足ＩＫ',
        'toe.L': '右つま先ＩＫ',
    },
}


class MMDArmatureClean(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_clean'
    bl_label = 'Clean MMD Armature'
    bl_description = 'Clean MMD armature.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
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
        mmd_bones = mmd_armature.edit_bones

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

    def execute(self, context):
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
    def poll(cls, context):
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

    def filter_required_mmd_bones(self, mmd_bones: List[bpy.types.Bone]):
        required_bone_names = set([
            '下半身',
            *metarig_mmd_tail_bone_names.values(),
            *metarig_mmd_head_bone_names.values()
        ])

        required_bones: Dict[str, bpy.types.Bone] = {}

        for bone in mmd_bones:
            if bone.name in required_bone_names:
                required_bones[bone.name] = bone

        difference = required_bone_names ^ required_bones.keys()
        if len(difference) > 0:
            raise KeyError(f'MMD armature has no required bone. {difference}')

        return required_bones

    def create_metarig(self) -> bpy.types.Object:
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
        # 縮尺をだいたい合わせる
        rigify_height = metarig_object.data.bones['spine.006'].tail_local[2]
        mmd_height = mmd_object.data.bones['頭'].tail_local[2]

        scale = mmd_height / rigify_height
        metarig_object.scale = (scale, scale, scale)
        bpy.ops.object.transform_apply(scale=True)

    def fit_bones(self, metarig_bones: Dict[str, bpy.types.EditBone], mmd_bones: Dict[str, bpy.types.EditBone]):
        def to_center(v1: Vector, v2: Vector) -> Vector:
            return (v1 + v2) / 2

        def to_bone_center(bone: bpy.types.EditBone) -> Vector:
            return to_center(bone.head, bone.tail)

        for bone_name in metarig_mmd_head_bone_names.keys():
            if bone_name not in metarig_mmd_head_bone_names:
                continue
            mmd_bone = mmd_bones[metarig_mmd_head_bone_names[bone_name]]
            metarig_bones[bone_name].head = mmd_bone.head

        for bone_name in metarig_mmd_tail_bone_names.keys():
            if bone_name not in metarig_mmd_tail_bone_names:
                continue
            mmd_bone = mmd_bones[metarig_mmd_tail_bone_names[bone_name]]
            metarig_bones[bone_name].tail = mmd_bone.tail

        # pelvisの先端は特に設定していない。
        metarig_bones['spine.004'].tail = to_bone_center(mmd_bones['首'])
        metarig_bones['spine.004'].head = mmd_bones['首'].head
        metarig_bones['spine'].tail = mmd_bones['下半身'].head
        metarig_bones['spine.002'].tail = to_bone_center(mmd_bones['上半身2'])
        metarig_bones['face'].tail = to_bone_center(mmd_bones['頭'])

        下半身_tail = mmd_bones['下半身'].tail
        metarig_bones['spine'].head = 下半身_tail
        metarig_bones['pelvis.L'].head = 下半身_tail
        metarig_bones['pelvis.R'].head = 下半身_tail

        ひざ_L = mmd_bones['ひざ.L']
        ひざ_L_tail = ひざ_L.tail
        ひざ_L_length = ひざ_L.length

        metarig_bones['heel.02.L'].tail = ひざ_L_tail + Vector([+ひざ_L_length / 6, +ひざ_L_length / 8, +0.0])
        metarig_bones['heel.02.L'].head = ひざ_L_tail + Vector([-ひざ_L_length / 6, +ひざ_L_length / 8, +0.0])

        ひざ_R = mmd_bones['ひざ.R']
        ひざ_R_tail = ひざ_R.tail
        ひざ_R_length = ひざ_R.length

        metarig_bones['heel.02.R'].tail = ひざ_R_tail + Vector([-ひざ_R_length / 6, +ひざ_R_length / 8, +0.0])
        metarig_bones['heel.02.R'].head = ひざ_R_tail + Vector([+ひざ_R_length / 6, +ひざ_R_length / 8, +0.0])

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
        人指１_L_head = mmd_bones['人指１.L'].head
        中指１_L_head = mmd_bones['中指１.L'].head
        薬指１_L_head = mmd_bones['薬指１.L'].head
        小指１_L_head = mmd_bones['小指１.L'].head
        metarig_bones['palm.01.L'].head = to_center(人指１_L_head, 手捩_L_tail)
        metarig_bones['palm.02.L'].head = to_center(中指１_L_head, 手捩_L_tail)
        metarig_bones['palm.03.L'].head = to_center(薬指１_L_head, 手捩_L_tail)
        metarig_bones['palm.04.L'].head = to_center(小指１_L_head, 手捩_L_tail)

        手捩_R_tail = mmd_bones['手捩.R'].tail
        人指１_R_head = mmd_bones['人指１.R'].head
        中指１_R_head = mmd_bones['中指１.R'].head
        薬指１_R_head = mmd_bones['薬指１.R'].head
        小指１_R_head = mmd_bones['小指１.R'].head
        metarig_bones['palm.01.R'].head = to_center(人指１_R_head, 手捩_R_tail)
        metarig_bones['palm.02.R'].head = to_center(中指１_R_head, 手捩_R_tail)
        metarig_bones['palm.03.R'].head = to_center(薬指１_R_head, 手捩_R_tail)
        metarig_bones['palm.04.R'].head = to_center(小指１_R_head, 手捩_R_tail)

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

    def execute(self, context):
        mmd_object = context.active_object
        metarig_object = self.create_metarig()
        self.fit_scale(metarig_object, mmd_object)

        mmd_object.select = True
        metarig_object.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        self.fit_bones(metarig_object.data.edit_bones, self.filter_required_mmd_bones(mmd_object.data.edit_bones))

        bpy.ops.object.mode_set(mode='POSE')
        self.pose_bones(metarig_object.pose.bones, self.filter_required_mmd_bones(mmd_object.pose.bones))

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class MMDArmatureIntegrateRigify(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_integrate_rigify'
    bl_label = 'Integrate Rigify Armature and MMD Armatures'
    bl_description = 'Integrate rigify armature and MMD armatures.'
    bl_options = {'REGISTER', 'UNDO'}

    mmd_bone_layer_mapping_0: bpy.props.IntProperty(default=24, min=0, max=31)
    mmd_bone_layer_mapping_8: bpy.props.IntProperty(default=25, min=0, max=31)
    mmd_bone_layer_mapping_9: bpy.props.IntProperty(default=26, min=0, max=31)

    @staticmethod
    def find_targets(selected_objects: Iterable[bpy.types.Object]) -> (bpy.types.Object, bpy.types.Object):
        mmd_tools = import_mmd_tools()

        rigify_object = None
        mmd_object = None

        for obj in selected_objects:
            if 'rig_id' in obj.data:
                rigify_object = obj
                continue

            mmd_root = mmd_tools.core.model.Model.findRoot(obj)
            if mmd_root is not None:
                mmd_object = obj
                continue

        return (rigify_object, mmd_object)

    @classmethod
    def poll(cls, context):
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) != 2:
            return False

        for obj in selected_objects:
            if obj.type != 'ARMATURE':
                return False

            if obj.mode != 'OBJECT':
                return False

        rigify_object, mmd_object = MMDArmatureIntegrateRigify.find_targets(selected_objects)

        if mmd_object is None:
            return False

        if rigify_object is None:
            return False

        return True

    def join_armature(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: bpy.types.Object):
        mmd_armature: bpy.types.Armature = mmd_armature_object.data
        for bone in mmd_armature.bones:
            if bone.layers[0] == True:
                bone.layers[self.mmd_bone_layer_mapping_0] = True
                bone.layers[0] = False

            if bone.layers[8] == True:
                bone.layers[self.mmd_bone_layer_mapping_8] = True
                bone.layers[8] = False

            if bone.layers[9] == True:
                bone.layers[self.mmd_bone_layer_mapping_9] = True
                bone.layers[9] = False

        rigify_armature: bpy.types.Armature = rigify_armature_object.data
        layers = rigify_armature.layers
        rig_id = rigify_armature['rig_id']

        bpy.context.view_layer.objects.active = mmd_armature_object
        bpy.ops.object.join()

        mmd_armature_object.draw_type = 'WIRE'
        mmd_armature_object.show_x_ray = True

        mmd_armature['rig_id'] = rig_id
        mmd_armature.layers = layers

    def change_bone_parent(self, mmd_armature_object: bpy.types.Object):
        mmd_armature: bpy.types.Armature = mmd_armature_object.data
        for mmd_bone in mmd_armature.edit_bones:
            if mmd_bone.name in mmd_rigify_bone_names:
                continue

            if mmd_bone.parent is None:
                continue

            if mmd_bone.parent.name not in mmd_rigify_bone_names:
                continue

            parent_name = mmd_rigify_bone_names[mmd_bone.parent.name]
            mmd_bone.parent = mmd_armature.edit_bones[parent_name]

    def change_bone_constraints(self, mmd_armature_object: bpy.types.Object):
        for mmd_bone in mmd_armature_object.pose.bones:
            for constraint in mmd_bone.constraints:
                if constraint.type != 'CHILD_OF':
                    continue

                if constraint.subtarget not in mmd_rigify_bone_names:
                    continue

                # ボーンコンストレイントの親を変更
                constraint.subtarget = mmd_rigify_bone_names[constraint.subtarget]

                # 逆補正を設定
                pbone = mmd_armature_object.pose.bones[mmd_bone.name]
                context = bpy.context.copy()
                context['constraint'] = constraint
                mmd_armature_object.data.bones.active = pbone.bone
                bpy.ops.constraint.childof_set_inverse(context, constraint=constraint.name, owner='BONE')

    def rename_vertex_groups(self, mmd_mesh_objects: Iterable[bpy.types.Object]):
        for mesh_object in mmd_mesh_objects:
            for vertex_group in mesh_object.vertex_groups:
                if vertex_group.name not in mmd_rigify_bone_names:
                    continue
                vertex_group.name = mmd_rigify_bone_names[vertex_group.name]

    def change_rigidbody_constraints(self, mmd_rigidbody_objects: Iterable[bpy.types.Object]):
        for obj in mmd_rigidbody_objects:
            for constraint in obj.constraints:
                if constraint.type != 'CHILD_OF':
                    continue

                if constraint.subtarget not in mmd_rigify_bone_names:
                    continue

                bpy.context.view_layer.objects.active = obj

                previous_hide_select = obj.hide_select
                previous_hide = obj.hide_get()
                try:
                    obj.hide_select = False
                    obj.hide_set(False)

                    # ボーンコンストレイントの親を変更
                    constraint.subtarget = mmd_rigify_bone_names[constraint.subtarget]

                    # 逆補正を設定
                    context = bpy.context.copy()
                    context['constraint'] = constraint
                    bpy.ops.constraint.childof_set_inverse(context, constraint=constraint.name, owner='OBJECT')

                finally:
                    obj.hide_set(previous_hide)
                    obj.hide_select = previous_hide_select

    def adjust_rigify_settings(self, mmd_armature_object: bpy.types.Object):
        """Imitate the behavior of MMD armature as much as possible."""
        pose_bones = mmd_armature_object.pose.bones

        # disable Arm IK
        pose_bones['upper_arm_parent.L']['IK_FK'] = 1.000
        pose_bones['upper_arm_parent.R']['IK_FK'] = 1.000

        pose_bones['upper_arm_parent.L']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.R']['IK_Stretch'] = 0.000

        # enable Leg IK
        pose_bones['thigh_parent.L']['IK_FK'] = 0.000
        pose_bones['thigh_parent.R']['IK_FK'] = 0.000

        pose_bones['thigh_parent.L']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.R']['IK_Stretch'] = 0.000

        pose_bones['thigh_parent.L']['pole_vector'] = 0  # disable
        pose_bones['thigh_parent.R']['pole_vector'] = 0  # disable

        pose_bones['thigh_parent.L']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.R']['IK_parent'] = 1  # root

        pose_bones['thigh_parent.L']['pole_parent'] = 2  # torso
        pose_bones['thigh_parent.R']['pole_parent'] = 2  # torso

        data_bones = mmd_armature_object.data.bones
        data_bones['spine_fk.001'].use_inherit_rotation = False

    mappp = {
        # '下半身': 'ORG-spine',
        '上半身': 'ORG-spine.001',
        '上半身2': 'ORG-spine.002',
        '首': 'ORG-spine.005',
        '頭': 'ORG-spine.006',

        '足.L': 'ORG-thigh.L',
        '足.R': 'ORG-thigh.R',
        'ひざ.L': 'ORG-shin.L',
        'ひざ.R': 'ORG-shin.R',
        '足首.L': 'ORG-foot.L',
        '足首.R': 'ORG-foot.R',
        '足先EX.L': 'ORG-toe.L',
        '足先EX.R': 'ORG-toe.R',

        '肩.L': 'ORG-shoulder.L',
        '肩.R': 'ORG-shoulder.R',
        '腕.L': 'ORG-upper_arm.L',
        '腕.R': 'ORG-upper_arm.R',
        'ひじ.L': 'ORG-forearm.L',
        'ひじ.R': 'ORG-forearm.R',
        '手首.L': 'ORG-hand.L',
        '手首.R': 'ORG-hand.R',
        '親指０.L': 'ORG-thumb.01.L',
        '親指０.R': 'ORG-thumb.01.R',
        '親指１.L': 'ORG-thumb.02.L',
        '親指１.R': 'ORG-thumb.02.R',
        '親指２.L': 'ORG-thumb.03.L',
        '親指２.R': 'ORG-thumb.03.R',
        '人指０.L': 'ORG-palm.01.L',
        '人指０.R': 'ORG-palm.01.R',
        '人指１.L': 'ORG-f_index.01.L',
        '人指１.R': 'ORG-f_index.01.R',
        '人指２.L': 'ORG-f_index.02.L',
        '人指２.R': 'ORG-f_index.02.R',
        '人指３.L': 'ORG-f_index.03.L',
        '人指３.R': 'ORG-f_index.03.R',
        '中指０.L': 'ORG-palm.02.L',
        '中指０.R': 'ORG-palm.02.R',
        '中指１.L': 'ORG-f_middle.01.L',
        '中指１.R': 'ORG-f_middle.01.R',
        '中指２.L': 'ORG-f_middle.02.L',
        '中指２.R': 'ORG-f_middle.02.R',
        '中指３.L': 'ORG-f_middle.03.L',
        '中指３.R': 'ORG-f_middle.03.R',
        '薬指０.L': 'ORG-palm.03.L',
        '薬指０.R': 'ORG-palm.03.R',
        '薬指１.L': 'ORG-f_ring.01.L',
        '薬指１.R': 'ORG-f_ring.01.R',
        '薬指２.L': 'ORG-f_ring.02.L',
        '薬指２.R': 'ORG-f_ring.02.R',
        '薬指３.L': 'ORG-f_ring.03.L',
        '薬指３.R': 'ORG-f_ring.03.R',
        '小指０.L': 'ORG-palm.04.L',
        '小指０.R': 'ORG-palm.04.R',
        '小指１.L': 'ORG-f_pinky.01.L',
        '小指１.R': 'ORG-f_pinky.01.R',
        '小指２.L': 'ORG-f_pinky.02.L',
        '小指２.R': 'ORG-f_pinky.02.R',
        '小指３.L': 'ORG-f_pinky.03.L',
        '小指３.R': 'ORG-f_pinky.03.R',

    }

    def edit_bone_rotations(self, mmd_armature_object: bpy.types.Object):
        edit_bones: Dict[str, bpy.types.EditBone] = mmd_armature_object.data.edit_bones
        for mmd_name, org_name in self.mappp.items():
            if mmd_name not in edit_bones:
                continue
            edit_bones[mmd_name].roll = edit_bones[org_name].roll

    def setup_bone_constraints(self, mmd_armature_object: bpy.types.Object):
        pose_bones: Dict[str, bpy.types.PoseBone] = mmd_armature_object.pose.bones

        for mmd_name, org_name in self.mappp.items():
            if mmd_name not in pose_bones:
                continue

            mmd_bone = pose_bones[mmd_name]

            for constraint in mmd_bone.constraints:
                if constraint.type not in {'IK'}:
                    continue
                constraint.mute = True

            constraint = mmd_bone.constraints.new('COPY_TRANSFORMS')
            constraint.target = mmd_armature_object
            constraint.subtarget = org_name
            constraint.target_space = 'WORLD'
            constraint.owner_space = 'WORLD'

        # invert spine bone
        mmd_bone = pose_bones['下半身']
        constraint = mmd_bone.constraints.new('COPY_LOCATION')
        constraint.target = mmd_armature_object
        constraint.subtarget = 'ORG-spine.001'
        constraint.target_space = 'WORLD'
        constraint.owner_space = 'WORLD'

        constraint = mmd_bone.constraints.new('COPY_ROTATION')
        constraint.target = mmd_armature_object
        constraint.subtarget = 'ORG-spine'
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.invert_x = False
        constraint.invert_y = True
        constraint.invert_z = True

    def execute(self, context):
        rigify_armature_object, mmd_armature_object = MMDArmatureIntegrateRigify.find_targets(bpy.context.selected_objects)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.join_armature(rigify_armature_object, mmd_armature_object)

        previous_mmd_bone_layer_0 = mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_0]
        previous_mmd_bone_layer_8 = mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_8]
        previous_mmd_bone_layer_9 = mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_9]
        try:
            mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_0] = True
            mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_8] = True
            mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_9] = True

            bpy.ops.object.mode_set(mode='EDIT')
            # self.change_bone_parent(mmd_armature_object)
            self.edit_bone_rotations(mmd_armature_object)

            bpy.ops.object.mode_set(mode='POSE')
            # self.change_bone_constraints(mmd_armature_object)
            self.setup_bone_constraints(mmd_armature_object)
            self.adjust_rigify_settings(mmd_armature_object)

            bpy.ops.object.mode_set(mode='OBJECT')

        finally:
            mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_0] = previous_mmd_bone_layer_0
            mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_8] = previous_mmd_bone_layer_8
            mmd_armature_object.data.layers[self.mmd_bone_layer_mapping_9] = previous_mmd_bone_layer_9

        mmd_tools = import_mmd_tools()
        mmd_root = mmd_tools.core.model.Model.findRoot(mmd_armature_object)
        mmd_model = mmd_tools.core.model.Model(mmd_root)
        # self.rename_vertex_groups(mmd_model.meshes())

        rigify_armature_object.select = False
        mmd_armature_object.select = False

        self.change_rigidbody_constraints(mmd_model.rigidBodies())

        return {'FINISHED'}


class MMDArmatureAssignBoneNames(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_assign_bone_names'
    bl_label = 'Assign MMD Compatible Bone Names'
    bl_description = 'Assign MMD compatible bone names.'
    bl_options = {'REGISTER', 'UNDO'}

    armature_type: bpy.props.EnumProperty(
        items=(
            ('RIGIFY', 'Rigify', 'Rigify Human without face'),
        ),
        name="Armature Type",
        description="choose a armature type",
        default='RIGIFY',
    )

    @classmethod
    def poll(cls, context):
        active_object = bpy.context.active_object

        if active_object is None:
            return False

        if active_object.type != 'ARMATURE':
            return False

        if active_object.mode != 'OBJECT':
            return False

        return True

    def execute(self, context):
        pose_bones = bpy.context.active_object.pose.bones
        pose_bone_mapping = pose_bone_mappings[self.armature_type]

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
