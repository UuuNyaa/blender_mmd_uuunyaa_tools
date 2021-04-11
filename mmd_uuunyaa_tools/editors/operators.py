# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Iterable, List, Set, Tuple, Union

import bpy
import rna_prop_ui
from mathutils import Vector
from mmd_uuunyaa_tools.utilities import import_mmd_tools


class BoneType(Enum):
    STANDARD = '標準'
    PARENT = '全ての親'
    UPPER_ARM_TWIST = '腕捩れ'
    LOWER_ARM_TWIST = '手捩れ'
    UPPER_BODY_2 = '上半身２'
    GROOVE = 'グルーブ'
    WAIST_HIP_CONTROL = '腰'
    LEG_IK_PARENT = '足IK親'
    CONTROL = '操作中心'
    TOE_EX = '足先EX'
    HAND_ACCESSORIES = '手持ちアクセサリ用ダミー'
    SHOULDER_CANCEL = '肩キャンセル'
    THUMB_0 = '親指０'
    OTHERS = 'その他・独自'


class GroupType(Enum):
    NONE = 'none'
    TORSO = 'torso'
    ARM_L = 'arm_l'
    ARM_R = 'arm_R'
    LEG_L = 'leg_l'
    LEG_R = 'leg_R'


class BindType(Enum):
    NONE = 0
    COPY_POSE = 1
    COPY_PARENT = 2
    COPY_LOCAL = 3
    COPY_SPINE = 4
    COPY_TOE = 5


@dataclass
class MMDRigifyBone:

    bone_type: BoneType
    mmd_bone_name: str

    pose_bone_name: str
    bind_bone_name: str

    group_type: GroupType
    bind_type: BindType


