# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from typing import Dict, Set

import bpy
from mathutils import Vector
from mmd_uuunyaa_tools.editors.armatures import ArmatureObjectABC, MMDBoneInfo, MMDBoneType
from mmd_uuunyaa_tools.utilities import import_mmd_tools


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
