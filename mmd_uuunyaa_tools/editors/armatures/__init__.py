# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Union

import bpy
import rna_prop_ui
from mathutils import Matrix, Vector
from mmd_uuunyaa_tools import PACKAGE_PATH
from mmd_uuunyaa_tools.utilities import import_mmd_tools

PATH_BLENDS_RIGSHAPELIBRARY = os.path.join(PACKAGE_PATH, 'blends', 'RigShapeLibrary.blend')


def add_influence_driver(constraint: bpy.types.Constraint, target: bpy.types.Object, data_path: str, invert=False):
    driver: bpy.types.Driver = constraint.driver_add('influence').driver
    variable: bpy.types.DriverVariable = driver.variables.new()
    variable.name = 'mmd_uuunyaa_influence'
    variable.targets[0].id = target
    variable.targets[0].data_path = data_path
    driver.expression = ('1-' if invert else '+') + variable.name


class MMDBindType(Enum):
    NONE = 0
    COPY_POSE = 1
    COPY_PARENT = 2
    COPY_LOCAL = 3
    COPY_SPINE = 4
    COPY_TOE = 5
    COPY_EYE = 6
    COPY_ROOT = 7


class MMDBoneType(Enum):
    STANDARD = '標準'
    PARENT = '全ての親'
    UPPER_ARM_TWIST = '腕捩'
    WRIST_TWIST = '手捩'
    UPPER_BODY_1 = '上半身1'
    UPPER_BODY_2 = '上半身２'
    GROOVE = 'グルーブ'
    TOLSO = '腰'
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
class MMDBoneInfo(Enum):
    # pylint: disable=non-ascii-name,invalid-name,too-many-instance-attributes

    bone_type: MMDBoneType
    mmd_bone_name: str

    全ての親 = (MMDBoneType.PARENT, '全ての親')
    センター = (MMDBoneType.STANDARD, 'センター')
    グルーブ = (MMDBoneType.GROOVE, 'グルーブ')
    腰 = (MMDBoneType.TOLSO, '腰')
    上半身 = (MMDBoneType.STANDARD, '上半身')
    上半身1 = (MMDBoneType.UPPER_BODY_1, '上半身1')
    上半身2 = (MMDBoneType.UPPER_BODY_2, '上半身2')
    首 = (MMDBoneType.STANDARD, '首')
    頭 = (MMDBoneType.STANDARD, '頭')

    両目 = (MMDBoneType.STANDARD, '両目')
    左目 = (MMDBoneType.STANDARD, '左目')
    右目 = (MMDBoneType.STANDARD, '右目')

    左肩 = (MMDBoneType.STANDARD, '左肩')
    左腕 = (MMDBoneType.STANDARD, '左腕')
    左腕捩 = (MMDBoneType.UPPER_ARM_TWIST, '左腕捩')
    左ひじ = (MMDBoneType.STANDARD, '左ひじ')
    左手捩 = (MMDBoneType.WRIST_TWIST, '左手捩')
    左手首 = (MMDBoneType.STANDARD, '左手首')
    左親指０ = (MMDBoneType.THUMB_0, '左親指０')
    左親指１ = (MMDBoneType.STANDARD, '左親指１')
    左親指２ = (MMDBoneType.STANDARD, '左親指２')
    左人指０ = (MMDBoneType.OTHERS, '左人指０')
    左人指１ = (MMDBoneType.STANDARD, '左人指１')
    左人指２ = (MMDBoneType.STANDARD, '左人指２')
    左人指３ = (MMDBoneType.STANDARD, '左人指３')
    左中指０ = (MMDBoneType.OTHERS, '左中指０')
    左中指１ = (MMDBoneType.STANDARD, '左中指１')
    左中指２ = (MMDBoneType.STANDARD, '左中指２')
    左中指３ = (MMDBoneType.STANDARD, '左中指３')
    左薬指０ = (MMDBoneType.OTHERS, '左薬指０')
    左薬指１ = (MMDBoneType.STANDARD, '左薬指１')
    左薬指２ = (MMDBoneType.STANDARD, '左薬指２')
    左薬指３ = (MMDBoneType.STANDARD, '左薬指３')
    左小指０ = (MMDBoneType.OTHERS, '左小指０')
    左小指１ = (MMDBoneType.STANDARD, '左小指１')
    左小指２ = (MMDBoneType.STANDARD, '左小指２')
    左小指３ = (MMDBoneType.STANDARD, '左小指３')

    右肩 = (MMDBoneType.STANDARD, '右肩')
    右腕 = (MMDBoneType.STANDARD, '右腕')
    右腕捩 = (MMDBoneType.UPPER_ARM_TWIST, '右腕捩')
    右ひじ = (MMDBoneType.STANDARD, '右ひじ')
    右手捩 = (MMDBoneType.WRIST_TWIST, '右手捩')
    右手首 = (MMDBoneType.STANDARD, '右手首')
    右親指０ = (MMDBoneType.THUMB_0, '右親指０')
    右親指１ = (MMDBoneType.STANDARD, '右親指１')
    右親指２ = (MMDBoneType.STANDARD, '右親指２')
    右人指０ = (MMDBoneType.OTHERS, '右人指０')
    右人指１ = (MMDBoneType.STANDARD, '右人指１')
    右人指２ = (MMDBoneType.STANDARD, '右人指２')
    右人指３ = (MMDBoneType.STANDARD, '右人指３')
    右中指０ = (MMDBoneType.OTHERS, '右中指０')
    右中指１ = (MMDBoneType.STANDARD, '右中指１')
    右中指２ = (MMDBoneType.STANDARD, '右中指２')
    右中指３ = (MMDBoneType.STANDARD, '右中指３')
    右薬指０ = (MMDBoneType.OTHERS, '右薬指０')
    右薬指１ = (MMDBoneType.STANDARD, '右薬指１')
    右薬指２ = (MMDBoneType.STANDARD, '右薬指２')
    右薬指３ = (MMDBoneType.STANDARD, '右薬指３')
    右小指０ = (MMDBoneType.OTHERS, '右小指０')
    右小指１ = (MMDBoneType.STANDARD, '右小指１')
    右小指２ = (MMDBoneType.STANDARD, '右小指２')
    右小指３ = (MMDBoneType.STANDARD, '右小指３')

    下半身 = (MMDBoneType.STANDARD, '下半身')

    左足 = (MMDBoneType.STANDARD, '左足')
    左ひざ = (MMDBoneType.STANDARD, '左ひざ')
    左足首 = (MMDBoneType.STANDARD, '左足首')
    左足ＩＫ = (MMDBoneType.STANDARD, '左足ＩＫ')
    左足先EX = (MMDBoneType.TOE_EX, '左足先EX')

    右足 = (MMDBoneType.STANDARD, '右足')
    右ひざ = (MMDBoneType.STANDARD, '右ひざ')
    右足首 = (MMDBoneType.STANDARD, '右足首')
    右足ＩＫ = (MMDBoneType.STANDARD, '右足ＩＫ')
    右足先EX = (MMDBoneType.TOE_EX, '右足先EX')

    左つま先ＩＫ = (MMDBoneType.STANDARD, '左つま先ＩＫ')
    右つま先ＩＫ = (MMDBoneType.STANDARD, '右つま先ＩＫ')
    左つま先 = (MMDBoneType.STANDARD, '左つま先')
    右つま先 = (MMDBoneType.STANDARD, '右つま先')

    左肩C = (MMDBoneType.SHOULDER_CANCEL, '左肩C')
    左肩P = (MMDBoneType.SHOULDER_CANCEL, '左肩P')
    右肩C = (MMDBoneType.SHOULDER_CANCEL, '右肩C')
    右肩P = (MMDBoneType.SHOULDER_CANCEL, '右肩P')
    左ダミー = (MMDBoneType.HAND_ACCESSORIES, '左ダミー')
    右ダミー = (MMDBoneType.HAND_ACCESSORIES, '右ダミー')
    左足IK親 = (MMDBoneType.LEG_IK_PARENT, '左足IK親')
    右足IK親 = (MMDBoneType.LEG_IK_PARENT, '右足IK親')

    def __new__(cls, bone_type: MMDBoneType, mmd_bone_name: str):
        obj = object.__new__(cls)
        obj.bone_type = bone_type
        obj.mmd_bone_name = mmd_bone_name
        return obj