mmd_rigify_bones = [
    MMDRigifyBone(BoneType.PARENT, '全ての親', 'root', 'root', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, 'センター', 'center', 'center', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.GROOVE, 'グルーブ', 'groove', 'groove', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, '上半身', 'torso', 'ORG-spine.001', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.UPPER_BODY_2, '上半身2', 'chest', 'ORG-spine.002', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, '首', 'neck', 'ORG-spine.005', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, '頭', 'head', 'ORG-spine.006', GroupType.TORSO, BindType.COPY_PARENT),

    MMDRigifyBone(BoneType.STANDARD, '左肩', 'shoulder.L', 'ORG-shoulder.L', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, '左腕', 'upper_arm_fk.L', 'ORG-upper_arm.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左ひじ', 'forearm_fk.L', 'ORG-forearm.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左手首', 'hand_fk.L', 'ORG-hand.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.THUMB_0, '左親指０', 'thumb.01.L', 'ORG-thumb.01.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左親指１', 'thumb.02.L', 'ORG-thumb.02.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左親指２', 'thumb.03.L', 'ORG-thumb.03.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '左人指０', None, 'ORG-palm.01.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左人指１', 'f_index.01.L', 'ORG-f_index.01.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左人指２', 'f_index.02.L', 'ORG-f_index.02.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左人指３', 'f_index.03.L', 'ORG-f_index.03.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '左中指０', None, 'ORG-palm.02.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左中指１', 'f_middle.01.L', 'ORG-f_middle.01.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左中指２', 'f_middle.02.L', 'ORG-f_middle.02.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左中指３', 'f_middle.03.L', 'ORG-f_middle.03.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '左薬指０', None, 'ORG-palm.03.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左薬指１', 'f_ring.01.L', 'ORG-f_ring.01.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左薬指２', 'f_ring.02.L', 'ORG-f_ring.02.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左薬指３', 'f_ring.03.L', 'ORG-f_ring.03.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '左小指０', None, 'ORG-palm.04.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左小指１', 'f_pinky.01.L', 'ORG-f_pinky.01.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左小指２', 'f_pinky.02.L', 'ORG-f_pinky.02.L', GroupType.ARM_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左小指３', 'f_pinky.03.L', 'ORG-f_pinky.03.L', GroupType.ARM_L, BindType.COPY_LOCAL),


    MMDRigifyBone(BoneType.STANDARD, '右肩', 'shoulder.R', 'ORG-shoulder.R', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, '右腕', 'upper_arm_fk.R', 'ORG-upper_arm.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右ひじ', 'forearm_fk.R', 'ORG-forearm.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右手首', 'hand_fk.R', 'ORG-hand.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.THUMB_0, '右親指０', 'thumb.01.R', 'ORG-thumb.01.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右親指１', 'thumb.02.R', 'ORG-thumb.02.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右親指２', 'thumb.03.R', 'ORG-thumb.03.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '右人指０', None, 'ORG-palm.01.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右人指１', 'f_index.01.R', 'ORG-f_index.01.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右人指２', 'f_index.02.R', 'ORG-f_index.02.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右人指３', 'f_index.03.R', 'ORG-f_index.03.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '右中指０', None, 'ORG-palm.02.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右中指１', 'f_middle.01.R', 'ORG-f_middle.01.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右中指２', 'f_middle.02.R', 'ORG-f_middle.02.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右中指３', 'f_middle.03.R', 'ORG-f_middle.03.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '右薬指０', None, 'ORG-palm.03.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右薬指１', 'f_ring.01.R', 'ORG-f_ring.01.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右薬指２', 'f_ring.02.R', 'ORG-f_ring.02.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右薬指３', 'f_ring.03.R', 'ORG-f_ring.03.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.OTHERS, '右小指０', None, 'ORG-palm.04.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右小指１', 'f_pinky.01.R', 'ORG-f_pinky.01.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右小指２', 'f_pinky.02.R', 'ORG-f_pinky.02.R', GroupType.ARM_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右小指３', 'f_pinky.03.R', 'ORG-f_pinky.03.R', GroupType.ARM_R, BindType.COPY_LOCAL),

    MMDRigifyBone(BoneType.STANDARD, '下半身', 'spine_fk', 'ORG-spine', GroupType.TORSO, BindType.COPY_SPINE),

    MMDRigifyBone(BoneType.STANDARD, '左足', 'thigh_fk.L', 'ORG-thigh.L', GroupType.LEG_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左ひざ', 'shin_fk.L', 'ORG-shin.L', GroupType.LEG_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左足首', 'foot_fk.L', 'ORG-foot.L', GroupType.LEG_L, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '左足ＩＫ', 'foot_ik.L', 'ORG-foot.L', GroupType.LEG_L, BindType.COPY_POSE),
    MMDRigifyBone(BoneType.TOE_EX, '左足先EX', None, 'ORG-toe.L', GroupType.LEG_L, BindType.COPY_TOE),

    MMDRigifyBone(BoneType.STANDARD, '右足', 'thigh_fk.R', 'ORG-thigh.R', GroupType.LEG_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右ひざ', 'shin_fk.R', 'ORG-shin.R', GroupType.LEG_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右足首', 'foot_fk.R', 'ORG-foot.R', GroupType.LEG_R, BindType.COPY_LOCAL),
    MMDRigifyBone(BoneType.STANDARD, '右足ＩＫ', 'foot_ik.R', 'ORG-foot.R', GroupType.LEG_R, BindType.COPY_POSE),
    MMDRigifyBone(BoneType.TOE_EX, '右足先EX', None, 'ORG-toe.R', GroupType.LEG_R, BindType.COPY_TOE),


    MMDRigifyBone(BoneType.STANDARD, '左つま先ＩＫ', 'toe.L', None, GroupType.LEG_L, BindType.NONE),
    MMDRigifyBone(BoneType.STANDARD, '右つま先ＩＫ', 'toe.R', None, GroupType.LEG_R, BindType.NONE),
    MMDRigifyBone(BoneType.STANDARD, '左つま先', None, None, GroupType.LEG_L, BindType.NONE),
    MMDRigifyBone(BoneType.STANDARD, '右つま先', None, None, GroupType.LEG_R, BindType.NONE),


    MMDRigifyBone(BoneType.SHOULDER_CANCEL, '左肩C', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.SHOULDER_CANCEL, '左肩P', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.SHOULDER_CANCEL, '右肩C', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.SHOULDER_CANCEL, '右肩P', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.HAND_ACCESSORIES, '左ダミー', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.HAND_ACCESSORIES, '右ダミー', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.LEG_IK_PARENT, '左足IK親', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.LEG_IK_PARENT, '右足IK親', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.LOWER_ARM_TWIST, '左手捩', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.LOWER_ARM_TWIST, '右手捩', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.UPPER_ARM_TWIST, '左腕捩', None, None, GroupType.NONE, BindType.NONE),
    MMDRigifyBone(BoneType.UPPER_ARM_TWIST, '右腕捩', None, None, GroupType.NONE, BindType.NONE),
]

