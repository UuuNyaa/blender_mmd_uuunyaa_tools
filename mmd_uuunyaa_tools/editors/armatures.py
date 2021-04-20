# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Set, Union

import bpy
import rna_prop_ui
from mathutils import Euler, Matrix, Vector
from mmd_uuunyaa_tools.utilities import import_mmd_tools

RigifyArmatureBones = Dict[str, bpy.types.Bone]
RigifyArmaturePoseBones = Dict[str, bpy.types.PoseBone]
RigifyArmatureEditBones = Dict[str, bpy.types.EditBone]

MMDArmatureBones = Dict[str, bpy.types.Bone]
MMDArmaturePoseBones = Dict[str, bpy.types.PoseBone]
MMDArmatureEditBones = Dict[str, bpy.types.EditBone]


class MMDBindType(Enum):
    NONE = 0
    COPY_POSE = 1
    COPY_PARENT = 2
    COPY_LOCAL = 3
    COPY_SPINE = 4
    COPY_TOE = 5
    COPY_EYE = 6


class MMDBoneType(Enum):
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
    FACE = 'face'
    TORSO = 'torso'
    ARM_L = 'arm_l'
    ARM_R = 'arm_R'
    LEG_L = 'leg_l'
    LEG_R = 'leg_R'


@dataclass
class MMDRigifyBone:

    bone_type: MMDBoneType
    mmd_bone_name: str

    pose_bone_name: str
    bind_bone_name: str

    group_type: GroupType
    bind_type: MMDBindType