@dataclass
class MMDBindInfo:
    bone_info: MMDBoneInfo

    pose_bone_name: Union[str, None]
    bind_bone_name: Union[str, None]

    group_type: GroupType
    bind_type: MMDBindType


class ArmatureObjectABC(ABC):
    raw_object: bpy.types.Object
    raw_armature: bpy.types.Armature

    def __init__(self, armature_object: bpy.types.Object):
        self.raw_object = armature_object
        self.raw_armature: bpy.types.Armature = self.raw_object.data

    @staticmethod
    def to_center(left: Vector, right: Vector) -> Vector:
        return (left + right) / 2

    @classmethod
    def to_bone_center(cls, bone: bpy.types.EditBone) -> Vector:
        return cls.to_center(bone.head, bone.tail)

    @staticmethod
    def to_bone_stretch(bone: bpy.types.EditBone, stretch_factor: float) -> Vector:
        return bone.head + bone.vector * stretch_factor

    @staticmethod
    def to_bone_suffix(bone_name: str) -> Union[str, None]:
        match = re.search(r'[_\.]([lLrR])$', bone_name)
        if not match:
            return None

        raw_suffix = match.group(1)
        if raw_suffix in {'l', 'L'}:
            return 'L'
        return 'R'

    @property
    def bones(self) -> bpy.types.ArmatureBones:
        return self.raw_armature.bones

    @property
    def pose_bones(self) -> Dict[str, bpy.types.PoseBone]:
        return self.raw_object.pose.bones

    @property
    def pose_bone_groups(self) -> bpy.types.BoneGroups:
        return self.raw_object.pose.bone_groups

    @property
    def edit_bones(self) -> bpy.types.ArmatureEditBones:
        return self.raw_armature.edit_bones

    @staticmethod
    def get_or_create_bone(edit_bones: bpy.types.ArmatureEditBones, bone_name: str) -> bpy.types.EditBone:
        if bone_name in edit_bones:
            return edit_bones[bone_name]

        return edit_bones.new(bone_name)

    @staticmethod
    def to_angle(vector: Vector, plane: str) -> float:
        if plane == 'XZ':
            return math.atan2(vector.z, vector.x)
        elif plane == 'XY':
            return math.atan2(vector.y, vector.x)
        elif plane == 'YZ':
            return math.atan2(vector.z, vector.y)

        raise ValueError(f"unknown plane, expected: XY, XZ, YZ, not '{plane}'")