RigifyArmaturePoseBones = Dict[str, bpy.types.PoseBone]
RigifyArmatureEditBones = Dict[str, bpy.types.EditBone]
MMDArmatureBones = Dict[str, bpy.types.Bone]
MMDArmaturePoseBones = Dict[str, bpy.types.PoseBone]
MMDArmatureEditBones = Dict[str, bpy.types.EditBone]


group_type2prop_names: Dict[GroupType, str] = {
    GroupType.TORSO: 'mmd_rigify_torso_bind_influence',
    GroupType.ARM_L: 'mmd_rigify_arm_l_bind_influence',
    GroupType.ARM_R: 'mmd_rigify_arm_r_bind_influence',
    GroupType.LEG_L: 'mmd_rigify_leg_l_bind_influence',
    GroupType.LEG_R: 'mmd_rigify_leg_r_bind_influence',
}


def add_influence_driver(constraint: bpy.types.Constraint, target, data_path, invert=False):
    driver: bpy.types.Driver = constraint.driver_add('influence').driver
    variable: bpy.types.DriverVariable = driver.variables.new()
    variable.name = 'mmd_rigify_influence'
    variable.targets[0].id = target
    variable.targets[0].data_path = data_path
    driver.expression = ('1-' if invert else '+') + variable.name


def create_binders() -> Dict[BindType, Callable]:

    def copy_pose(mmd_bone, org_armature_object, org_name, influence_data_path):
        constraint = mmd_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_rigify_copy_transforms'
        constraint.target = org_armature_object
        constraint.subtarget = org_name
        constraint.target_space = 'POSE'
        constraint.owner_space = 'POSE'
        add_influence_driver(constraint, org_armature_object, influence_data_path)

    def copy_parent(mmd_bone, org_armature_object, org_name, influence_data_path):
        constraint = mmd_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_rigify_copy_transforms'
        constraint.target = org_armature_object
        constraint.subtarget = org_name
        constraint.target_space = 'LOCAL_WITH_PARENT'
        constraint.owner_space = 'LOCAL_WITH_PARENT'
        add_influence_driver(constraint, org_armature_object, influence_data_path)

    def copy_local(mmd_bone, org_armature_object, org_name, influence_data_path):
        constraint = mmd_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_rigify_copy_transforms'
        constraint.target = org_armature_object
        constraint.subtarget = org_name
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        add_influence_driver(constraint, org_armature_object, influence_data_path)

    def copy_spine(mmd_bone, org_armature_object, org_name, influence_data_path):
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

    def copy_toe(mmd_bone, org_armature_object, org_name, influence_data_path):
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

    return {
        BindType.COPY_POSE: copy_pose,
        BindType.COPY_PARENT: copy_parent,
        BindType.COPY_LOCAL: copy_local,
        BindType.COPY_SPINE: copy_spine,
        BindType.COPY_TOE: copy_toe,
    }


binders: Dict[BindType, Callable] = create_binders()


class MMDArmatureObject:
    mmd_armature_object: bpy.types.Object
    mmd_armature: bpy.types.Armature

    existing_bone_types: Set[BoneType]
    pose_bones: MMDArmaturePoseBones
    mmd_rigify_bones: List[MMDRigifyBone]

    actual_pose_bones: MMDArmaturePoseBones

    def __init__(self, mmd_armature_object: bpy.types.Object):
        self.mmd_armature_object = mmd_armature_object
        mmd_armature: bpy.types.Armature = mmd_armature_object.data
        self.mmd_armature = mmd_armature

        mmd_names: Set[str] = {b.mmd_bone_name for b in mmd_rigify_bones}

        self.pose_bones: MMDArmaturePoseBones = {
            b.mmd_bone.name_j: b
            for b in mmd_armature_object.pose.bones
            if b.mmd_bone.name_j in mmd_names
        }

        self.actual_pose_bones: MMDArmaturePoseBones = {
            b.name: b
            for b in self.pose_bones.values()
        }

        self.mmd_rigify_bones = [
            b
            for b in mmd_rigify_bones
            if b.mmd_bone_name in self.pose_bones
        ]

        self.existing_bone_types: Set[BoneType] = {b.bone_type for b in mmd_rigify_bones}

    def has_bone_type(self, bone_type: BoneType) -> bool:
        return bone_type in self.existing_bone_types

    def to_strict_mmd_bone_name(self, actual_mmd_bone_name: str) -> str:
        return self.actual_pose_bones[actual_mmd_bone_name].mmd_bone.name_j

    def to_actual_mmd_bone_name(self, strict_mmd_bone_name: str) -> str:
        return self.pose_bones[strict_mmd_bone_name].name

    @property
    def bones(self) -> MMDArmatureBones:
        return {
            self.to_strict_mmd_bone_name(b.name): b
            for b in self.mmd_armature.bones
            if b.name in self.actual_pose_bones
        }

    @property
    def edit_bones(self) -> MMDArmatureEditBones:
        return {
            self.to_strict_mmd_bone_name(b.name): b
            for b in self.mmd_armature.edit_bones
            if b.name in self.actual_pose_bones
        }


