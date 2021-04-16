# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Iterable, List, Set, Tuple, Union

import bpy
import rna_prop_ui
from mathutils import Euler, Matrix, Quaternion, Vector
from mmd_uuunyaa_tools.utilities import MessageException, import_mmd_tools


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
    FACE = 'face'
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
    COPY_EYE = 6


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
    MMDRigifyBone(BoneType.STANDARD, '上半身', 'torso', 'ORG-spine.001', GroupType.TORSO, BindType.COPY_POSE),
    MMDRigifyBone(BoneType.UPPER_BODY_2, '上半身2', 'chest', 'ORG-spine.002', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, '首', 'neck', 'ORG-spine.005', GroupType.TORSO, BindType.COPY_PARENT),
    MMDRigifyBone(BoneType.STANDARD, '頭', 'head', 'ORG-spine.006', GroupType.TORSO, BindType.COPY_PARENT),

    MMDRigifyBone(BoneType.STANDARD, '両目', 'mmd_rigify_eyes_fk', 'mmd_rigify_eyes_fk', GroupType.FACE, BindType.COPY_EYE),
    MMDRigifyBone(BoneType.STANDARD, '左目', 'mmd_rigify_eye_fk.L', 'ORG-eye.L', GroupType.FACE, BindType.COPY_EYE),
    MMDRigifyBone(BoneType.STANDARD, '右目', 'mmd_rigify_eye_fk.R', 'ORG-eye.R', GroupType.FACE, BindType.COPY_EYE),

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
    GroupType.FACE: 'mmd_rigify_face_bind_influence',
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
        constraint.subtarget = 'spine_fk'
        constraint.target_space = 'POSE'
        constraint.owner_space = 'POSE'
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

    def copy_eye(mmd_bone, org_armature_object, org_name, influence_data_path):
        constraint = mmd_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_rigify_copy_rotation'
        constraint.target = org_armature_object
        constraint.subtarget = org_name
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        add_influence_driver(constraint, org_armature_object, influence_data_path)

    return {
        BindType.COPY_POSE: copy_pose,
        BindType.COPY_PARENT: copy_parent,
        BindType.COPY_LOCAL: copy_local,
        BindType.COPY_SPINE: copy_spine,
        BindType.COPY_TOE: copy_toe,
        BindType.COPY_EYE: copy_eye,
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
        self.mmd_armature: bpy.types.Armature = self.mmd_armature_object.data

        mmd_names: Set[str] = {b.mmd_bone_name for b in mmd_rigify_bones}

        self.pose_bones: MMDArmaturePoseBones = {
            b.mmd_bone.name_j: b
            for b in self.mmd_armature_object.pose.bones
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

        self.existing_bone_types: Set[BoneType] = {b.bone_type for b in self.mmd_rigify_bones}

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


class MMDArmatureAddMetarig(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_add_metarig'
    bl_label = 'Add Human (metarig) from MMD Armature'
    bl_description = 'Add human (metarig) from MMD armature.'
    bl_options = {'REGISTER', 'UNDO'}

    is_clean_armature: bpy.props.BoolProperty(name='Clean Armature', default=True)

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

    def clean_armature_fingers(self, mmd_armature_object: MMDArmatureObject):
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

    def clean_armature_spine(self, mmd_armature_object: MMDArmatureObject):
        mmd_edit_bones = mmd_armature_object.edit_bones

        # spine chain
        mmd_edit_bones['上半身'].tail = mmd_edit_bones['上半身2'].head
        mmd_edit_bones['上半身2'].tail = mmd_edit_bones['首'].head
        mmd_edit_bones['首'].tail = mmd_edit_bones['頭'].head

    def create_metarig_object(self) -> bpy.types.Object:
        original_cursor_location = bpy.context.scene.cursor.location
        try:
            # Rigifyのメタリグはどこに置いたとしても、
            # 生成ボタンをおすと(0, 0, 0)にRigifyArmatureが生成される。
            # よってメタリグも(0, 0, 0)に生成するようにする。
            bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
            bpy.ops.object.armature_human_metarig_add()
            return bpy.context.object
        except AttributeError as e:
            if str(e) != 'Calling operator "bpy.ops.object.armature_human_metarig_add" error, could not be found':
                raise
            raise MessageException('Failed to invoke Rigify\nPlease enable Rigify add-on.')
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
        metarig_bones['heel.02.L'].tail = mmd_edit_bones['左ひざ'].tail.copy()
        metarig_bones['heel.02.L'].tail[0] += +mmd_edit_bones['左ひざ'].length / 8
        metarig_bones['heel.02.L'].tail[1] += +mmd_edit_bones['左ひざ'].length / 10
        metarig_bones['heel.02.L'].tail[2] = 0
        metarig_bones['heel.02.L'].head = mmd_edit_bones['左ひざ'].tail.copy()
        metarig_bones['heel.02.L'].head[0] += -mmd_edit_bones['左ひざ'].length / 8
        metarig_bones['heel.02.L'].head[1] += +mmd_edit_bones['左ひざ'].length / 10
        metarig_bones['heel.02.L'].head[2] = 0
        metarig_bones['heel.02.R'].tail = mmd_edit_bones['右ひざ'].tail.copy()
        metarig_bones['heel.02.R'].tail[0] += -mmd_edit_bones['右ひざ'].length / 8
        metarig_bones['heel.02.R'].tail[1] += +mmd_edit_bones['右ひざ'].length / 10
        metarig_bones['heel.02.R'].tail[2] = 0
        metarig_bones['heel.02.R'].head = mmd_edit_bones['右ひざ'].tail.copy()
        metarig_bones['heel.02.R'].head[0] += +mmd_edit_bones['右ひざ'].length / 8
        metarig_bones['heel.02.R'].head[1] += +mmd_edit_bones['右ひざ'].length / 10
        metarig_bones['heel.02.R'].head[2] = 0
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
        remove_metarig_bones = [
            metarig_bones['breast.L'],
            metarig_bones['breast.R'],
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

        # fix straight leg IK problem
        # limbs.super_limb
        metarig_bones['thigh.L'].rigify_parameters.rotation_axis = 'x'
        metarig_bones['thigh.R'].rigify_parameters.rotation_axis = 'x'

    def execute(self, context: bpy.types.Context):
        mmd_object = context.active_object

        try:
            metarig_object = self.create_metarig_object()
        except MessageException as e:
            self.report(type={'ERROR'}, message=str(e))
            return {'CANCELLED'}

        mmd_armature_object = MMDArmatureObject(mmd_object)
        self.fit_scale(metarig_object, mmd_armature_object)

        mmd_object.select = True
        metarig_object.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        if self.is_clean_armature:
            self.clean_armature_fingers(mmd_armature_object)
            self.clean_armature_spine(mmd_armature_object)

        self.fit_bones(metarig_object.data.edit_bones, mmd_armature_object.edit_bones)

        bpy.ops.object.mode_set(mode='POSE')
        self.pose_bones(metarig_object.pose.bones, mmd_armature_object.pose_bones)

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class MMDRigifyIntegrate(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_rigify_integrate'
    bl_label = 'Integrate Rigify and MMD Armatures'
    bl_description = 'Integrate Rigify and MMD armatures.'
    bl_options = {'REGISTER', 'UNDO'}

    is_join_armatures: bpy.props.BoolProperty(name='Join Aarmtures', description='Join MMD and Rigify armatures', default=True)
    mmd_main_bone_layer: bpy.props.IntProperty(name='MMD main bone layer', default=24, min=0, max=31)
    mmd_others_bone_layer: bpy.props.IntProperty(name='MMD others bone layer', default=25, min=0, max=31)
    mmd_shadow_bone_layer: bpy.props.IntProperty(name='MMD shadow bone layer', default=26, min=0, max=31)
    mmd_dummy_bone_layer: bpy.props.IntProperty(name='MMD dummy bone layer', default=27, min=0, max=31)

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

    def change_mmd_bone_layer(self, mmd_armature_object: MMDArmatureObject):
        mmd_bones = mmd_armature_object.bones
        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            mmd_bones[mmd_rigify_bone.mmd_bone_name].layers[23] = True

    def imitate_mmd_bone_behavior(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: MMDArmatureObject):
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones
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

        if BoneType.GROOVE in mmd_armature_object.existing_bone_types:
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

    def remove_unused_face_bones(self, rigify_armature_object: bpy.types.Object):
        # remove unused face drivers
        rig_pose_bones: Dict[str, bpy.types.PoseBone] = rigify_armature_object.pose.bones
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
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones
        for rig_edit_bone in rig_edit_bones['ORG-face'].children_recursive:
            if rig_edit_bone.name in use_bone_names:
                continue

            rig_edit_bones.remove(rig_edit_bone)

    def fit_bone_rotations(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: MMDArmatureObject):
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones
        mmd_edit_bones: MMDArmatureEditBones = mmd_armature_object.edit_bones

        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            bind_bone_name = mmd_rigify_bone.bind_bone_name
            if bind_bone_name is None:
                continue

            mmd_bone_name = mmd_rigify_bone.mmd_bone_name
            if mmd_bone_name not in mmd_edit_bones or bind_bone_name not in rig_edit_bones:
                continue

            mmd_edit_bones[mmd_bone_name].roll = rig_edit_bones[bind_bone_name].roll

    def imitate_mmd_pose_behavior(self, rigify_armature_object: bpy.types.Object):
        """Imitate the behavior of MMD armature as much as possible."""

        rigify_armature_object.show_in_front = True

        pose_bones = rigify_armature_object.pose.bones

        # set arms IK and stretch
        pose_bones['upper_arm_parent.L']['IK_FK'] = 1.000
        pose_bones['upper_arm_parent.R']['IK_FK'] = 1.000
        pose_bones['upper_arm_parent.L']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.R']['IK_Stretch'] = 0.000

        # set legs IK and stretch
        pose_bones['thigh_parent.L']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.R']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.L']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.R']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.L']['pole_parent'] = 2  # torso
        pose_bones['thigh_parent.R']['pole_parent'] = 2  # torso

        # torso hack
        pose_bones['torso']["neck_follow"] = 1.000  # follow chest
        pose_bones['torso']["head_follow"] = 1.000  # follow chest

        # 上半身２ connect spine.002 and spine.003
        pose_bones['MCH-spine.003'].constraints['Copy Transforms'].influence = 0.000
        pose_bones['MCH-spine.002'].constraints['Copy Transforms'].influence = 1.000

        # TODO enable spine_fk.003
        # split 上半身２
        # constraint subtarget ORG-spine.003

        bones: bpy.types.ArmatureBones = rigify_armature_object.data.bones

        # 上半身
        bones["tweak_spine.001"].use_inherit_rotation = True

        # 下半身
        bones["spine_fk"].use_inherit_rotation = False

        # split spine.001 (上半身) and spine (下半身)
        pose_bones['ORG-spine.001'].constraints['Copy Transforms'].subtarget = 'tweak_spine.001'
        pose_bones['ORG-spine.001'].constraints['Stretch To'].subtarget = 'tweak_spine.002'

        pose_bones['ORG-spine'].constraints['Copy Transforms'].subtarget = 'tweak_spine'
        pose_bones['ORG-spine'].constraints['Stretch To'].subtarget = 'spine_fk'

        # reset rest_length
        # https://blenderartists.org/t/resetting-stretch-to-constraints-via-python/650628
        pose_bones['ORG-spine.001'].constraints['Stretch To'].rest_length = 0.000
        pose_bones['ORG-spine'].constraints['Stretch To'].rest_length = 0.000

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

        rna_prop_ui.rna_idprop_ui_create(
            torso_pose_bone,
            'mmd_rigify_eye_mmd_rigify',
            default=1.000,
            min=0.000, max=1.000,
            soft_min=None, soft_max=None,
            description=None,
            overridable=True,
            subtype=None
        )

        # bind rigify -> mmd
        mmd_pose_bones: MMDArmaturePoseBones = mmd_armature_object.pose_bones
        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            if mmd_rigify_bone.bind_type == BindType.NONE:
                continue

            mmd_bone_name = mmd_rigify_bone.mmd_bone_name
            mmd_pose_bone = mmd_pose_bones[mmd_bone_name]
            prop_data_path = f'pose.bones["torso"]["{group_type2prop_names[mmd_rigify_bone.group_type]}"]'

            for constraint in mmd_pose_bone.constraints:
                if constraint.name.startswith('mmd_rigify_'):
                    # rigify -> mmd influence
                    mmd_pose_bone.constraints.remove(constraint)

                elif constraint.name == 'IK' and constraint.type == 'IK':
                    # mmd internal IK influence
                    add_influence_driver(constraint, rigify_armature_object, prop_data_path, invert=True)

                elif mmd_rigify_bone.bind_type == BindType.COPY_EYE:
                    # mmd internal eye influence
                    add_influence_driver(constraint, rigify_armature_object, prop_data_path, invert=True)

            binders[mmd_rigify_bone.bind_type](
                mmd_pose_bone,
                rigify_armature_object,
                mmd_rigify_bone.bind_bone_name,
                prop_data_path
            )

        # adjust rigify eyes influence
        def create_mmd_rotation_constraint(rig_bone: bpy.types.PoseBone, subtarget: str, influence_data_path: str) -> bpy.types.Constraint:
            constraint = rig_bone.constraints.new('COPY_ROTATION')
            constraint.name = 'mmd_rigify_copy_rotation_mmd'
            constraint.target = rigify_armature_object
            constraint.subtarget = subtarget
            constraint.target_space = 'LOCAL'
            constraint.owner_space = 'LOCAL'
            add_influence_driver(constraint, rigify_armature_object, influence_data_path, invert=True)
            return constraint

        def create_rig_rotation_constraint(rig_bone: bpy.types.PoseBone, subtarget: str, influence_data_path: str) -> bpy.types.Constraint:
            constraint = rig_bone.constraints.new('COPY_ROTATION')
            constraint.name = 'mmd_rigify_copy_rotation_rigify'
            constraint.target = rigify_armature_object
            constraint.subtarget = subtarget
            constraint.target_space = 'LOCAL'
            constraint.owner_space = 'LOCAL'
            add_influence_driver(constraint, rigify_armature_object, influence_data_path, invert=False)
            return constraint

        create_mmd_rotation_constraint(rig_pose_bones['ORG-eye.L'], 'mmd_rigify_eye_fk.L', 'pose.bones["torso"]["mmd_rigify_eye_mmd_rigify"]')
        create_rig_rotation_constraint(rig_pose_bones['ORG-eye.L'], 'MCH-eye.L', 'pose.bones["torso"]["mmd_rigify_eye_mmd_rigify"]')
        create_mmd_rotation_constraint(rig_pose_bones['ORG-eye.R'], 'mmd_rigify_eye_fk.R', 'pose.bones["torso"]["mmd_rigify_eye_mmd_rigify"]')
        create_rig_rotation_constraint(rig_pose_bones['ORG-eye.R'], 'MCH-eye.R', 'pose.bones["torso"]["mmd_rigify_eye_mmd_rigify"]')
        create_mmd_rotation_constraint(rig_pose_bones['mmd_rigify_eye_fk.L'], 'mmd_rigify_eyes_fk', 'pose.bones["torso"]["mmd_rigify_eye_mmd_rigify"]').mix_mode = 'ADD'
        create_mmd_rotation_constraint(rig_pose_bones['mmd_rigify_eye_fk.R'], 'mmd_rigify_eyes_fk', 'pose.bones["torso"]["mmd_rigify_eye_mmd_rigify"]').mix_mode = 'ADD'

        rig_pose_bones['mmd_rigify_eyes_fk'].bone_group = rig_bone_groups['FK']
        rig_pose_bones['mmd_rigify_eye_fk.L'].bone_group = rig_bone_groups['FK']
        rig_pose_bones['mmd_rigify_eye_fk.R'].bone_group = rig_bone_groups['FK']

    def assign_mmd_bone_names(self, rigify_armature_object: bpy.types.Object):
        pose_bones = rigify_armature_object.pose.bones

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

    def set_view_layers(self, rigify_armature_object: bpy.types.Object):
        rig_armature: bpy.types.Armature = rigify_armature_object.data
        rig_armature.layers = [i in {0, 3, 5, 7, 10, 13, 16, 28} for i in range(32)]

    def join_armatures(self, rigify_armature_object: bpy.types.Object, mmd_armature_object: MMDArmatureObject):
        mmd_main_bone_layer = self.mmd_main_bone_layer
        mmd_others_bone_layer = self.mmd_others_bone_layer
        mmd_shadow_bone_layer = self.mmd_shadow_bone_layer
        mmd_dummy_bone_layer = self.mmd_dummy_bone_layer

        mmd_armature = mmd_armature_object.mmd_armature
        mmd_armature.layers = [i in {0, 8, 9, 23, mmd_main_bone_layer, mmd_others_bone_layer, mmd_shadow_bone_layer, mmd_dummy_bone_layer} for i in range(32)]

        mmd_bind_bones = {b.name for b in mmd_armature_object.bones.values()}

        for bone in mmd_armature.bones.values():
            if bone.layers[0] == True:
                bone.layers = [i in {mmd_main_bone_layer} for i in range(32)]
                if bone.name not in mmd_bind_bones:
                    bone.layers[mmd_others_bone_layer] = True

            elif bone.layers[8] == True:
                bone.layers = [i in {mmd_shadow_bone_layer} for i in range(32)]

            elif bone.layers[9] == True:
                bone.layers = [i in {mmd_dummy_bone_layer} for i in range(32)]

            elif bone.layers[23] == True:
                bone.layers[23] = False

        rigify_armature: bpy.types.Armature = rigify_armature_object.data
        layers = rigify_armature.layers
        rig_id = rigify_armature['rig_id']

        bpy.context.view_layer.objects.active = mmd_armature_object.mmd_armature_object
        bpy.ops.object.join()
        mmd_armature.layers = layers
        mmd_armature['rig_id'] = rig_id
        mmd_armature_object.mmd_armature_object.draw_type = 'WIRE'

        mmd_armature.layers[mmd_main_bone_layer] = False
        mmd_armature.layers[mmd_others_bone_layer] = True
        mmd_armature.layers[mmd_shadow_bone_layer] = False
        mmd_armature.layers[mmd_dummy_bone_layer] = False

        mmd_armature_object.mmd_armature_object.show_x_ray = True

    def execute(self, context: bpy.types.Context):
        rigify_armature_object, mmd_armature_object = self.find_armature_objects(bpy.context.selected_objects)
        mmd_armature_object = MMDArmatureObject(mmd_armature_object)

        self.change_mmd_bone_layer(mmd_armature_object)

        bpy.ops.object.mode_set(mode='EDIT')
        self.remove_unused_face_bones(rigify_armature_object)
        self.fit_bone_rotations(rigify_armature_object, mmd_armature_object)
        self.imitate_mmd_bone_behavior(rigify_armature_object, mmd_armature_object)

        bpy.ops.object.mode_set(mode='POSE')
        self.imitate_mmd_pose_behavior(rigify_armature_object)
        self.pose_bone_constraints(rigify_armature_object, mmd_armature_object)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.assign_mmd_bone_names(rigify_armature_object)
        self.set_view_layers(rigify_armature_object)

        if self.is_join_armatures:
            self.join_armatures(rigify_armature_object, mmd_armature_object)

        return {'FINISHED'}


class MMDRigifyConvert(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.rigify_to_mmd_compatible'
    bl_label = 'Convert Rigify Armature to MMD compatible'
    bl_description = 'Convert Rigify armature to MMD compatible.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False

        if context.object.type != 'ARMATURE':
            return False

        if context.active_object.data.get('rig_id') is None:
            return False

        pose_bones = bpy.context.active_object.pose.bones
        if group_type2prop_names[GroupType.TORSO] in pose_bones['torso']:
            # MMD armature
            return False

        return True

    def imitate_mmd_bone_behavior(self, rigify_armature_object: bpy.types.Object):
        rig_edit_bones: bpy.types.ArmatureEditBones = rigify_armature_object.data.edit_bones

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

    def imitate_mmd_pose_behavior(self, rigify_armature_object: bpy.types.Object):
        """Imitate the behavior of MMD armature as much as possible."""

        rigify_armature_object.show_in_front = True

        pose_bones = rigify_armature_object.pose.bones

        # set arms IK and stretch
        pose_bones['upper_arm_parent.L']['IK_FK'] = 1.000
        pose_bones['upper_arm_parent.R']['IK_FK'] = 1.000
        pose_bones['upper_arm_parent.L']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.R']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.L']['pole_vector'] = 0  # disable
        pose_bones['upper_arm_parent.R']['pole_vector'] = 0  # disable

        # set legs IK and stretch
        pose_bones['thigh_parent.L']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.R']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.L']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.R']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.L']['pole_vector'] = 0  # disable
        pose_bones['thigh_parent.R']['pole_vector'] = 0  # disable
        pose_bones['thigh_parent.L']['pole_parent'] = 2  # torso
        pose_bones['thigh_parent.R']['pole_parent'] = 2  # torso

        # torso hack
        pose_bones['torso']["neck_follow"] = 1.000  # follow chest
        pose_bones['torso']["head_follow"] = 1.000  # follow chest

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

        # 上半身２ connect spine.002 and spine.003
        edit_constraint(pose_bones['MCH-spine.003'], 'COPY_TRANSFORMS', influence=0.000)
        edit_constraint(pose_bones['MCH-spine.002'], 'COPY_TRANSFORMS', influence=1.000)

        # TODO enable spine_fk.003
        # split 上半身２
        # constraint subtarget ORG-spine.003

        bones: bpy.types.ArmatureBones = rigify_armature_object.data.bones

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
        edit_constraint(pose_bones['ORG-spine.001'], 'COPY_TRANSFORMS', rest_length=0.000)
        edit_constraint(pose_bones['ORG-spine'], 'STRETCH_TO', rest_length=0.000)

    def assign_mmd_bone_names(self, rigify_armature_object: bpy.types.Object):
        pose_bones = rigify_armature_object.pose.bones

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

    def execute(self, context: bpy.types.Context):
        rigify_armature_object = context.active_object

        bpy.ops.object.mode_set(mode='EDIT')
        self.imitate_mmd_bone_behavior(rigify_armature_object)

        bpy.ops.object.mode_set(mode='POSE')
        self.imitate_mmd_pose_behavior(rigify_armature_object)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.assign_mmd_bone_names(rigify_armature_object)
        return {'FINISHED'}


class MMDRigifyApplyMMDRestPose(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.rigify_apply_mmd_rest_pose'
    bl_label = 'Apply MMD Rest Pose'
    bl_description = 'Apply MMD rest pose.'
    bl_options = {'REGISTER', 'UNDO'}

    iterations: bpy.props.IntProperty(name='Iterations', description='Number of solving iterations', default=7, min=1, max=100)

    def initialize(self, rigify_armature_object: bpy.types.Object):
        pose_bones = rigify_armature_object.pose.bones

        # set arms IK and stretch
        # MCH-upper_arm_parent
        pose_bones['upper_arm_parent.L']['IK_FK'] = 1.000
        pose_bones['upper_arm_parent.R']['IK_FK'] = 1.000
        pose_bones['upper_arm_parent.L']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.R']['IK_Stretch'] = 0.000
        pose_bones['upper_arm_parent.L']['pole_vector'] = 0  # disable
        pose_bones['upper_arm_parent.R']['pole_vector'] = 0  # disable

        # set legs IK and stretch
        pose_bones['thigh_parent.L']['IK_FK'] = 0.000
        pose_bones['thigh_parent.R']['IK_FK'] = 0.000
        pose_bones['thigh_parent.L']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.R']['IK_Stretch'] = 0.000
        pose_bones['thigh_parent.L']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.R']['IK_parent'] = 1  # root
        pose_bones['thigh_parent.L']['pole_vector'] = 0  # disable
        pose_bones['thigh_parent.R']['pole_vector'] = 0  # disable
        pose_bones['thigh_parent.L']['pole_parent'] = 2  # torso
        pose_bones['thigh_parent.R']['pole_parent'] = 2  # torso

    def pose_mmd_rest(self, rigify_armature_object: bpy.types.Object, dependency_graph: bpy.types.Depsgraph, iterations: int):
        pose_bones: Dict[str, bpy.types.PoseBone] = rigify_armature_object.pose.bones

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

    def execute(self, context: bpy.types.Context):
        rigify_armature_object = context.active_object
        dependency_graph = context.evaluated_depsgraph_get()

        bpy.ops.object.mode_set(mode='POSE')
        self.initialize(rigify_armature_object)
        self.pose_mmd_rest(rigify_armature_object, dependency_graph, self.iterations)

        bpy.ops.object.mode_set(mode='OBJECT')
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
        pose_bones = bpy.context.active_object.pose.bones

        if group_type2prop_names[GroupType.TORSO] not in pose_bones['torso']:
            return

        layout = self.layout
        col = layout.column()

        col.label(text='MMD-Rigify:')
        row = col.row()
        row.prop(pose_bones['torso'], '["mmd_rigify_eye_mmd_rigify"]', text='Eyes', slider=True)

        col.label(text='IK-FK:')
        row = col.row()
        row.prop(pose_bones['upper_arm_parent.L'], '["IK_FK"]', text='Arm.L', slider=True)
        row.prop(pose_bones['upper_arm_parent.R'], '["IK_FK"]', text='Arm.R', slider=True)
        row = col.row()
        row.prop(pose_bones['thigh_parent.L'], '["IK_FK"]', text='Leg.L', slider=True)
        row.prop(pose_bones['thigh_parent.R'], '["IK_FK"]', text='Leg.R', slider=True)

        col.label(text='Influences:')
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.FACE]}"]', text='Face', slider=True)
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.TORSO]}"]', text='Torso', slider=True)
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.ARM_L]}"]', text='Arm.L', slider=True)
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.ARM_R]}"]', text='Arm.R', slider=True)
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.LEG_L]}"]', text='Leg.L', slider=True)
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.LEG_R]}"]', text='Leg.R', slider=True)