class MMDArmatureObject(ArmatureObjectABC):
    exist_bone_types: Set[MMDBoneType]

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
        super().__init__(mmd_armature_object)

        self.mmd_bone_names: Set[str] = set({b.mmd_bone_name for b in MMDBoneInfo})
        self.exist_strict_bone_names: Set[str] = {
            b.mmd_bone.name_j
            for b in self.raw_object.pose.bones
            if b.mmd_bone.name_j in self.mmd_bone_names
        }
        self.exist_actual_bone_names: Set[str] = {
            b.name
            for b in self.raw_object.pose.bones
            if b.mmd_bone.name_j in self.mmd_bone_names
        }
        self.exist_bone_types: Set[MMDBoneType] = {
            b.bone_type for b in MMDBoneInfo
            if b.mmd_bone_name in self.exist_strict_bone_names
        }

    def has_bone_type(self, bone_type: MMDBoneType) -> bool:
        return bone_type in self.exist_bone_types

    def to_strict_mmd_bone_name(self, actual_mmd_bone_name: str) -> str:
        return self.pose_bones[actual_mmd_bone_name].mmd_bone.name_j

    def to_actual_mmd_bone_name(self, strict_mmd_bone_name: str) -> str:
        return self.strict_pose_bones[strict_mmd_bone_name].name

    @property
    def strict_bones(self) -> Dict[str, bpy.types.Bone]:
        return {
            self.to_strict_mmd_bone_name(b.name): b
            for b in self.raw_armature.bones
            if b.name in self.exist_actual_bone_names
        }

    @property
    def strict_pose_bones(self) -> Dict[str, bpy.types.PoseBone]:
        return {
            b.mmd_bone.name_j: b
            for b in self.raw_object.pose.bones
            if b.mmd_bone.name_j in self.mmd_bone_names
        }

    @property
    def actual_pose_bones(self) -> Dict[str, bpy.types.PoseBone]:
        return {
            b.name: b
            for b in self.raw_object.pose.bones
            if b.mmd_bone.name_j in self.mmd_bone_names
        }

    @property
    def strict_edit_bones(self) -> Dict[str, bpy.types.EditBone]:
        return {
            self.to_strict_mmd_bone_name(b.name): b
            for b in self.raw_armature.edit_bones
            if b.name in self.exist_actual_bone_names
        }

    def clean_armature(self):
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

        mmd_edit_bones = self.strict_edit_bones

        # fingers
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

        # spine chain

        upper_lower_distance = (mmd_edit_bones['上半身'].head - mmd_edit_bones['下半身'].head).length
        threshold_distance = mmd_edit_bones['下半身'].length / 4
        if upper_lower_distance > threshold_distance:
            # upper body is too far
            mmd_edit_bones['上半身'].head += -mmd_edit_bones['上半身'].vector * ((upper_lower_distance-threshold_distance)/mmd_edit_bones['上半身'].length)

        if MMDBoneType.UPPER_BODY_1 in self.exist_bone_types:
            upper_body_1_head = self.to_center(mmd_edit_bones['上半身'].head, mmd_edit_bones['上半身2'].head)
            mmd_edit_bones['上半身'].tail = upper_body_1_head
            mmd_edit_bones['上半身1'].tail = mmd_edit_bones['上半身2'].head
            mmd_edit_bones['上半身2'].tail = mmd_edit_bones['首'].head
            mmd_edit_bones['首'].tail = mmd_edit_bones['頭'].head
        elif MMDBoneType.UPPER_BODY_2 in self.exist_bone_types:
            mmd_edit_bones['上半身'].tail = mmd_edit_bones['上半身2'].head
            mmd_edit_bones['上半身2'].tail = mmd_edit_bones['首'].head
            mmd_edit_bones['首'].tail = mmd_edit_bones['頭'].head
        else:
            mmd_edit_bones['上半身'].tail = mmd_edit_bones['首'].head
            mmd_edit_bones['首'].tail = mmd_edit_bones['頭'].head