class MMDRigifyBoneBinder:

    @staticmethod
    def bind():
        pass


"""
MCH-eyes_parent
    eyes
        eye.L
        eye.R
ORG-spine.006
    ORG-face
        master_eye.L
            MCH-eye.L
                ORG-eye.L
            MCH-eye.L.001
        master_eye.R
            MCH-eye.R
                ORG-eye.R
            MCH-eye.R.001
"""


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

    def clean_armature(self, mmd_armature_object: MMDArmatureObject):
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

        mmd_edit_bones = mmd_armature_object.edit_bones

        if_far_then_set(mmd_edit_bones['右親指２'], tail=extend_toward_tail(mmd_edit_bones['右親指１'], 1.8))
        if_far_then_set(mmd_edit_bones['右人指３'], tail=extend_toward_tail(mmd_edit_bones['右人指２'], 1.8))
        if_far_then_set(mmd_edit_bones['右中指３'], tail=extend_toward_tail(mmd_edit_bones['右中指２'], 1.8))
        if_far_then_set(mmd_edit_bones['右薬指３'], tail=extend_toward_tail(mmd_edit_bones['右薬指２'], 1.8))
        if_far_then_set(mmd_edit_bones['右小指３'], tail=extend_toward_tail(mmd_edit_bones['右小指２'], 1.8))
        if_far_then_set(mmd_edit_bones['右手首'], tail=extend_toward_tail(mmd_edit_bones['右ひじ'], 1.3))

        if_far_then_set(mmd_edit_bones['左親指２'], tail=extend_toward_tail(mmd_edit_bones['左親指１'], 1.8))
        if_far_then_set(mmd_edit_bones['左人指３'], tail=extend_toward_tail(mmd_edit_bones['左人指２'], 1.8))
        if_far_then_set(mmd_edit_bones['左中指３'], tail=extend_toward_tail(mmd_edit_bones['左中指２'], 1.8))
        if_far_then_set(mmd_edit_bones['左薬指３'], tail=extend_toward_tail(mmd_edit_bones['左薬指２'], 1.8))
        if_far_then_set(mmd_edit_bones['左小指３'], tail=extend_toward_tail(mmd_edit_bones['左小指２'], 1.8))
        if_far_then_set(mmd_edit_bones['左手首'], tail=extend_toward_tail(mmd_edit_bones['左ひじ'], 1.3))

    def execute(self, context: bpy.types.Context):
        bpy.ops.object.mode_set(mode='EDIT')

        self.clean_armature(MMDArmatureObject(bpy.context.active_object))

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

    def fit_scale(self, metarig_object: bpy.types.Object, mmd_armature_object: MMDArmatureObject):
        rigify_height = metarig_object.data.bones['spine.006'].tail_local[2]
        mmd_height = mmd_armature_object.bones['頭'].tail_local[2]

        scale = mmd_height / rigify_height
        metarig_object.scale = (scale, scale, scale)
        bpy.ops.object.transform_apply(scale=True)

    def fit_bones(self, metarig_bones: bpy.types.ArmatureEditBones, mmd_edit_bones: bpy.types.ArmatureEditBones):
        def to_center(v1: Vector, v2: Vector) -> Vector:
            return (v1 + v2) / 2

        def to_bone_center(bone: bpy.types.EditBone) -> Vector:
            return to_center(bone.head, bone.tail)

        metarig_bones['spine.001'].tail = mmd_edit_bones['上半身'].tail
        metarig_bones['spine.002'].tail = to_bone_center(mmd_edit_bones['上半身2'])
        metarig_bones['spine.003'].tail = mmd_edit_bones['上半身2'].tail
        metarig_bones['spine.004'].tail = to_bone_center(mmd_edit_bones['首'])
        metarig_bones['spine.004'].head = mmd_edit_bones['首'].head
        metarig_bones['spine.005'].tail = mmd_edit_bones['首'].tail
        metarig_bones['spine.006'].tail = mmd_edit_bones['頭'].tail

        metarig_bones['face'].head = mmd_edit_bones['頭'].head
        metarig_bones['face'].tail = to_bone_center(mmd_edit_bones['頭'])

        metarig_bones['shoulder.L'].head = mmd_edit_bones['左肩'].head
        metarig_bones['shoulder.L'].tail = mmd_edit_bones['左肩'].tail
        metarig_bones['shoulder.R'].head = mmd_edit_bones['右肩'].head
        metarig_bones['shoulder.R'].tail = mmd_edit_bones['右肩'].tail
        metarig_bones['upper_arm.L'].head = mmd_edit_bones['左腕'].head
        metarig_bones['upper_arm.R'].head = mmd_edit_bones['右腕'].head
        metarig_bones['forearm.L'].head = mmd_edit_bones['左ひじ'].head
        metarig_bones['forearm.L'].tail = mmd_edit_bones['左手捩'].tail
        metarig_bones['forearm.R'].head = mmd_edit_bones['右ひじ'].head
        metarig_bones['forearm.R'].tail = mmd_edit_bones['右手捩'].tail

        metarig_bones['hand.L'].tail = mmd_edit_bones['左手首'].tail
        metarig_bones['hand.R'].tail = mmd_edit_bones['右手首'].tail
        metarig_bones['thumb.01.L'].head = mmd_edit_bones['左親指０'].head
        metarig_bones['thumb.01.L'].tail = mmd_edit_bones['左親指０'].tail
        metarig_bones['thumb.01.R'].head = mmd_edit_bones['右親指０'].head
        metarig_bones['thumb.01.R'].tail = mmd_edit_bones['右親指０'].tail
        metarig_bones['thumb.02.L'].tail = mmd_edit_bones['左親指１'].tail
        metarig_bones['thumb.02.R'].tail = mmd_edit_bones['右親指１'].tail
        metarig_bones['thumb.03.L'].tail = mmd_edit_bones['左親指２'].tail
        metarig_bones['thumb.03.R'].tail = mmd_edit_bones['右親指２'].tail
        metarig_bones['palm.01.L'].head = to_center(mmd_edit_bones['左人指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_bones['palm.01.L'].tail = mmd_edit_bones['左人指１'].head
        metarig_bones['palm.01.R'].head = to_center(mmd_edit_bones['右人指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_bones['palm.01.R'].tail = mmd_edit_bones['右人指１'].head
        metarig_bones['f_index.01.L'].head = mmd_edit_bones['左人指１'].head
        metarig_bones['f_index.01.L'].tail = mmd_edit_bones['左人指１'].tail
        metarig_bones['f_index.01.R'].head = mmd_edit_bones['右人指１'].head
        metarig_bones['f_index.01.R'].tail = mmd_edit_bones['右人指１'].tail
        metarig_bones['f_index.02.L'].tail = mmd_edit_bones['左人指２'].tail
        metarig_bones['f_index.02.R'].tail = mmd_edit_bones['右人指２'].tail
        metarig_bones['f_index.03.L'].tail = mmd_edit_bones['左人指３'].tail
        metarig_bones['f_index.03.R'].tail = mmd_edit_bones['右人指３'].tail
        metarig_bones['palm.02.L'].head = to_center(mmd_edit_bones['左中指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_bones['palm.02.L'].tail = mmd_edit_bones['左中指１'].head
        metarig_bones['palm.02.R'].head = to_center(mmd_edit_bones['右中指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_bones['palm.02.R'].tail = mmd_edit_bones['右中指１'].head
        metarig_bones['f_middle.01.L'].head = mmd_edit_bones['左中指１'].head
        metarig_bones['f_middle.01.L'].tail = mmd_edit_bones['左中指１'].tail
        metarig_bones['f_middle.01.R'].head = mmd_edit_bones['右中指１'].head
        metarig_bones['f_middle.01.R'].tail = mmd_edit_bones['右中指１'].tail
        metarig_bones['f_middle.02.L'].tail = mmd_edit_bones['左中指２'].tail
        metarig_bones['f_middle.02.R'].tail = mmd_edit_bones['右中指２'].tail
        metarig_bones['f_middle.03.L'].tail = mmd_edit_bones['左中指３'].tail
        metarig_bones['f_middle.03.R'].tail = mmd_edit_bones['右中指３'].tail
        metarig_bones['palm.03.L'].head = to_center(mmd_edit_bones['左薬指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_bones['palm.03.L'].tail = mmd_edit_bones['左薬指１'].head
        metarig_bones['palm.03.R'].head = to_center(mmd_edit_bones['右薬指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_bones['palm.03.R'].tail = mmd_edit_bones['右薬指１'].head
        metarig_bones['f_ring.01.L'].head = mmd_edit_bones['左薬指１'].head
        metarig_bones['f_ring.01.L'].tail = mmd_edit_bones['左薬指１'].tail
        metarig_bones['f_ring.01.R'].head = mmd_edit_bones['右薬指１'].head
        metarig_bones['f_ring.01.R'].tail = mmd_edit_bones['右薬指１'].tail
        metarig_bones['f_ring.02.L'].tail = mmd_edit_bones['左薬指２'].tail
        metarig_bones['f_ring.02.R'].tail = mmd_edit_bones['右薬指２'].tail
        metarig_bones['f_ring.03.L'].tail = mmd_edit_bones['左薬指３'].tail
        metarig_bones['f_ring.03.R'].tail = mmd_edit_bones['右薬指３'].tail
        metarig_bones['palm.04.L'].head = to_center(mmd_edit_bones['左小指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_bones['palm.04.L'].tail = mmd_edit_bones['左小指１'].head
        metarig_bones['palm.04.R'].head = to_center(mmd_edit_bones['右小指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_bones['palm.04.R'].tail = mmd_edit_bones['右小指１'].head
        metarig_bones['f_pinky.01.L'].head = mmd_edit_bones['左小指１'].head
        metarig_bones['f_pinky.01.L'].tail = mmd_edit_bones['左小指１'].tail
        metarig_bones['f_pinky.01.R'].head = mmd_edit_bones['右小指１'].head
        metarig_bones['f_pinky.01.R'].tail = mmd_edit_bones['右小指１'].tail
        metarig_bones['f_pinky.02.L'].tail = mmd_edit_bones['左小指２'].tail
        metarig_bones['f_pinky.02.R'].tail = mmd_edit_bones['右小指２'].tail
        metarig_bones['f_pinky.03.L'].tail = mmd_edit_bones['左小指３'].tail
        metarig_bones['f_pinky.03.R'].tail = mmd_edit_bones['右小指３'].tail

        metarig_bones['spine'].head = mmd_edit_bones['下半身'].tail
        metarig_bones['spine'].tail = mmd_edit_bones['下半身'].head
        metarig_bones['pelvis.L'].head = mmd_edit_bones['下半身'].tail
        metarig_bones['pelvis.R'].head = mmd_edit_bones['下半身'].tail
        metarig_bones['pelvis.L'].tail[1:3] = [mmd_edit_bones['下半身'].tail[1]-metarig_bones['spine'].length/2, mmd_edit_bones['下半身'].head[2]]
        metarig_bones['pelvis.R'].tail[1:3] = [mmd_edit_bones['下半身'].tail[1]-metarig_bones['spine'].length/2, mmd_edit_bones['下半身'].head[2]]

        metarig_bones['thigh.L'].head = mmd_edit_bones['左足'].head
        metarig_bones['thigh.L'].tail = mmd_edit_bones['左足'].tail
        metarig_bones['thigh.R'].head = mmd_edit_bones['右足'].head
        metarig_bones['thigh.R'].tail = mmd_edit_bones['右足'].tail
        metarig_bones['shin.L'].tail = mmd_edit_bones['左ひざ'].tail
        metarig_bones['shin.R'].tail = mmd_edit_bones['右ひざ'].tail
        metarig_bones['foot.L'].tail = mmd_edit_bones['左足首'].tail
        metarig_bones['foot.R'].tail = mmd_edit_bones['右足首'].tail
        metarig_bones['heel.02.L'].tail = mmd_edit_bones['左ひざ'].tail + Vector([+mmd_edit_bones['左ひざ'].length / 6, +mmd_edit_bones['左ひざ'].length / 8, +0.0])
        metarig_bones['heel.02.L'].head = mmd_edit_bones['左ひざ'].tail + Vector([-mmd_edit_bones['左ひざ'].length / 6, +mmd_edit_bones['左ひざ'].length / 8, +0.0])
        metarig_bones['heel.02.R'].tail = mmd_edit_bones['右ひざ'].tail + Vector([-mmd_edit_bones['右ひざ'].length / 6, +mmd_edit_bones['右ひざ'].length / 8, +0.0])
        metarig_bones['heel.02.R'].head = mmd_edit_bones['右ひざ'].tail + Vector([+mmd_edit_bones['右ひざ'].length / 6, +mmd_edit_bones['右ひざ'].length / 8, +0.0])
        metarig_bones['toe.L'].tail = mmd_edit_bones['左足首'].tail + Vector([+0.0, -mmd_edit_bones['左足首'].length / 2, +0.0])
        metarig_bones['toe.R'].tail = mmd_edit_bones['右足首'].tail + Vector([+0.0, -mmd_edit_bones['右足首'].length / 2, +0.0])

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

        # remove unused mmd_edit_bones
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
        metarig_bones['thumb.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['thumb.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['thumb.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_index.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_index.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_index.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_index.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_middle.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_middle.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_middle.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_middle.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_ring.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_ring.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_ring.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_ring.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_pinky.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_pinky.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_bones['f_pinky.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_bones['f_pinky.01.R'].rigify_parameters.make_extra_ik_control = True

        # fix straight arm IK problem
        # limbs.super_limb
        metarig_bones['upper_arm.L'].rigify_parameters.rotation_axis = 'x'
        metarig_bones['upper_arm.R'].rigify_parameters.rotation_axis = 'x'

    def execute(self, context: bpy.types.Context):
        mmd_object = context.active_object
        metarig_object = self.create_metarig_object()

        mmd_armature = MMDArmatureObject(mmd_object)
        self.fit_scale(metarig_object, mmd_armature)

        mmd_object.select = True
        metarig_object.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        self.fit_bones(metarig_object.data.edit_bones, mmd_armature.edit_bones)

        bpy.ops.object.mode_set(mode='POSE')
        self.pose_bones(metarig_object.pose.bones, mmd_armature.pose_bones)

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


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
            if obj.type != 'ARMATURE':
                continue

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

    def edit_bones(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: MMDArmatureObject):
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones
        mmd_edit_bones: MMDArmatureEditBones = mmd_armature_object.edit_bones

        center_bone = rig_edit_bones.new('center')
        center_bone.layers = [i in {4} for i in range(32)]
        center_bone.head = mmd_edit_bones['センター'].head
        center_bone.tail = mmd_edit_bones['センター'].tail

        groove_bone = rig_edit_bones.new('groove')
        groove_bone.layers = [i in {4} for i in range(32)]
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

        rigify_armature_object.show_in_front = True

        pose_bones = rigify_armature_object.pose.bones

        pose_bones["upper_arm_parent.L"]["IK_FK"] = 0.000
        pose_bones["upper_arm_parent.R"]["IK_FK"] = 0.000
        pose_bones['upper_arm_parent.L']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.R']['IK_Stretch'] = 0.000

        pose_bones['thigh_parent.L']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.R']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.L']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.R']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.L']['pole_parent'] = 2  # torso
        pose_bones['thigh_parent.R']['pole_parent'] = 2  # torso

        # torso hack
        pose_bones["torso"]["neck_follow"] = 1.000  # follow chest
        pose_bones["torso"]["head_follow"] = 1.000  # follow chest

        # 上半身２
        pose_bones["MCH-spine.003"].constraints['Copy Transforms'].influence = 0.000
        pose_bones["MCH-spine.002"].constraints['Copy Transforms'].influence = 1.000

        bones: bpy.types.ArmatureBones = rigify_armature_object.data.bones

        # 上半身
        bones["tweak_spine.001"].use_inherit_rotation = True

        # 下半身
        bones["spine_fk"].use_inherit_rotation = False

    def fit_bone_rotations(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: MMDArmatureObject):
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones
        mmd_edit_bones: MMDArmatureEditBones = mmd_armature_object.edit_bones

        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            if mmd_rigify_bone.bind_bone_name is None:
                continue

            mmd_edit_bones[mmd_rigify_bone.mmd_bone_name].roll = rig_edit_bones[mmd_rigify_bone.bind_bone_name].roll

    def pose_bone_constraints(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: MMDArmatureObject):
        rig_pose_bones: Dict[str, bpy.types.PoseBone] = rigify_armature_object.pose.bones
        rig_bone_groups = rigify_armature_object.pose.bone_groups

        rig_pose_bones['center'].bone_group = rig_bone_groups['Tweak']
        rig_pose_bones['groove'].bone_group = rig_bone_groups['Tweak']

        torso_pose_bone = rig_pose_bones['torso']
        for influence_prop_name in group_type2prop_names.values():
            rna_prop_ui.rna_idprop_ui_create(
                torso_pose_bone,
                influence_prop_name,
                default=1.000,
                min=0.000, max=1.000,
                soft_min=None, soft_max=None,
                description=None,
                overridable=True,
                subtype=None
            )

        mmd_pose_bones: MMDArmaturePoseBones = mmd_armature_object.pose_bones

        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            if mmd_rigify_bone.bind_type == BindType.NONE:
                continue

            mmd_pose_bone = mmd_pose_bones[mmd_rigify_bone.mmd_bone_name]
            prop_data_path = f'pose.bones["torso"]["{group_type2prop_names[mmd_rigify_bone.group_type]}"]'

            for constraint in mmd_pose_bone.constraints:
                if constraint.name.startswith('mmd_rigify_'):
                    mmd_pose_bone.constraints.remove(constraint)

                elif constraint.name == 'IK' and constraint.type == 'IK':
                    add_influence_driver(constraint, rigify_armature_object, prop_data_path, invert=True)

            binders[mmd_rigify_bone.bind_type](
                mmd_pose_bone,
                rigify_armature_object,
                mmd_rigify_bone.bind_bone_name,
                prop_data_path
            )

    def assign_mmd_bone_names(self, rigify_armature_object: bpy.types.Object):
        pose_bones = rigify_armature_object.pose.bones

        mmd_name2rigify_names = {b.mmd_bone_name: b.pose_bone_name for b in mmd_rigify_bones}

        # clear mmd pose bone names
        for pose_bone in pose_bones:
            if pose_bone.mmd_bone.name_j not in mmd_name2rigify_names:
                continue

            pose_bone.mmd_bone.name_j = ''

        for mmd_bone_name, pose_bone_name in mmd_name2rigify_names.items():
            if pose_bone_name is None:
                continue

            pose_bones[pose_bone_name].mmd_bone.name_j = mmd_bone_name

    def change_mmd_bone_layer(self, mmd_armature_object: MMDArmatureObject):
        mmd_bones = mmd_armature_object.bones
        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            mmd_bones[mmd_rigify_bone.mmd_bone_name].layers[23] = True

    def set_view_layers(self, rigify_armature_object: bpy.types.Object):
        rig_armature: bpy.types.Armature = rigify_armature_object.data
        rig_armature.layers = [i in {3, 5, 7, 10, 13, 16, 28} for i in range(32)]

    def execute(self, context: bpy.types.Context):
        rigify_armature_object, mmd_armature_object = self.find_armature_objects(bpy.context.selected_objects)
        mmd_armature_object = MMDArmatureObject(mmd_armature_object)

        bpy.ops.object.mode_set(mode='EDIT')
        self.edit_bones(rigify_armature_object, mmd_armature_object)
        self.fit_bone_rotations(rigify_armature_object, mmd_armature_object)

        bpy.ops.object.mode_set(mode='POSE')
        self.imitate_mmd_behavior(rigify_armature_object)
        self.assign_mmd_bone_names(rigify_armature_object)
        self.pose_bone_constraints(rigify_armature_object, mmd_armature_object)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.change_mmd_bone_layer(mmd_armature_object)
        self.set_view_layers(rigify_armature_object)

        return {'FINISHED'}


class OperatorPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_mmd_rigify'
    bl_label = 'UuuNyaa MMD Rigify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_context = ''

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False

        return context.object.type == 'ARMATURE' and context.active_object.data.get('rig_id') is not None

    def draw(self, context: bpy.types.Context):
        torso_pose_bone = bpy.context.active_object.pose.bones['torso']
        if group_type2prop_names[GroupType.TORSO] not in torso_pose_bone:
            return

        layout = self.layout
        col = layout.column()
        col.label(text='Influences:')
        row = col.row()
        row.prop(torso_pose_bone, f'["{group_type2prop_names[GroupType.TORSO]}"]', text='Torso', slider=True)

        row = col.row()
        row.prop(torso_pose_bone, f'["{group_type2prop_names[GroupType.ARM_L]}"]', text='Arm.L', slider=True)
        row.prop(torso_pose_bone, f'["{group_type2prop_names[GroupType.ARM_R]}"]', text='Arm.R', slider=True)
        row = col.row()
        row.prop(torso_pose_bone, f'["{group_type2prop_names[GroupType.LEG_L]}"]', text='Leg.L', slider=True)
        row.prop(torso_pose_bone, f'["{group_type2prop_names[GroupType.LEG_R]}"]', text='Leg.R', slider=True)


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