mmd_rigify_bones = [
    MMDRigifyBone(MMDBoneType.PARENT, '全ての親', 'root', 'root', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDRigifyBone(MMDBoneType.STANDARD, 'センター', 'center', 'center', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDRigifyBone(MMDBoneType.GROOVE, 'グルーブ', 'groove', 'groove', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDRigifyBone(MMDBoneType.STANDARD, '上半身', 'torso', 'ORG-spine.001', GroupType.TORSO, MMDBindType.COPY_POSE),
    MMDRigifyBone(MMDBoneType.UPPER_BODY_2, '上半身2', 'chest', 'ORG-spine.002', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDRigifyBone(MMDBoneType.STANDARD, '首', 'neck', 'ORG-spine.005', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDRigifyBone(MMDBoneType.STANDARD, '頭', 'head', 'ORG-spine.006', GroupType.TORSO, MMDBindType.COPY_PARENT),

    MMDRigifyBone(MMDBoneType.STANDARD, '両目', 'mmd_rigify_eyes_fk', 'mmd_rigify_eyes_fk', GroupType.FACE, MMDBindType.COPY_EYE),
    MMDRigifyBone(MMDBoneType.STANDARD, '左目', 'mmd_rigify_eye_fk.L', 'MCH-eye.L', GroupType.FACE, MMDBindType.COPY_EYE),
    MMDRigifyBone(MMDBoneType.STANDARD, '右目', 'mmd_rigify_eye_fk.R', 'MCH-eye.R', GroupType.FACE, MMDBindType.COPY_EYE),

    MMDRigifyBone(MMDBoneType.STANDARD, '左肩', 'shoulder.L', 'ORG-shoulder.L', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDRigifyBone(MMDBoneType.STANDARD, '左腕', 'upper_arm_fk.L', 'ORG-upper_arm.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左ひじ', 'forearm_fk.L', 'ORG-forearm.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左手首', 'hand_fk.L', 'ORG-hand.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.THUMB_0, '左親指０', 'thumb.01.L', 'ORG-thumb.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左親指１', 'thumb.02.L', 'ORG-thumb.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左親指２', 'thumb.03.L', 'ORG-thumb.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '左人指０', None, 'ORG-palm.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左人指１', 'f_index.01.L', 'ORG-f_index.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左人指２', 'f_index.02.L', 'ORG-f_index.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左人指３', 'f_index.03.L', 'ORG-f_index.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '左中指０', None, 'ORG-palm.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左中指１', 'f_middle.01.L', 'ORG-f_middle.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左中指２', 'f_middle.02.L', 'ORG-f_middle.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左中指３', 'f_middle.03.L', 'ORG-f_middle.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '左薬指０', None, 'ORG-palm.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左薬指１', 'f_ring.01.L', 'ORG-f_ring.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左薬指２', 'f_ring.02.L', 'ORG-f_ring.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左薬指３', 'f_ring.03.L', 'ORG-f_ring.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '左小指０', None, 'ORG-palm.04.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左小指１', 'f_pinky.01.L', 'ORG-f_pinky.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左小指２', 'f_pinky.02.L', 'ORG-f_pinky.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左小指３', 'f_pinky.03.L', 'ORG-f_pinky.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),

    MMDRigifyBone(MMDBoneType.STANDARD, '右肩', 'shoulder.R', 'ORG-shoulder.R', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDRigifyBone(MMDBoneType.STANDARD, '右腕', 'upper_arm_fk.R', 'ORG-upper_arm.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右ひじ', 'forearm_fk.R', 'ORG-forearm.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右手首', 'hand_fk.R', 'ORG-hand.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.THUMB_0, '右親指０', 'thumb.01.R', 'ORG-thumb.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右親指１', 'thumb.02.R', 'ORG-thumb.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右親指２', 'thumb.03.R', 'ORG-thumb.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '右人指０', None, 'ORG-palm.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右人指１', 'f_index.01.R', 'ORG-f_index.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右人指２', 'f_index.02.R', 'ORG-f_index.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右人指３', 'f_index.03.R', 'ORG-f_index.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '右中指０', None, 'ORG-palm.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右中指１', 'f_middle.01.R', 'ORG-f_middle.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右中指２', 'f_middle.02.R', 'ORG-f_middle.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右中指３', 'f_middle.03.R', 'ORG-f_middle.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '右薬指０', None, 'ORG-palm.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右薬指１', 'f_ring.01.R', 'ORG-f_ring.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右薬指２', 'f_ring.02.R', 'ORG-f_ring.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右薬指３', 'f_ring.03.R', 'ORG-f_ring.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.OTHERS, '右小指０', None, 'ORG-palm.04.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右小指１', 'f_pinky.01.R', 'ORG-f_pinky.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右小指２', 'f_pinky.02.R', 'ORG-f_pinky.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右小指３', 'f_pinky.03.R', 'ORG-f_pinky.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),

    MMDRigifyBone(MMDBoneType.STANDARD, '下半身', 'spine_fk', 'ORG-spine', GroupType.TORSO, MMDBindType.COPY_SPINE),

    MMDRigifyBone(MMDBoneType.STANDARD, '左足', 'thigh_fk.L', 'ORG-thigh.L', GroupType.LEG_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左ひざ', 'shin_fk.L', 'ORG-shin.L', GroupType.LEG_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左足首', 'foot_fk.L', 'ORG-foot.L', GroupType.LEG_L, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '左足ＩＫ', 'foot_ik.L', 'ORG-foot.L', GroupType.LEG_L, MMDBindType.COPY_POSE),
    MMDRigifyBone(MMDBoneType.TOE_EX, '左足先EX', None, 'ORG-toe.L', GroupType.LEG_L, MMDBindType.COPY_TOE),

    MMDRigifyBone(MMDBoneType.STANDARD, '右足', 'thigh_fk.R', 'ORG-thigh.R', GroupType.LEG_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右ひざ', 'shin_fk.R', 'ORG-shin.R', GroupType.LEG_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右足首', 'foot_fk.R', 'ORG-foot.R', GroupType.LEG_R, MMDBindType.COPY_LOCAL),
    MMDRigifyBone(MMDBoneType.STANDARD, '右足ＩＫ', 'foot_ik.R', 'ORG-foot.R', GroupType.LEG_R, MMDBindType.COPY_POSE),
    MMDRigifyBone(MMDBoneType.TOE_EX, '右足先EX', None, 'ORG-toe.R', GroupType.LEG_R, MMDBindType.COPY_TOE),

    MMDRigifyBone(MMDBoneType.STANDARD, '左つま先ＩＫ', 'toe.L', None, GroupType.LEG_L, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.STANDARD, '右つま先ＩＫ', 'toe.R', None, GroupType.LEG_R, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.STANDARD, '左つま先', None, None, GroupType.LEG_L, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.STANDARD, '右つま先', None, None, GroupType.LEG_R, MMDBindType.NONE),

    MMDRigifyBone(MMDBoneType.SHOULDER_CANCEL, '左肩C', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.SHOULDER_CANCEL, '左肩P', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.SHOULDER_CANCEL, '右肩C', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.SHOULDER_CANCEL, '右肩P', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.HAND_ACCESSORIES, '左ダミー', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.HAND_ACCESSORIES, '右ダミー', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.LEG_IK_PARENT, '左足IK親', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.LEG_IK_PARENT, '右足IK親', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.LOWER_ARM_TWIST, '左手捩', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.LOWER_ARM_TWIST, '右手捩', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.UPPER_ARM_TWIST, '左腕捩', None, None, GroupType.NONE, MMDBindType.NONE),
    MMDRigifyBone(MMDBoneType.UPPER_ARM_TWIST, '右腕捩', None, None, GroupType.NONE, MMDBindType.NONE),
]


def add_influence_driver(constraint: bpy.types.Constraint, target: bpy.types.Object, data_path: str, invert=False):
    driver: bpy.types.Driver = constraint.driver_add('influence').driver
    variable: bpy.types.DriverVariable = driver.variables.new()
    variable.name = 'mmd_rigify_influence'
    variable.targets[0].id = target
    variable.targets[0].data_path = data_path
    driver.expression = ('1-' if invert else '+') + variable.name


def create_binders() -> Dict[MMDBindType, Callable]:

    def copy_pose(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_rigify_copy_transforms'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'POSE'
        constraint.owner_space = 'POSE'
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_parent(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_rigify_copy_transforms'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL_WITH_PARENT'
        constraint.owner_space = 'LOCAL_WITH_PARENT'
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_local(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_rigify_copy_transforms'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_spine(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_LOCATION')
        constraint.name = 'mmd_rigify_copy_location'
        constraint.target = target_object
        constraint.subtarget = 'spine_fk'
        constraint.target_space = 'POSE'
        constraint.owner_space = 'POSE'
        add_influence_driver(constraint, target_object, influence_data_path)

        constraint = pose_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_rigify_copy_rotation'
        constraint.target = target_object
        constraint.subtarget = 'ORG-spine'
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.invert_x = False
        constraint.invert_y = True
        constraint.invert_z = True
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_toe(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_LOCATION')
        constraint.name = 'mmd_rigify_copy_location'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        add_influence_driver(constraint, target_object, influence_data_path)

        constraint = pose_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_rigify_copy_rotation'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.invert_x = True
        constraint.invert_y = False
        constraint.invert_z = False
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_eye(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_rigify_copy_rotation'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        add_influence_driver(constraint, target_object, influence_data_path)

    return {
        MMDBindType.COPY_POSE: copy_pose,
        MMDBindType.COPY_PARENT: copy_parent,
        MMDBindType.COPY_LOCAL: copy_local,
        MMDBindType.COPY_SPINE: copy_spine,
        MMDBindType.COPY_TOE: copy_toe,
        MMDBindType.COPY_EYE: copy_eye,
    }


binders: Dict[MMDBindType, Callable] = create_binders()


class MMDArmatureObject:
    raw_object: bpy.types.Object
    raw_armature: bpy.types.Armature

    existing_bone_types: Set[MMDBoneType]
    pose_bones: MMDArmaturePoseBones
    mmd_rigify_bones: List[MMDRigifyBone]

    actual_pose_bones: MMDArmaturePoseBones

    @staticmethod
    def is_mmd_armature_object(obj: bpy.types.Object):
        if obj is None:
            return False

        if obj.type != 'ARMATURE':
            return False

        if import_mmd_tools().core.model.Model.findRoot(obj) is None:
            return False

        return True

    def __init__(self, mmd_armature_object: bpy.types.Object):
        self.raw_object = mmd_armature_object
        self.raw_armature: bpy.types.Armature = self.raw_object.data

        mmd_names: Set[str] = {b.mmd_bone_name for b in mmd_rigify_bones}

        self.pose_bones: MMDArmaturePoseBones = {
            b.mmd_bone.name_j: b
            for b in self.raw_object.pose.bones
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

        self.existing_bone_types: Set[MMDBoneType] = {b.bone_type for b in self.mmd_rigify_bones}

    def has_bone_type(self, bone_type: MMDBoneType) -> bool:
        return bone_type in self.existing_bone_types

    def to_strict_mmd_bone_name(self, actual_mmd_bone_name: str) -> str:
        return self.actual_pose_bones[actual_mmd_bone_name].mmd_bone.name_j

    def to_actual_mmd_bone_name(self, strict_mmd_bone_name: str) -> str:
        return self.pose_bones[strict_mmd_bone_name].name

    @property
    def bones(self) -> MMDArmatureBones:
        return {
            self.to_strict_mmd_bone_name(b.name): b
            for b in self.raw_armature.bones
            if b.name in self.actual_pose_bones
        }

    @property
    def edit_bones(self) -> MMDArmatureEditBones:
        return {
            self.to_strict_mmd_bone_name(b.name): b
            for b in self.raw_armature.edit_bones
            if b.name in self.actual_pose_bones
        }

    def clean_armature_fingers(self):
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

        mmd_edit_bones = self.edit_bones

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

    def clean_armature_spine(self):
        mmd_edit_bones = self.edit_bones

        # spine chain
        mmd_edit_bones['上半身'].tail = mmd_edit_bones['上半身2'].head
        mmd_edit_bones['上半身2'].tail = mmd_edit_bones['首'].head
        mmd_edit_bones['首'].tail = mmd_edit_bones['頭'].head


group_type2prop_names: Dict[GroupType, str] = {
    GroupType.FACE: 'mmd_rigify_face_bind_influence',
    GroupType.TORSO: 'mmd_rigify_torso_bind_influence',
    GroupType.ARM_L: 'mmd_rigify_arm_l_bind_influence',
    GroupType.ARM_R: 'mmd_rigify_arm_r_bind_influence',
    GroupType.LEG_L: 'mmd_rigify_leg_l_bind_influence',
    GroupType.LEG_R: 'mmd_rigify_leg_r_bind_influence',
}


@dataclass
class DataPath:
    bone_name: str
    prop_name: str


class ControlType(Enum):
    TORSO_NECK_FOLLOW = 'torso_neck_follow'
    TORSO_HEAD_FOLLOW = 'torso_head_follow'
    EYE_MMD_RIGIFY = 'eye_mmd_rigify'
    ARM_L_IK_FK = 'arm_l_ik_fk'
    ARM_R_IK_FK = 'arm_r_ik_fk'
    ARM_L_IK_STRETCH = 'arm_l_ik_stretch'
    ARM_R_IK_STRETCH = 'arm_r_ik_stretch'
    ARM_L_IK_PARENT = 'arm_l_ik_parent'
    ARM_R_IK_PARENT = 'arm_r_ik_parent'
    ARM_L_POLE_VECTOR = 'arm_l_pole_vector'
    ARM_R_POLE_VECTOR = 'arm_r_pole_vector'
    LEG_L_IK_FK = 'leg_l_ik_fk'
    LEG_R_IK_FK = 'leg_r_ik_fk'
    LEG_L_IK_STRETCH = 'leg_l_ik_stretch'
    LEG_R_IK_STRETCH = 'leg_r_ik_stretch'
    LEG_L_IK_PARENT = 'leg_l_ik_parent'
    LEG_R_IK_PARENT = 'leg_r_ik_parent'
    LEG_L_POLE_VECTOR = 'leg_l_pole_vector'
    LEG_R_POLE_VECTOR = 'leg_r_pole_vector'
    LEG_L_POLE_PARENT = 'leg_l_pole_parent'
    LEG_R_POLE_PARENT = 'leg_r_pole_parent'


class RigifyArmatureObject:
    raw_object: bpy.types.Object
    raw_armature: bpy.types.Armature
    datapaths: Dict[str, DataPath]

    pose_bones: RigifyArmaturePoseBones

    prop_storage_bone_name: str = 'torso'

    @staticmethod
    def is_rigify_armature_object(obj: bpy.types.Object):
        if obj is None:
            return False

        if obj.type != 'ARMATURE':
            return False

        if 'rig_id' not in obj.data:
            return False

        return True

    def __init__(self, rigify_armature_object: bpy.types.Object):
        self.raw_object = rigify_armature_object
        self.raw_armature: bpy.types.Armature = self.raw_object.data

        self.pose_bones: RigifyArmaturePoseBones = self.raw_object.pose.bones

        def to_bone_suffix(bone_name: str) -> Union[str, None]:
            match = re.search(r'[_\.]([lLrR])$', bone_name)
            if not match:
                return None

            raw_suffix = match.group(1)
            if raw_suffix in {'l', 'L'}:
                return 'L'
            else:
                return 'R'

        control_types = {
            (True, False, 'L', 'IK_FK'): ControlType.ARM_L_IK_FK,
            (True, False, 'R', 'IK_FK'): ControlType.ARM_R_IK_FK,
            (True, False, 'L', 'IK_Strertch'): ControlType.ARM_L_IK_STRETCH,
            (True, False, 'R', 'IK_Strertch'): ControlType.ARM_R_IK_STRETCH,
            (True, False, 'L', 'IK_parent'): ControlType.ARM_L_IK_PARENT,
            (True, False, 'R', 'IK_parent'): ControlType.ARM_R_IK_PARENT,
            (True, False, 'L', 'pole_vector'): ControlType.ARM_L_POLE_VECTOR,
            (True, False, 'R', 'pole_vector'): ControlType.ARM_R_POLE_VECTOR,
            (False, True, 'L', 'IK_FK'): ControlType.LEG_L_IK_FK,
            (False, True, 'R', 'IK_FK'): ControlType.LEG_R_IK_FK,
            (False, True, 'L', 'IK_Strertch'): ControlType.LEG_L_IK_STRETCH,
            (False, True, 'R', 'IK_Strertch'): ControlType.LEG_R_IK_STRETCH,
            (False, True, 'L', 'IK_parent'): ControlType.LEG_L_IK_PARENT,
            (False, True, 'R', 'IK_parent'): ControlType.LEG_R_IK_PARENT,
            (False, True, 'L', 'pole_vector'): ControlType.LEG_L_POLE_VECTOR,
            (False, True, 'R', 'pole_vector'): ControlType.LEG_R_POLE_VECTOR,
            (False, True, 'L', 'pole_parent'): ControlType.LEG_L_POLE_PARENT,
            (False, True, 'R', 'pole_parent'): ControlType.LEG_R_POLE_PARENT,
        }

        datapaths: Dict[ControlType, DataPath] = {
            ControlType.TORSO_NECK_FOLLOW: DataPath('torso', 'neck_follow'),
            ControlType.TORSO_HEAD_FOLLOW: DataPath('torso', 'head_follow'),
            ControlType.EYE_MMD_RIGIFY: DataPath('torso', 'mmd_rigify_eye_mmd_rigify'),
        }

        for pose_bone in self.pose_bones:
            bone_name = pose_bone.name

            is_arm_bone_name = 'upper_arm_parent' in bone_name
            is_leg_bone_name = 'thigh_parent' in bone_name
            bone_suffix = to_bone_suffix(bone_name)

            for key in pose_bone.keys():
                if key in {'IK_FK', 'IK/FK'}:
                    prop_name = 'IK_FK'
                elif key in {'IK_Strertch', 'IK_parent', 'pole_vector', 'pole_parent'}:
                    prop_name = key
                else:
                    continue

                control_type = control_types.get((is_arm_bone_name, is_leg_bone_name, bone_suffix, prop_name))
                if control_type is None:
                    continue

                datapaths[control_type] = DataPath(bone_name, key)

        self.datapaths = datapaths

    @property
    def bones(self) -> RigifyArmatureBones:
        return self.raw_armature.bones

    @property
    def pose_bone_groups(self) -> bpy.types.BoneGroups:
        return self.raw_object.pose.bone_groups

    @property
    def edit_bones(self) -> RigifyArmatureEditBones:
        return self.raw_armature.edit_bones

    def _get_property(self, control_type: ControlType):
        datapath = self.datapaths.get(control_type)
        if datapath is None:
            return None
        return self.pose_bones[datapath.bone_name][datapath.prop_name]

    def _set_property(self, control_type: ControlType, value):
        datapath = self.datapaths.get(control_type)
        if datapath is None:
            return
        self.pose_bones[datapath.bone_name][datapath.prop_name] = value

    @property
    def torso_neck_follow(self):
        return self._get_property(ControlType.TORSO_NECK_FOLLOW)

    @torso_neck_follow.setter
    def torso_neck_follow(self, value):
        self._set_property(ControlType.TORSO_NECK_FOLLOW, value)

    @property
    def torso_head_follow(self):
        return self._get_property(ControlType.TORSO_HEAD_FOLLOW)

    @torso_head_follow.setter
    def torso_head_follow(self, value):
        self._set_property(ControlType.TORSO_HEAD_FOLLOW, value)

    @property
    def eye_mmd_rigify(self):
        return self._get_property(ControlType.EYE_MMD_RIGIFY)

    @eye_mmd_rigify.setter
    def eye_mmd_rigify(self, value):
        self._set_property(ControlType.EYE_MMD_RIGIFY, value)

    @property
    def arm_l_ik_fk(self):
        return self._get_property(ControlType.ARM_L_IK_FK)

    @arm_l_ik_fk.setter
    def arm_l_ik_fk(self, value):
        self._set_property(ControlType.ARM_L_IK_FK, value)

    @property
    def arm_r_ik_fk(self):
        return self._get_property(ControlType.ARM_R_IK_FK)

    @arm_r_ik_fk.setter
    def arm_r_ik_fk(self, value):
        self._set_property(ControlType.ARM_R_IK_FK, value)

    @property
    def arm_l_ik_stretch(self):
        return self._get_property(ControlType.ARM_L_IK_STRETCH)

    @arm_l_ik_stretch.setter
    def arm_l_ik_stretch(self, value):
        self._set_property(ControlType.ARM_L_IK_STRETCH, value)

    @property
    def arm_r_ik_stretch(self):
        return self._get_property(ControlType.ARM_R_IK_STRETCH)

    @arm_r_ik_stretch.setter
    def arm_r_ik_stretch(self, value):
        self._set_property(ControlType.ARM_R_IK_STRETCH, value)

    @property
    def arm_l_ik_parent(self):
        return self._get_property(ControlType.ARM_L_IK_PARENT)

    @arm_l_ik_parent.setter
    def arm_l_ik_parent(self, value):
        self._set_property(ControlType.ARM_L_IK_PARENT, value)

    @property
    def arm_r_ik_parent(self):
        return self._get_property(ControlType.ARM_R_IK_PARENT)

    @arm_r_ik_parent.setter
    def arm_r_ik_parent(self, value):
        self._set_property(ControlType.ARM_R_IK_PARENT, value)

    @property
    def arm_l_pole_vector(self):
        return self._get_property(ControlType.ARM_L_POLE_VECTOR)

    @arm_l_pole_vector.setter
    def arm_l_pole_vector(self, value):
        self._set_property(ControlType.ARM_L_POLE_VECTOR, value)

    @property
    def arm_r_pole_vector(self):
        return self._get_property(ControlType.ARM_R_POLE_VECTOR)

    @arm_r_pole_vector.setter
    def arm_r_pole_vector(self, value):
        self._set_property(ControlType.ARM_R_POLE_VECTOR, value)

    @property
    def leg_l_ik_fk(self):
        return self._get_property(ControlType.LEG_L_IK_FK)

    @leg_l_ik_fk.setter
    def leg_l_ik_fk(self, value):
        self._set_property(ControlType.LEG_L_IK_FK, value)

    @property
    def leg_r_ik_fk(self):
        return self._get_property(ControlType.LEG_R_IK_FK)

    @leg_r_ik_fk.setter
    def leg_r_ik_fk(self, value):
        self._set_property(ControlType.LEG_R_IK_FK, value)

    @property
    def leg_l_ik_stretch(self):
        return self._get_property(ControlType.LEG_L_IK_STRETCH)

    @leg_l_ik_stretch.setter
    def leg_l_ik_stretch(self, value):
        self._set_property(ControlType.LEG_L_IK_STRETCH, value)

    @property
    def leg_r_ik_stretch(self):
        return self._get_property(ControlType.LEG_R_IK_STRETCH)

    @leg_r_ik_stretch.setter
    def leg_r_ik_stretch(self, value):
        self._set_property(ControlType.LEG_R_IK_STRETCH, value)

    @property
    def leg_l_ik_parent(self):
        return self._get_property(ControlType.LEG_L_IK_PARENT)

    @leg_l_ik_parent.setter
    def leg_l_ik_parent(self, value):
        self._set_property(ControlType.LEG_L_IK_PARENT, value)

    @property
    def leg_r_ik_parent(self):
        return self._get_property(ControlType.LEG_R_IK_PARENT)

    @leg_r_ik_parent.setter
    def leg_r_ik_parent(self, value):
        self._set_property(ControlType.LEG_R_IK_PARENT, value)

    @property
    def leg_l_pole_vector(self):
        return self._get_property(ControlType.LEG_L_POLE_VECTOR)

    @leg_l_pole_vector.setter
    def leg_l_pole_vector(self, value):
        self._set_property(ControlType.LEG_L_POLE_VECTOR, value)

    @property
    def leg_r_pole_vector(self):
        return self._get_property(ControlType.LEG_R_POLE_VECTOR)

    @leg_r_pole_vector.setter
    def leg_r_pole_vector(self, value):
        self._set_property(ControlType.LEG_R_POLE_VECTOR, value)

    @property
    def leg_l_pole_parent(self):
        return self._get_property(ControlType.LEG_L_POLE_PARENT)

    @leg_l_pole_parent.setter
    def leg_l_pole_parent(self, value):
        self._set_property(ControlType.LEG_L_POLE_PARENT, value)

    @property
    def leg_r_pole_parent(self):
        return self._get_property(ControlType.LEG_R_POLE_PARENT)

    @leg_r_pole_parent.setter
    def leg_r_pole_parent(self, value):
        self._set_property(ControlType.LEG_R_POLE_PARENT, value)

    def imitate_mmd_pose_behavior(self):
        """Imitate the behavior of MMD armature as much as possible."""

        self.raw_object.show_in_front = True

        # set arms IK and stretch
        self.arm_l_ik_fk = 1.000
        self.arm_r_ik_fk = 1.000
        self.arm_l_ik_stretch = 0.000
        self.arm_r_ik_stretch = 0.000
        self.arm_l_pole_vector = 0  # disable
        self.arm_r_pole_vector = 0  # disable

        # set legs IK and stretch
        self.leg_l_ik_fk = 0.000
        self.leg_r_ik_fk = 0.000
        self.leg_l_stretch = 0.000
        self.leg_r_stretch = 0.000
        self.leg_l_ik_parent = 1  # root
        self.leg_r_ik_parent = 1  # root
        self.leg_l_pole_vector = 0  # disable
        self.leg_r_pole_vector = 0  # disable
        self.leg_l_pole_parent = 2  # torso
        self.leg_r_pole_parent = 2  # torso

        # set eye motion mode
        self.eye_mmd_rigify = 0.000  # MMD

        # torso hack
        self.torso_neck_follow = 1.000  # follow chest
        self.torso_head_follow = 1.000  # follow chest

        def get_constraint(pose_bone: bpy.types.PoseBone, type: str) -> bpy.types.Constraint:
            for constraint in pose_bone.constraints:
                if constraint.type == type:
                    return constraint
            return None

        def edit_constraint(pose_bone: bpy.types.PoseBone, type: str, **kwargs) -> bpy.types.Constraint:
            constraint = get_constraint(pose_bone, type)
            if constraint is None:
                return None

            for key, value in kwargs.items():
                setattr(constraint, key, value)

        pose_bones = self.pose_bones

        # 上半身２ connect spine.002 and spine.003
        edit_constraint(pose_bones['MCH-spine.003'], 'COPY_TRANSFORMS', influence=0.000)
        edit_constraint(pose_bones['MCH-spine.002'], 'COPY_TRANSFORMS', influence=1.000)

        # TODO enable spine_fk.003
        # split 上半身２
        # constraint subtarget ORG-spine.003

        bones: RigifyArmatureBones = self.bones

        # 上半身
        bones["tweak_spine.001"].use_inherit_rotation = True

        # 下半身
        bones["spine_fk"].use_inherit_rotation = False

        # split spine.001 (上半身) and spine (下半身)
        edit_constraint(pose_bones['MCH-spine.003'], 'COPY_TRANSFORMS', subtarget='tweak_spine.001')
        edit_constraint(pose_bones['ORG-spine.001'], 'STRETCH_TO', subtarget='tweak_spine.002')

        edit_constraint(pose_bones['ORG-spine'], 'COPY_TRANSFORMS', subtarget='tweak_spine')
        edit_constraint(pose_bones['ORG-spine'], 'STRETCH_TO', subtarget='spine_fk')

        # reset rest_length
        # https://blenderartists.org/t/resetting-stretch-to-constraints-via-python/650628
        edit_constraint(pose_bones['ORG-spine.001'], 'STRETCH_TO', rest_length=0.000)
        edit_constraint(pose_bones['ORG-spine'], 'STRETCH_TO', rest_length=0.000)

    def imitate_mmd_bone_behavior(self):
        rig_edit_bones = self.edit_bones

        def get_or_create_bone(edit_bones: bpy.types.ArmatureEditBones, bone_name: str) -> bpy.types.EditBone:
            if bone_name in edit_bones:
                return edit_bones[bone_name]
            else:
                return edit_bones.new(bone_name)

        # add center (センター) bone
        center_bone = get_or_create_bone(rig_edit_bones, 'center')
        center_bone.layers = [i in {4} for i in range(32)]
        center_bone.head = Vector([0.0, 0.0, 0.7])
        center_bone.tail = Vector([0.0, 0.0, 0.0])
        center_bone.roll = 0

        # add groove (グルーブ) bone
        groove_bone = get_or_create_bone(rig_edit_bones, 'groove')
        groove_bone.layers = [i in {4} for i in range(32)]
        groove_bone.head = center_bone.head
        groove_bone.tail = groove_bone.head + Vector([0.0, 0.0, 0.1])
        groove_bone.roll = 0

        # fix torso rotation origin
        torso_bone = rig_edit_bones['torso']
        torso_bone.head = rig_edit_bones['ORG-spine.001'].head
        torso_bone.tail[2] = torso_bone.head[2]

        # set parent-child relationship
        if 'MCH-torso.parent' in rig_edit_bones:
            spine_root_bone = rig_edit_bones['MCH-torso.parent']
        else:
            spine_root_bone = rig_edit_bones['root']

        center_bone.parent = spine_root_bone
        groove_bone.parent = center_bone
        torso_bone.parent = groove_bone

        def move_bone(edit_bone: bpy.types.EditBone, head: Vector = None, tail: Vector = None):
            vector: Vector = edit_bone.vector
            if head is not None:
                edit_bone.head = head
                edit_bone.tail = head + vector
            elif tail is not None:
                edit_bone.head = tail - vector
                edit_bone.tail = tail

        spine_fk_bone = get_or_create_bone(rig_edit_bones, 'spine_fk')
        spine_fk_bone.layers = [i in {4} for i in range(32)]
        spine_fk_bone.head = rig_edit_bones['ORG-spine'].tail
        spine_fk_bone.tail = spine_fk_bone.head - rig_edit_bones['ORG-spine'].vector
        spine_fk_bone.roll = 0

        # split spine.001 (上半身) and spine (下半身)
        rig_edit_bones['ORG-spine.001'].use_connect = False
        rig_edit_bones['ORG-spine.001'].head = rig_edit_bones['ORG-spine.001'].head
        rig_edit_bones['DEF-spine.001'].use_connect = False
        rig_edit_bones['DEF-spine.001'].head = rig_edit_bones['ORG-spine.001'].head

        rig_edit_bones['ORG-spine'].tail = rig_edit_bones['ORG-spine.001'].head
        move_bone(rig_edit_bones['MCH-spine'], head=rig_edit_bones['ORG-spine.001'].head)
        move_bone(rig_edit_bones['tweak_spine.001'], head=rig_edit_bones['ORG-spine.001'].head)

        # set face bones
        def to_center(v1: Vector, v2: Vector) -> Vector:
            return (v1 + v2) / 2

        rig_eyes_bone = get_or_create_bone(rig_edit_bones, 'mmd_rigify_eyes_fk')
        rig_eyes_bone.head = to_center(rig_edit_bones['ORG-eye.L'].head, rig_edit_bones['ORG-eye.R'].head)
        rig_eyes_bone.tail = rig_eyes_bone.head - Vector([0, rig_edit_bones['ORG-eye.L'].length, 0])
        rig_eyes_bone.layers = [i in {0} for i in range(32)]
        rig_eyes_bone.parent = rig_edit_bones['ORG-face']
        rig_eyes_bone.roll = 0

        rig_eye_l_bone = get_or_create_bone(rig_edit_bones, 'mmd_rigify_eye_fk.L')
        rig_eye_l_bone.head = rig_edit_bones['master_eye.L'].head
        rig_eye_l_bone.tail = rig_edit_bones['master_eye.L'].tail
        rig_eye_l_bone.layers = [i in {0} for i in range(32)]
        rig_eye_l_bone.parent = rig_edit_bones['ORG-face']

        rig_eye_r_bone = get_or_create_bone(rig_edit_bones, 'mmd_rigify_eye_fk.R')
        rig_eye_r_bone.head = rig_edit_bones['master_eye.R'].head
        rig_eye_r_bone.tail = rig_edit_bones['master_eye.R'].tail
        rig_eye_r_bone.layers = [i in {0} for i in range(32)]
        rig_eye_r_bone.parent = rig_edit_bones['ORG-face']

    def set_bone_groups(self):
        rig_pose_bones: Dict[str, bpy.types.PoseBone] = self.pose_bones
        rig_bone_groups = self.pose_bone_groups

        rig_pose_bones['center'].bone_group = rig_bone_groups['Tweak']
        rig_pose_bones['groove'].bone_group = rig_bone_groups['Tweak']

        rig_pose_bones['mmd_rigify_eyes_fk'].bone_group = rig_bone_groups['FK']
        rig_pose_bones['mmd_rigify_eye_fk.L'].bone_group = rig_bone_groups['FK']
        rig_pose_bones['mmd_rigify_eye_fk.R'].bone_group = rig_bone_groups['FK']

    def pose_bone_constraints(self):
        eye_mmd_rigify = self.datapaths[ControlType.EYE_MMD_RIGIFY]

        def create_props(prop_storage_bone):
            for influence_prop_name in group_type2prop_names.values():
                rna_prop_ui.rna_idprop_ui_create(
                    prop_storage_bone,
                    influence_prop_name,
                    default=1.000,
                    min=0.000, max=1.000,
                    soft_min=None, soft_max=None,
                    description=None,
                    overridable=True,
                    subtype=None
                )

            rna_prop_ui.rna_idprop_ui_create(
                prop_storage_bone,
                eye_mmd_rigify.prop_name,
                default=1.000,
                min=0.000, max=1.000,
                soft_min=None, soft_max=None,
                description=None,
                overridable=True,
                subtype=None
            )

        def remove_constraints(pose_bones):
            for pose_bone in pose_bones:
                for constraint in pose_bone.constraints:
                    if not constraint.name.startswith('mmd_rigify_'):
                        continue
                    pose_bone.constraints.remove(constraint)

        # adjust rigify eyes influence
        def create_mmd_rotation_constraint(rig_bone: bpy.types.PoseBone, subtarget: str, influence_data_path: str) -> bpy.types.Constraint:
            constraint = rig_bone.constraints.new('COPY_ROTATION')
            constraint.name = 'mmd_rigify_copy_rotation_mmd'
            constraint.target = self.raw_object
            constraint.subtarget = subtarget
            constraint.target_space = 'LOCAL'
            constraint.owner_space = 'LOCAL'
            add_influence_driver(constraint, self.raw_object, influence_data_path, invert=True)
            return constraint

        rig_pose_bones: Dict[str, bpy.types.PoseBone] = self.pose_bones
        create_props(rig_pose_bones[self.prop_storage_bone_name])
        remove_constraints(rig_pose_bones)
        create_mmd_rotation_constraint(rig_pose_bones['MCH-eye.L'], 'mmd_rigify_eye_fk.L', f'pose.bones["{eye_mmd_rigify.bone_name}"]["{eye_mmd_rigify.prop_name}"]')
        create_mmd_rotation_constraint(rig_pose_bones['MCH-eye.R'], 'mmd_rigify_eye_fk.R', f'pose.bones["{eye_mmd_rigify.bone_name}"]["{eye_mmd_rigify.prop_name}"]')
        create_mmd_rotation_constraint(rig_pose_bones['mmd_rigify_eye_fk.L'], 'mmd_rigify_eyes_fk', f'pose.bones["{eye_mmd_rigify.bone_name}"]["{eye_mmd_rigify.prop_name}"]').mix_mode = 'ADD'
        create_mmd_rotation_constraint(rig_pose_bones['mmd_rigify_eye_fk.R'], 'mmd_rigify_eyes_fk', f'pose.bones["{eye_mmd_rigify.bone_name}"]["{eye_mmd_rigify.prop_name}"]').mix_mode = 'ADD'

    def pose_mmd_rest(self, dependency_graph: bpy.types.Depsgraph, iterations: int):
        pose_bones = self.pose_bones

        def set_rotation(pose_bone: bpy.types.PoseBone, rotation_matrix: Matrix):
            pose_bone.matrix = Matrix.Translation(pose_bone.matrix.to_translation()) @ rotation_matrix

        def to_rotation_matrix(pose_bone: bpy.types.PoseBone) -> Matrix:
            return pose_bone.matrix.to_euler().to_matrix().to_4x4()

        arm_l_target_rotation = Euler([math.radians(+90), math.radians(+123), math.radians(0)]).to_matrix().to_4x4()
        arm_r_target_rotation = Euler([math.radians(+90), math.radians(-123), math.radians(0)]).to_matrix().to_4x4()

        for _ in range(iterations):
            # foot.L
            pose_bones['foot_ik.L'].matrix = (
                pose_bones['foot_ik.L'].matrix
                @ Matrix.Translation(Vector([pose_bones['ORG-thigh.L'].head[0]-pose_bones['ORG-foot.L'].head[0], 0, 0]))
                @ Matrix.Rotation(-pose_bones['ORG-foot.L'].matrix.to_euler().z, 4, 'Z')
            )

            # foot.R
            pose_bones['foot_ik.R'].matrix = (
                pose_bones['foot_ik.R'].matrix
                @ Matrix.Translation(Vector([pose_bones['ORG-thigh.R'].head[0]-pose_bones['ORG-foot.R'].head[0], 0, 0]))
                @ Matrix.Rotation(-pose_bones['ORG-foot.R'].matrix.to_euler().z, 4, 'Z')
            )

            # arm.L
            for bone_name in ['upper_arm_fk.L', 'forearm_fk.L', 'hand_fk.L', ]:
                set_rotation(pose_bones[bone_name], arm_l_target_rotation)

            # arm.R
            for bone_name in ['upper_arm_fk.R', 'forearm_fk.R', 'hand_fk.R', ]:
                set_rotation(pose_bones[bone_name], arm_r_target_rotation)

            # finger.L
            target_rotation = to_rotation_matrix(pose_bones['f_middle.01.L'])
            for bone_name in ['f_index.01.L', 'f_index.02.L', 'f_index.03.L', 'f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L', 'f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L', 'f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L', ]:
                set_rotation(pose_bones[bone_name], target_rotation)

            # finger.R
            target_rotation = to_rotation_matrix(pose_bones['f_middle.01.R'])
            for bone_name in ['f_index.01.R', 'f_index.02.R', 'f_index.03.R', 'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R', 'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R', 'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R', ]:
                set_rotation(pose_bones[bone_name], target_rotation)

            dependency_graph.update()

    def assign_mmd_bone_names(self):
        pose_bones = self.pose_bones
        mmd_bone_name2pose_bone_names = {b.mmd_bone_name: b.pose_bone_name for b in mmd_rigify_bones}

        # clear mmd pose bone names
        for pose_bone in pose_bones:
            if pose_bone.mmd_bone.name_j not in mmd_bone_name2pose_bone_names:
                continue
            pose_bone.mmd_bone.name_j = ''

        for mmd_bone_name, pose_bone_name in mmd_bone_name2pose_bone_names.items():
            if pose_bone_name is None:
                continue

            pose_bones[pose_bone_name].mmd_bone.name_j = mmd_bone_name

    def remove_unused_face_bones(self):
        # remove unused face drivers
        rig_pose_bones: Dict[str, bpy.types.PoseBone] = self.pose_bones
        rig_pose_bones['MCH-jaw_master'].constraints['Copy Transforms.001'].driver_remove('influence')
        rig_pose_bones['MCH-jaw_master.001'].constraints['Copy Transforms.001'].driver_remove('influence')
        rig_pose_bones['MCH-jaw_master.002'].constraints['Copy Transforms.001'].driver_remove('influence')
        rig_pose_bones['MCH-jaw_master.003'].constraints['Copy Transforms.001'].driver_remove('influence')

        # remove unused face bones
        use_bone_names = {
            'MCH-eyes_parent',
            'eyes',
            'eye.L', 'eye.R',
            'master_eye.L', 'master_eye.R',
            'MCH-eye.L', 'MCH-eye.R',
            'ORG-eye.L', 'ORG-eye.R',
            'mmd_rigify_eyes_fk',
            'mmd_rigify_eye_fk.L', 'mmd_rigify_eye_fk.R',
        }
        rig_edit_bones: bpy.types.ArmatureEditBones = self.edit_bones
        for rig_edit_bone in rig_edit_bones['ORG-face'].children_recursive:
            if rig_edit_bone.name in use_bone_names:
                continue

            rig_edit_bones.remove(rig_edit_bone)

    def fit_bone_rotations(self, mmd_armature_object: MMDArmatureObject):
        rig_edit_bones: bpy.types.ArmatureEditBones = self.edit_bones
        mmd_edit_bones: MMDArmatureEditBones = mmd_armature_object.edit_bones

        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            bind_bone_name = mmd_rigify_bone.bind_bone_name
            if bind_bone_name is None:
                continue

            mmd_bone_name = mmd_rigify_bone.mmd_bone_name
            if mmd_bone_name not in mmd_edit_bones or bind_bone_name not in rig_edit_bones:
                continue

            mmd_edit_bones[mmd_bone_name].roll = rig_edit_bones[bind_bone_name].roll


class MMDRigifyArmatureObject(RigifyArmatureObject):

    @staticmethod
    def is_mmd_integrated_object(obj: bpy.types.Object):
        if not RigifyArmatureObject.is_rigify_armature_object(obj):
            return False

        if not MMDArmatureObject.is_mmd_armature_object(obj):
            return False

        pose_bones: Dict[str, bpy.types.PoseBone] = obj.pose.bones

        prop_storage_bone = pose_bones[RigifyArmatureObject.prop_storage_bone_name]
        for influence_prop_name in group_type2prop_names.values():
            if influence_prop_name not in prop_storage_bone:
                return False

        return True

    def imitate_mmd_bone_behavior(self, mmd_armature_object: MMDArmatureObject):
        rig_edit_bones: bpy.types.ArmatureEditBones = self.edit_bones
        mmd_edit_bones: MMDArmatureEditBones = mmd_armature_object.edit_bones

        # add center (センター) bone
        center_bone = rig_edit_bones.new('center')
        center_bone.layers = [i in {4} for i in range(32)]
        center_bone.head = mmd_edit_bones['センター'].head
        center_bone.tail = mmd_edit_bones['センター'].tail
        center_bone.roll = 0
        mmd_edit_bones['センター'].roll = 0

        # add groove (グルーブ) bone
        groove_bone = rig_edit_bones.new('groove')
        groove_bone.layers = [i in {4} for i in range(32)]

        if MMDBoneType.GROOVE in mmd_armature_object.existing_bone_types:
            groove_bone.head = mmd_edit_bones['グルーブ'].head
            groove_bone.tail = mmd_edit_bones['グルーブ'].tail
            mmd_edit_bones['グルーブ'].roll = 0
        else:
            groove_bone.head = mmd_edit_bones['センター'].head
            groove_bone.tail = groove_bone.head + Vector([0.0, 0.0, 0.1])

        groove_bone.roll = 0

        # fix torso rotation origin
        torso_bone = rig_edit_bones['torso']
        torso_bone.head = mmd_edit_bones['上半身'].head
        torso_bone.tail[2] = torso_bone.head[2]

        # set parent-child relationship
        center_bone.parent = rig_edit_bones['MCH-torso.parent']
        groove_bone.parent = center_bone
        torso_bone.parent = groove_bone

        def move_bone(edit_bone: bpy.types.EditBone, head: Vector = None, tail: Vector = None):
            vector: Vector = edit_bone.vector
            if head is not None:
                edit_bone.head = head
                edit_bone.tail = head + vector
            elif tail is not None:
                edit_bone.head = tail - vector
                edit_bone.tail = tail

        # split spine.001 (上半身) and spine (下半身)
        rig_edit_bones['ORG-spine.001'].use_connect = False
        rig_edit_bones['ORG-spine.001'].head = mmd_edit_bones['上半身'].head
        rig_edit_bones['DEF-spine.001'].use_connect = False
        rig_edit_bones['DEF-spine.001'].head = mmd_edit_bones['上半身'].head

        rig_edit_bones['ORG-spine'].tail = rig_edit_bones['spine_fk'].head
        move_bone(rig_edit_bones['MCH-spine'], head=mmd_edit_bones['上半身'].head)
        move_bone(rig_edit_bones['tweak_spine.001'], head=mmd_edit_bones['上半身'].head)

        # set face bones
        eye_height_translation_vector = Vector([0.0, 0.0, mmd_edit_bones['左目'].head[2] - rig_edit_bones['ORG-eye.L'].head[2]])

        rig_edit_bones['ORG-eye.L'].parent = rig_edit_bones['ORG-face']
        rig_edit_bones['ORG-eye.L'].length = mmd_edit_bones['左目'].length
        move_bone(rig_edit_bones['ORG-eye.L'], head=mmd_edit_bones['左目'].head)
        mmd_edit_bones['左目'].head = rig_edit_bones['ORG-eye.L'].head
        mmd_edit_bones['左目'].tail = rig_edit_bones['ORG-eye.L'].tail

        rig_edit_bones['ORG-eye.R'].parent = rig_edit_bones['ORG-face']
        rig_edit_bones['ORG-eye.R'].length = mmd_edit_bones['右目'].length
        move_bone(rig_edit_bones['ORG-eye.R'], head=mmd_edit_bones['右目'].head)
        mmd_edit_bones['右目'].head = rig_edit_bones['ORG-eye.R'].head
        mmd_edit_bones['右目'].tail = rig_edit_bones['ORG-eye.R'].tail

        rig_edit_bones['eyes'].translate(eye_height_translation_vector)
        rig_edit_bones['eye.L'].translate(eye_height_translation_vector)
        rig_edit_bones['eye.R'].translate(eye_height_translation_vector)
        rig_edit_bones['master_eye.L'].translate(eye_height_translation_vector)
        rig_edit_bones['master_eye.R'].translate(eye_height_translation_vector)
        rig_edit_bones['MCH-eye.R'].translate(eye_height_translation_vector)
        rig_edit_bones['MCH-eye.L'].translate(eye_height_translation_vector)

        def get_or_create_bone(edit_bones: bpy.types.ArmatureEditBones, bone_name: str) -> bpy.types.EditBone:
            if bone_name in edit_bones:
                return edit_bones[bone_name]
            else:
                return edit_bones.new(bone_name)

        def to_center(v1: Vector, v2: Vector) -> Vector:
            return (v1 + v2) / 2

        rig_eyes_bone = get_or_create_bone(rig_edit_bones, 'mmd_rigify_eyes_fk')
        rig_eyes_bone.head = to_center(rig_edit_bones['ORG-eye.L'].head, rig_edit_bones['ORG-eye.R'].head)
        rig_eyes_bone.tail = rig_eyes_bone.head - Vector([0, mmd_edit_bones['両目'].length, 0])
        rig_eyes_bone.layers = [i in {0} for i in range(32)]
        rig_eyes_bone.parent = rig_edit_bones['ORG-face']
        rig_eyes_bone.roll = 0
        mmd_edit_bones['両目'].roll = 0

        rig_eye_l_bone = get_or_create_bone(rig_edit_bones, 'mmd_rigify_eye_fk.L')
        rig_eye_l_bone.head = rig_edit_bones['master_eye.L'].head
        rig_eye_l_bone.tail = rig_edit_bones['master_eye.L'].tail
        rig_eye_l_bone.layers = [i in {0} for i in range(32)]
        rig_eye_l_bone.parent = rig_edit_bones['ORG-face']

        rig_eye_r_bone = get_or_create_bone(rig_edit_bones, 'mmd_rigify_eye_fk.R')
        rig_eye_r_bone.head = rig_edit_bones['master_eye.R'].head
        rig_eye_r_bone.tail = rig_edit_bones['master_eye.R'].tail
        rig_eye_r_bone.layers = [i in {0} for i in range(32)]
        rig_eye_r_bone.parent = rig_edit_bones['ORG-face']

    def bind_bones(self, mmd_armature_object: MMDArmatureObject):
        # bind rigify -> mmd
        mmd_pose_bones: MMDArmaturePoseBones = mmd_armature_object.pose_bones
        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            if mmd_rigify_bone.bind_type == MMDBindType.NONE:
                continue

            mmd_bone_name = mmd_rigify_bone.mmd_bone_name
            mmd_pose_bone = mmd_pose_bones[mmd_bone_name]
            prop_data_path = f'pose.bones["torso"]["{group_type2prop_names[mmd_rigify_bone.group_type]}"]'

            for constraint in mmd_pose_bone.constraints:
                if constraint.name == 'IK' and constraint.type == 'IK':
                    # mmd internal IK influence
                    add_influence_driver(constraint, self.raw_object, prop_data_path, invert=True)

                elif mmd_rigify_bone.bind_type == MMDBindType.COPY_EYE:
                    # mmd internal eye influence
                    add_influence_driver(constraint, self.raw_object, prop_data_path, invert=True)

            binders[mmd_rigify_bone.bind_type](
                mmd_pose_bone,
                self.raw_object,
                mmd_rigify_bone.bind_bone_name,
                prop_data_path
            )


class MetarigArmatureObject:
    raw_object: bpy.types.Object
    raw_armature: bpy.types.Armature

    def __init__(self, metarig_armature_object: bpy.types.Object):
        self.raw_object = metarig_armature_object
        self.raw_armature: bpy.types.Armature = self.raw_object.data

    @property
    def bones(self) -> bpy.types.ArmatureBones:
        return self.raw_armature.bones

    @property
    def edit_bones(self) -> bpy.types.ArmatureEditBones:
        return self.raw_armature.edit_bones

    @property
    def pose_bones(self) -> Dict[str, bpy.types.PoseBone]:
        return self.raw_object.pose.bones

    def fit_scale(self, mmd_armature_object: MMDArmatureObject):
        rigify_height = self.bones['spine.006'].tail_local[2]
        mmd_height = mmd_armature_object.bones['頭'].tail_local[2]

        scale = mmd_height / rigify_height
        self.raw_object.scale = (scale, scale, scale)
        bpy.ops.object.transform_apply(scale=True)

    def fit_bones(self, mmd_armature_object: MMDArmatureObject):
        def to_center(v1: Vector, v2: Vector) -> Vector:
            return (v1 + v2) / 2

        def to_bone_center(bone: bpy.types.EditBone) -> Vector:
            return to_center(bone.head, bone.tail)

        metarig_edit_bones = self.edit_bones
        mmd_edit_bones = mmd_armature_object.edit_bones
        metarig_edit_bones['spine.001'].tail = mmd_edit_bones['上半身'].tail
        metarig_edit_bones['spine.002'].tail = to_bone_center(mmd_edit_bones['上半身2'])
        metarig_edit_bones['spine.003'].tail = mmd_edit_bones['上半身2'].tail
        metarig_edit_bones['spine.004'].tail = to_bone_center(mmd_edit_bones['首'])
        metarig_edit_bones['spine.004'].head = mmd_edit_bones['首'].head
        metarig_edit_bones['spine.005'].tail = mmd_edit_bones['首'].tail
        metarig_edit_bones['spine.006'].tail = mmd_edit_bones['頭'].tail

        metarig_edit_bones['face'].head = mmd_edit_bones['頭'].head
        metarig_edit_bones['face'].tail = to_bone_center(mmd_edit_bones['頭'])

        metarig_edit_bones['shoulder.L'].head = mmd_edit_bones['左肩'].head
        metarig_edit_bones['shoulder.L'].tail = mmd_edit_bones['左肩'].tail
        metarig_edit_bones['shoulder.R'].head = mmd_edit_bones['右肩'].head
        metarig_edit_bones['shoulder.R'].tail = mmd_edit_bones['右肩'].tail
        metarig_edit_bones['upper_arm.L'].head = mmd_edit_bones['左腕'].head
        metarig_edit_bones['upper_arm.R'].head = mmd_edit_bones['右腕'].head
        metarig_edit_bones['forearm.L'].head = mmd_edit_bones['左ひじ'].head
        metarig_edit_bones['forearm.L'].tail = mmd_edit_bones['左手捩'].tail
        metarig_edit_bones['forearm.R'].head = mmd_edit_bones['右ひじ'].head
        metarig_edit_bones['forearm.R'].tail = mmd_edit_bones['右手捩'].tail

        metarig_edit_bones['hand.L'].tail = mmd_edit_bones['左手首'].tail
        metarig_edit_bones['hand.R'].tail = mmd_edit_bones['右手首'].tail
        metarig_edit_bones['thumb.01.L'].head = mmd_edit_bones['左親指０'].head
        metarig_edit_bones['thumb.01.L'].tail = mmd_edit_bones['左親指０'].tail
        metarig_edit_bones['thumb.01.R'].head = mmd_edit_bones['右親指０'].head
        metarig_edit_bones['thumb.01.R'].tail = mmd_edit_bones['右親指０'].tail
        metarig_edit_bones['thumb.02.L'].tail = mmd_edit_bones['左親指１'].tail
        metarig_edit_bones['thumb.02.R'].tail = mmd_edit_bones['右親指１'].tail
        metarig_edit_bones['thumb.03.L'].tail = mmd_edit_bones['左親指２'].tail
        metarig_edit_bones['thumb.03.R'].tail = mmd_edit_bones['右親指２'].tail
        metarig_edit_bones['palm.01.L'].head = to_center(mmd_edit_bones['左人指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_edit_bones['palm.01.L'].tail = mmd_edit_bones['左人指１'].head
        metarig_edit_bones['palm.01.R'].head = to_center(mmd_edit_bones['右人指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_edit_bones['palm.01.R'].tail = mmd_edit_bones['右人指１'].head
        metarig_edit_bones['f_index.01.L'].head = mmd_edit_bones['左人指１'].head
        metarig_edit_bones['f_index.01.L'].tail = mmd_edit_bones['左人指１'].tail
        metarig_edit_bones['f_index.01.R'].head = mmd_edit_bones['右人指１'].head
        metarig_edit_bones['f_index.01.R'].tail = mmd_edit_bones['右人指１'].tail
        metarig_edit_bones['f_index.02.L'].tail = mmd_edit_bones['左人指２'].tail
        metarig_edit_bones['f_index.02.R'].tail = mmd_edit_bones['右人指２'].tail
        metarig_edit_bones['f_index.03.L'].tail = mmd_edit_bones['左人指３'].tail
        metarig_edit_bones['f_index.03.R'].tail = mmd_edit_bones['右人指３'].tail
        metarig_edit_bones['palm.02.L'].head = to_center(mmd_edit_bones['左中指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_edit_bones['palm.02.L'].tail = mmd_edit_bones['左中指１'].head
        metarig_edit_bones['palm.02.R'].head = to_center(mmd_edit_bones['右中指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_edit_bones['palm.02.R'].tail = mmd_edit_bones['右中指１'].head
        metarig_edit_bones['f_middle.01.L'].head = mmd_edit_bones['左中指１'].head
        metarig_edit_bones['f_middle.01.L'].tail = mmd_edit_bones['左中指１'].tail
        metarig_edit_bones['f_middle.01.R'].head = mmd_edit_bones['右中指１'].head
        metarig_edit_bones['f_middle.01.R'].tail = mmd_edit_bones['右中指１'].tail
        metarig_edit_bones['f_middle.02.L'].tail = mmd_edit_bones['左中指２'].tail
        metarig_edit_bones['f_middle.02.R'].tail = mmd_edit_bones['右中指２'].tail
        metarig_edit_bones['f_middle.03.L'].tail = mmd_edit_bones['左中指３'].tail
        metarig_edit_bones['f_middle.03.R'].tail = mmd_edit_bones['右中指３'].tail
        metarig_edit_bones['palm.03.L'].head = to_center(mmd_edit_bones['左薬指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_edit_bones['palm.03.L'].tail = mmd_edit_bones['左薬指１'].head
        metarig_edit_bones['palm.03.R'].head = to_center(mmd_edit_bones['右薬指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_edit_bones['palm.03.R'].tail = mmd_edit_bones['右薬指１'].head
        metarig_edit_bones['f_ring.01.L'].head = mmd_edit_bones['左薬指１'].head
        metarig_edit_bones['f_ring.01.L'].tail = mmd_edit_bones['左薬指１'].tail
        metarig_edit_bones['f_ring.01.R'].head = mmd_edit_bones['右薬指１'].head
        metarig_edit_bones['f_ring.01.R'].tail = mmd_edit_bones['右薬指１'].tail
        metarig_edit_bones['f_ring.02.L'].tail = mmd_edit_bones['左薬指２'].tail
        metarig_edit_bones['f_ring.02.R'].tail = mmd_edit_bones['右薬指２'].tail
        metarig_edit_bones['f_ring.03.L'].tail = mmd_edit_bones['左薬指３'].tail
        metarig_edit_bones['f_ring.03.R'].tail = mmd_edit_bones['右薬指３'].tail
        metarig_edit_bones['palm.04.L'].head = to_center(mmd_edit_bones['左小指１'].head, mmd_edit_bones['左手捩'].tail)
        metarig_edit_bones['palm.04.L'].tail = mmd_edit_bones['左小指１'].head
        metarig_edit_bones['palm.04.R'].head = to_center(mmd_edit_bones['右小指１'].head, mmd_edit_bones['右手捩'].tail)
        metarig_edit_bones['palm.04.R'].tail = mmd_edit_bones['右小指１'].head
        metarig_edit_bones['f_pinky.01.L'].head = mmd_edit_bones['左小指１'].head
        metarig_edit_bones['f_pinky.01.L'].tail = mmd_edit_bones['左小指１'].tail
        metarig_edit_bones['f_pinky.01.R'].head = mmd_edit_bones['右小指１'].head
        metarig_edit_bones['f_pinky.01.R'].tail = mmd_edit_bones['右小指１'].tail
        metarig_edit_bones['f_pinky.02.L'].tail = mmd_edit_bones['左小指２'].tail
        metarig_edit_bones['f_pinky.02.R'].tail = mmd_edit_bones['右小指２'].tail
        metarig_edit_bones['f_pinky.03.L'].tail = mmd_edit_bones['左小指３'].tail
        metarig_edit_bones['f_pinky.03.R'].tail = mmd_edit_bones['右小指３'].tail

        metarig_edit_bones['spine'].head = mmd_edit_bones['下半身'].tail
        metarig_edit_bones['spine'].tail = mmd_edit_bones['下半身'].head
        metarig_edit_bones['pelvis.L'].head = mmd_edit_bones['下半身'].tail
        metarig_edit_bones['pelvis.R'].head = mmd_edit_bones['下半身'].tail
        metarig_edit_bones['pelvis.L'].tail[1:3] = [mmd_edit_bones['下半身'].tail[1]-metarig_edit_bones['spine'].length/2, mmd_edit_bones['下半身'].head[2]]
        metarig_edit_bones['pelvis.R'].tail[1:3] = [mmd_edit_bones['下半身'].tail[1]-metarig_edit_bones['spine'].length/2, mmd_edit_bones['下半身'].head[2]]

        metarig_edit_bones['thigh.L'].head = mmd_edit_bones['左足'].head
        metarig_edit_bones['thigh.L'].tail = mmd_edit_bones['左足'].tail
        metarig_edit_bones['thigh.R'].head = mmd_edit_bones['右足'].head
        metarig_edit_bones['thigh.R'].tail = mmd_edit_bones['右足'].tail
        metarig_edit_bones['shin.L'].tail = mmd_edit_bones['左ひざ'].tail
        metarig_edit_bones['shin.R'].tail = mmd_edit_bones['右ひざ'].tail
        metarig_edit_bones['foot.L'].tail = mmd_edit_bones['左足首'].tail
        metarig_edit_bones['foot.R'].tail = mmd_edit_bones['右足首'].tail
        metarig_edit_bones['heel.02.L'].tail = mmd_edit_bones['左ひざ'].tail.copy()
        metarig_edit_bones['heel.02.L'].tail[0] += +mmd_edit_bones['左ひざ'].length / 8
        metarig_edit_bones['heel.02.L'].tail[1] += +mmd_edit_bones['左ひざ'].length / 10
        metarig_edit_bones['heel.02.L'].tail[2] = 0
        metarig_edit_bones['heel.02.L'].head = mmd_edit_bones['左ひざ'].tail.copy()
        metarig_edit_bones['heel.02.L'].head[0] += -mmd_edit_bones['左ひざ'].length / 8
        metarig_edit_bones['heel.02.L'].head[1] += +mmd_edit_bones['左ひざ'].length / 10
        metarig_edit_bones['heel.02.L'].head[2] = 0
        metarig_edit_bones['heel.02.R'].tail = mmd_edit_bones['右ひざ'].tail.copy()
        metarig_edit_bones['heel.02.R'].tail[0] += -mmd_edit_bones['右ひざ'].length / 8
        metarig_edit_bones['heel.02.R'].tail[1] += +mmd_edit_bones['右ひざ'].length / 10
        metarig_edit_bones['heel.02.R'].tail[2] = 0
        metarig_edit_bones['heel.02.R'].head = mmd_edit_bones['右ひざ'].tail.copy()
        metarig_edit_bones['heel.02.R'].head[0] += +mmd_edit_bones['右ひざ'].length / 8
        metarig_edit_bones['heel.02.R'].head[1] += +mmd_edit_bones['右ひざ'].length / 10
        metarig_edit_bones['heel.02.R'].head[2] = 0
        metarig_edit_bones['toe.L'].tail = mmd_edit_bones['左足首'].tail + Vector([+0.0, -mmd_edit_bones['左足首'].length / 2, +0.0])
        metarig_edit_bones['toe.R'].tail = mmd_edit_bones['右足首'].tail + Vector([+0.0, -mmd_edit_bones['右足首'].length / 2, +0.0])

        # fix straight finger bend problem
        # https://blenderartists.org/t/rigify-fingers-issue/1218987
        # limbs.super_finger
        metarig_edit_bones['thumb.01.L'].roll += math.radians(-45)
        metarig_edit_bones['thumb.02.L'].roll += math.radians(-45)
        metarig_edit_bones['thumb.03.L'].roll += math.radians(-45)
        metarig_edit_bones['f_index.01.L'].roll += math.radians(-45)
        metarig_edit_bones['f_index.02.L'].roll += math.radians(-45)
        metarig_edit_bones['f_index.03.L'].roll += math.radians(-45)
        metarig_edit_bones['f_middle.01.L'].roll += math.radians(-45)
        metarig_edit_bones['f_middle.02.L'].roll += math.radians(-45)
        metarig_edit_bones['f_middle.03.L'].roll += math.radians(-45)
        metarig_edit_bones['f_ring.01.L'].roll += math.radians(-45)
        metarig_edit_bones['f_ring.02.L'].roll += math.radians(-45)
        metarig_edit_bones['f_ring.03.L'].roll += math.radians(-45)
        metarig_edit_bones['f_pinky.01.L'].roll += math.radians(-45)
        metarig_edit_bones['f_pinky.02.L'].roll += math.radians(-45)
        metarig_edit_bones['f_pinky.03.L'].roll += math.radians(-45)

        metarig_edit_bones['thumb.01.R'].roll += math.radians(+45)
        metarig_edit_bones['thumb.02.R'].roll += math.radians(+45)
        metarig_edit_bones['thumb.03.R'].roll += math.radians(+45)
        metarig_edit_bones['f_index.01.R'].roll += math.radians(+45)
        metarig_edit_bones['f_index.02.R'].roll += math.radians(+45)
        metarig_edit_bones['f_index.03.R'].roll += math.radians(+45)
        metarig_edit_bones['f_middle.01.R'].roll += math.radians(+45)
        metarig_edit_bones['f_middle.02.R'].roll += math.radians(+45)
        metarig_edit_bones['f_middle.03.R'].roll += math.radians(+45)
        metarig_edit_bones['f_ring.01.R'].roll += math.radians(+45)
        metarig_edit_bones['f_ring.02.R'].roll += math.radians(+45)
        metarig_edit_bones['f_ring.03.R'].roll += math.radians(+45)
        metarig_edit_bones['f_pinky.01.R'].roll += math.radians(+45)
        metarig_edit_bones['f_pinky.02.R'].roll += math.radians(+45)
        metarig_edit_bones['f_pinky.03.R'].roll += math.radians(+45)

        # fix elbow pole problem
        # https://blenderartists.org/t/rigify-elbow-problem/565285
        metarig_edit_bones['upper_arm.L'].tail += Vector([0, +0.001, 0])
        metarig_edit_bones['upper_arm.R'].tail += Vector([0, +0.001, 0])

        # remove unused mmd_edit_bones
        remove_metarig_edit_bones = [
            metarig_edit_bones['breast.L'],
            metarig_edit_bones['breast.R'],
        ]
        for metarig_bone in remove_metarig_edit_bones:
            metarig_edit_bones.remove(metarig_bone)

    def set_rigify_parameters(self):
        metarig_pose_bones = self.pose_bones

        # fix straight finger bend problem
        # https://blenderartists.org/t/rigify-fingers-issue/1218987
        # limbs.super_finger
        metarig_pose_bones['thumb.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['thumb.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['thumb.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['thumb.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_index.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_index.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_index.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_index.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_middle.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_middle.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_middle.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_middle.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_ring.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_ring.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_ring.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_ring.01.R'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_pinky.01.L'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_pinky.01.L'].rigify_parameters.make_extra_ik_control = True
        metarig_pose_bones['f_pinky.01.R'].rigify_parameters.primary_rotation_axis = 'X'
        metarig_pose_bones['f_pinky.01.R'].rigify_parameters.make_extra_ik_control = True

        # fix straight arm IK problem
        # limbs.super_limb
        metarig_pose_bones['upper_arm.L'].rigify_parameters.rotation_axis = 'x'
        metarig_pose_bones['upper_arm.R'].rigify_parameters.rotation_axis = 'x'

        # fix straight leg IK problem
        # limbs.super_limb
        metarig_pose_bones['thigh.L'].rigify_parameters.rotation_axis = 'x'
        metarig_pose_bones['thigh.R'].rigify_parameters.rotation_axis = 'x'