@dataclass
class DataPath:
    bone_name: str
    prop_name: str

    @property
    def bone_data_path(self) -> str:
        return f'["{self.bone_name}"]'

    @property
    def prop_data_path(self) -> str:
        return f'["{self.prop_name}"]'

    @property
    def data_path(self) -> str:
        return f'["{self.bone_name}"]["{self.prop_name}"]'


class ControlType(Enum):
    EYE_MMD_UUUNYAA = 'eye_mmd_uuunyaa'
    BIND_MMD_UUUNYAA = 'bind_mmd_uuunyaa'
    LEG_L_MMD_UUUNYAA = 'leg_l_mmd_uuunyaa'
    LEG_R_MMD_UUUNYAA = 'leg_r_mmd_uuunyaa'
    TOE_L_MMD_UUUNYAA = 'toe_l_mmd_uuunyaa'
    TOE_R_MMD_UUUNYAA = 'toe_r_mmd_uuunyaa'
    TORSO_NECK_FOLLOW = 'torso_neck_follow'
    TORSO_HEAD_FOLLOW = 'torso_head_follow'
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


class RichArmatureObjectABC(ArmatureObjectABC):
    # pylint: disable=too-many-public-methods
    datapaths: Dict[str, DataPath]
    mmd_bind_infos: List[MMDBindInfo]

    def create_props(self, prop_storage_bone: bpy.types.PoseBone):
        for control_type in [
            ControlType.BIND_MMD_UUUNYAA, ControlType.EYE_MMD_UUUNYAA,
            ControlType.LEG_L_MMD_UUUNYAA, ControlType.LEG_R_MMD_UUUNYAA,
            ControlType.TOE_L_MMD_UUUNYAA, ControlType.TOE_R_MMD_UUUNYAA
        ]:
            data_path = self.datapaths.get(control_type)
            if data_path is None:
                continue

            rna_prop_ui.rna_idprop_ui_create(
                prop_storage_bone,
                data_path.prop_name,
                default=0.000,
                min=0.000, max=1.000,
                soft_min=None, soft_max=None,
                description=None,
                overridable=True,
                subtype=None
            )

    # pylint: disable=too-many-arguments
    def create_mmd_ik_constraint(self, pose_bone: bpy.types.PoseBone, subtarget: str, influence_data_path: str, chain_count: int, iterations: int, invert: bool = True) -> bpy.types.Constraint:
        constraint = pose_bone.constraints.new('IK')
        constraint.name = 'mmd_uuunyaa_ik_mmd'
        constraint.target = self.raw_object
        constraint.subtarget = subtarget
        constraint.chain_count = chain_count
        constraint.iterations = iterations
        add_influence_driver(constraint, self.raw_object, influence_data_path, invert=invert)
        return constraint

    @staticmethod
    def remove_constraints(pose_bones: Dict[str, bpy.types.PoseBone]):
        for pose_bone in pose_bones.values():
            for constraint in pose_bone.constraints:
                if not constraint.name.startswith('mmd_uuunyaa_'):
                    continue
                pose_bone.constraints.remove(constraint)

    @staticmethod
    def fit_edit_bone_rotation(target_bone: bpy.types.EditBone, reference_bone: bpy.types.EditBone):
        def set_rotation(bone, rotation_matrix: Matrix):
            bone.matrix = Matrix.Translation(bone.matrix.to_translation()) @ rotation_matrix

        def to_rotation_matrix(bone) -> Matrix:
            return bone.matrix.to_quaternion().to_matrix().to_4x4()

        set_rotation(target_bone, to_rotation_matrix(reference_bone))

    @staticmethod
    def insert_edit_bone(edit_bone: bpy.types.EditBone, parent_bone: bpy.types.EditBone):
        for bone in parent_bone.children:
            bone.parent = edit_bone
        edit_bone.parent = parent_bone

    def assign_mmd_bone_names(self, mmd2pose_bone_name_overrides: Union[Dict[str, str], None] = None):
        pose_bones = self.pose_bones
        mmd_bone_name2pose_bone_names = {b.bone_info.mmd_bone_name: b.pose_bone_name for b in self.mmd_bind_infos}

        if mmd2pose_bone_name_overrides is not None:
            mmd_bone_name2pose_bone_names.update(mmd2pose_bone_name_overrides)

        # clear mmd pose bone names
        for pose_bone in pose_bones:
            if pose_bone.mmd_bone.name_j not in mmd_bone_name2pose_bone_names:
                continue
            pose_bone.mmd_bone.name_j = ''

        for mmd_bone_name, pose_bone_name in mmd_bone_name2pose_bone_names.items():
            if pose_bone_name is None:
                continue

            if pose_bone_name not in pose_bones:
                continue

            pose_bones[pose_bone_name].mmd_bone.name_j = mmd_bone_name

    @abstractmethod
    def has_face_bones(self) -> bool:
        pass

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

    ######################
    # generated methods

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
