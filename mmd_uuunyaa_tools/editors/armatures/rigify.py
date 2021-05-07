# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

# pylint: disable=too-many-lines

import math
from typing import Callable, Dict, Iterable

import bpy
from mathutils import Color, Euler, Matrix, Vector
from mmd_uuunyaa_tools.editors.armatures import (PATH_BLENDS_RIGSHAPELIBRARY,
                                                 ControlType, DataPath,
                                                 GroupType, MMDBindInfo,
                                                 MMDBindType, MMDBoneInfo,
                                                 MMDBoneType,
                                                 RichArmatureObjectABC,
                                                 add_influence_driver)
from mmd_uuunyaa_tools.editors.armatures.mmd import MMDArmatureObject


def _create_binders() -> Dict[MMDBindType, Callable]:
    # pylint: disable=too-many-statements

    def copy_pose(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_uuunyaa_copy_transforms'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'POSE'
        constraint.owner_space = 'POSE'
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_parent(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_uuunyaa_copy_transforms'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL_WITH_PARENT'
        constraint.owner_space = 'LOCAL_WITH_PARENT'
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_local(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = 'mmd_uuunyaa_copy_transforms'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_spine(pose_bone, target_object, _, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_LOCATION')
        constraint.name = 'mmd_uuunyaa_copy_location'
        constraint.target = target_object
        constraint.subtarget = 'spine_fk'
        constraint.target_space = 'POSE'
        constraint.owner_space = 'POSE'
        add_influence_driver(constraint, target_object, influence_data_path)

        constraint = pose_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_uuunyaa_copy_rotation'
        constraint.target = target_object
        constraint.subtarget = 'spine_fk'
        constraint.target_space = 'LOCAL_WITH_PARENT'
        constraint.owner_space = 'LOCAL_WITH_PARENT'
        constraint.invert_x = False
        constraint.invert_y = True
        constraint.invert_z = True
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_toe(pose_bone, target_object, subtarget, influence_data_path):

        def add_driver(constraint, target_object, influence_data_path):
            driver: bpy.types.Driver = constraint.driver_add('influence').driver
            variable: bpy.types.DriverVariable = driver.variables.new()
            variable.name = 'mmd_uuunyaa_influence'
            variable.targets[0].id = target_object
            variable.targets[0].data_path = influence_data_path

            if subtarget.endswith('.L'):
                left_right = 'l'
            else:
                left_right = 'r'

            variable: bpy.types.DriverVariable = driver.variables.new()
            variable.name = f'mmd_uuunyaa_toe_{left_right}_mmd_rigify'
            variable.targets[0].id = target_object
            variable.targets[0].data_path = f'pose.bones["torso"]["{variable.name}"]'

            driver.expression = f'mmd_uuunyaa_influence * {variable.name}'

        constraint = pose_bone.constraints.new('COPY_LOCATION')
        constraint.name = 'mmd_uuunyaa_copy_location'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.invert_x = True
        constraint.invert_y = False
        constraint.invert_z = True
        add_driver(constraint, target_object, influence_data_path)

        constraint = pose_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_uuunyaa_copy_rotation'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.invert_x = True
        constraint.invert_y = False
        constraint.invert_z = True
        constraint.mix_mode = 'ADD'
        add_driver(constraint, target_object, influence_data_path)

    def copy_eye(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_uuunyaa_copy_rotation'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        add_influence_driver(constraint, target_object, influence_data_path)

    def copy_root(pose_bone, target_object, subtarget, influence_data_path):
        constraint = pose_bone.constraints.new('COPY_LOCATION')
        constraint.name = 'mmd_uuunyaa_copy_location'
        constraint.target = target_object
        constraint.subtarget = subtarget
        constraint.target_space = 'POSE'
        constraint.owner_space = 'POSE'
        add_influence_driver(constraint, target_object, influence_data_path)

        constraint = pose_bone.constraints.new('COPY_ROTATION')
        constraint.name = 'mmd_uuunyaa_copy_rotation'
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
        MMDBindType.COPY_ROOT: copy_root,
    }


binders: Dict[MMDBindType, Callable] = _create_binders()


class RigifyArmatureObject(RichArmatureObjectABC):
    # pylint: disable=too-many-instance-attributes
    prop_storage_bone_name = 'torso'
    prop_name_mmd_uuunyaa_bind_mmd_rigify = 'mmd_uuunyaa_bind_mmd_rigify'

    mmd_bind_infos = [
        MMDBindInfo(MMDBoneInfo.全ての親, 'root', 'root', GroupType.TORSO, MMDBindType.COPY_ROOT),
        MMDBindInfo(MMDBoneInfo.センター, 'center', 'center', GroupType.TORSO, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.グルーブ, 'groove', 'groove', GroupType.TORSO, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.腰, 'torso', 'torso', GroupType.TORSO, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.上半身, 'spine_fk.001', 'ORG-spine.001', GroupType.TORSO, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.上半身1, None, None, GroupType.TORSO, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.上半身2, 'spine_fk.002', 'ORG-spine.002', GroupType.TORSO, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.首, 'neck', 'ORG-spine.004', GroupType.TORSO, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.頭, 'head', 'ORG-spine.006', GroupType.TORSO, MMDBindType.COPY_PARENT),

        MMDBindInfo(MMDBoneInfo.両目, 'mmd_uuunyaa_eyes_fk', 'mmd_uuunyaa_eyes_fk', GroupType.FACE, MMDBindType.COPY_EYE),
        MMDBindInfo(MMDBoneInfo.左目, 'mmd_uuunyaa_eye_fk.L', 'MCH-eye.L', GroupType.FACE, MMDBindType.COPY_EYE),
        MMDBindInfo(MMDBoneInfo.右目, 'mmd_uuunyaa_eye_fk.R', 'MCH-eye.R', GroupType.FACE, MMDBindType.COPY_EYE),

        MMDBindInfo(MMDBoneInfo.左肩, 'shoulder.L', 'ORG-shoulder.L', GroupType.TORSO, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左腕, 'upper_arm_fk.L', 'ORG-upper_arm.L', GroupType.ARM_L, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.左腕捩, 'mmd_uuunyaa_upper_arm_twist_fk.L', None, GroupType.ARM_L, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.左ひじ, 'forearm_fk.L', 'ORG-forearm.L', GroupType.ARM_L, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.左手捩, 'mmd_uuunyaa_wrist_twist_fk.L', None, GroupType.ARM_L, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.左手首, 'hand_fk.L', 'ORG-hand.L', GroupType.ARM_L, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.左親指０, 'thumb.01.L', 'ORG-thumb.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左親指１, 'thumb.02.L', 'ORG-thumb.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左親指２, 'thumb.03.L', 'ORG-thumb.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左人指０, None, 'ORG-palm.01.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左人指１, 'f_index.01.L', 'ORG-f_index.01.L', GroupType.ARM_L, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左人指２, 'f_index.02.L', 'ORG-f_index.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左人指３, 'f_index.03.L', 'ORG-f_index.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左中指０, None, 'ORG-palm.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左中指１, 'f_middle.01.L', 'ORG-f_middle.01.L', GroupType.ARM_L, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左中指２, 'f_middle.02.L', 'ORG-f_middle.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左中指３, 'f_middle.03.L', 'ORG-f_middle.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左薬指０, None, 'ORG-palm.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左薬指１, 'f_ring.01.L', 'ORG-f_ring.01.L', GroupType.ARM_L, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左薬指２, 'f_ring.02.L', 'ORG-f_ring.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左薬指３, 'f_ring.03.L', 'ORG-f_ring.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左小指０, None, 'ORG-palm.04.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左小指１, 'f_pinky.01.L', 'ORG-f_pinky.01.L', GroupType.ARM_L, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左小指２, 'f_pinky.02.L', 'ORG-f_pinky.02.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左小指３, 'f_pinky.03.L', 'ORG-f_pinky.03.L', GroupType.ARM_L, MMDBindType.COPY_LOCAL),

        MMDBindInfo(MMDBoneInfo.右肩, 'shoulder.R', 'ORG-shoulder.R', GroupType.TORSO, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右腕, 'upper_arm_fk.R', 'ORG-upper_arm.R', GroupType.ARM_R, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.右腕捩, 'mmd_uuunyaa_upper_arm_twist_fk.R', None, GroupType.NONE, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.右ひじ, 'forearm_fk.R', 'ORG-forearm.R', GroupType.ARM_R, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.右手捩, 'mmd_uuunyaa_wrist_twist_fk.R', None, GroupType.ARM_R, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.右手首, 'hand_fk.R', 'ORG-hand.R', GroupType.ARM_R, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.右親指０, 'thumb.01.R', 'ORG-thumb.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右親指１, 'thumb.02.R', 'ORG-thumb.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右親指２, 'thumb.03.R', 'ORG-thumb.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右人指０, None, 'ORG-palm.01.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右人指１, 'f_index.01.R', 'ORG-f_index.01.R', GroupType.ARM_R, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右人指２, 'f_index.02.R', 'ORG-f_index.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右人指３, 'f_index.03.R', 'ORG-f_index.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右中指０, None, 'ORG-palm.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右中指１, 'f_middle.01.R', 'ORG-f_middle.01.R', GroupType.ARM_R, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右中指２, 'f_middle.02.R', 'ORG-f_middle.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右中指３, 'f_middle.03.R', 'ORG-f_middle.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右薬指０, None, 'ORG-palm.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右薬指１, 'f_ring.01.R', 'ORG-f_ring.01.R', GroupType.ARM_R, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右薬指２, 'f_ring.02.R', 'ORG-f_ring.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右薬指３, 'f_ring.03.R', 'ORG-f_ring.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右小指０, None, 'ORG-palm.04.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右小指１, 'f_pinky.01.R', 'ORG-f_pinky.01.R', GroupType.ARM_R, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右小指２, 'f_pinky.02.R', 'ORG-f_pinky.02.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右小指３, 'f_pinky.03.R', 'ORG-f_pinky.03.R', GroupType.ARM_R, MMDBindType.COPY_LOCAL),

        MMDBindInfo(MMDBoneInfo.下半身, 'spine_fk', 'ORG-spine', GroupType.TORSO, MMDBindType.COPY_SPINE),

        MMDBindInfo(MMDBoneInfo.左足, 'thigh_fk.L', 'ORG-thigh.L', GroupType.LEG_L, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左ひざ, 'shin_fk.L', 'ORG-shin.L', GroupType.LEG_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左足首, 'foot_fk.L', 'ORG-foot.L', GroupType.LEG_L, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.左足ＩＫ, 'foot_ik.L', 'foot_ik.L', GroupType.LEG_L, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.左足先EX, 'toe.L', 'ORG-toe.L', GroupType.LEG_L, MMDBindType.COPY_TOE),

        MMDBindInfo(MMDBoneInfo.右足, 'thigh_fk.R', 'ORG-thigh.R', GroupType.LEG_R, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右ひざ, 'shin_fk.R', 'ORG-shin.R', GroupType.LEG_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右足首, 'foot_fk.R', 'ORG-foot.R', GroupType.LEG_R, MMDBindType.COPY_LOCAL),
        MMDBindInfo(MMDBoneInfo.右足ＩＫ, 'foot_ik.R', 'foot_ik.R', GroupType.LEG_R, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.右足先EX, 'toe.R', 'ORG-toe.R', GroupType.LEG_R, MMDBindType.COPY_TOE),

        MMDBindInfo(MMDBoneInfo.左つま先ＩＫ, 'mmd_uuunyaa_toe_ik.L', 'mmd_uuunyaa_toe_ik.L', GroupType.LEG_L, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右つま先ＩＫ, 'mmd_uuunyaa_toe_ik.R', 'mmd_uuunyaa_toe_ik.R', GroupType.LEG_R, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左つま先, None, None, GroupType.LEG_L, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.右つま先, None, None, GroupType.LEG_R, MMDBindType.NONE),

        MMDBindInfo(MMDBoneInfo.左肩C, 'mmd_uuunyaa_shoulder_cancel.L', 'mmd_uuunyaa_shoulder_cancel.L', GroupType.NONE, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左肩P, 'mmd_uuunyaa_shoulder_parent.L', 'mmd_uuunyaa_shoulder_parent.L', GroupType.NONE, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右肩C, 'mmd_uuunyaa_shoulder_cancel.R', 'mmd_uuunyaa_shoulder_cancel.R', GroupType.NONE, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.右肩P, 'mmd_uuunyaa_shoulder_parent.R', 'mmd_uuunyaa_shoulder_parent.R', GroupType.NONE, MMDBindType.COPY_PARENT),
        MMDBindInfo(MMDBoneInfo.左ダミー, None, None, GroupType.NONE, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.右ダミー, None, None, GroupType.NONE, MMDBindType.NONE),
        MMDBindInfo(MMDBoneInfo.左足IK親, 'mmd_uuunyaa_leg_ik_parent.L', 'mmd_uuunyaa_leg_ik_parent.L', GroupType.LEG_L, MMDBindType.COPY_POSE),
        MMDBindInfo(MMDBoneInfo.右足IK親, 'mmd_uuunyaa_leg_ik_parent.R', 'mmd_uuunyaa_leg_ik_parent.R', GroupType.LEG_R, MMDBindType.COPY_POSE),
    ]

    @staticmethod
    def is_rigify_armature_object(obj: bpy.types.Object):
        if obj is None:
            return False

        if obj.type != 'ARMATURE':
            return False

        rig_id = obj.data.get('rig_id')
        if not rig_id:
            return False

        return True

    def __init__(self, rigify_armature_object: bpy.types.Object):
        super().__init__(rigify_armature_object)

        control_types = {
            (True, False, 'L', 'IK_FK'): ControlType.ARM_L_IK_FK,
            (True, False, 'R', 'IK_FK'): ControlType.ARM_R_IK_FK,
            (True, False, 'L', 'IK_Stretch'): ControlType.ARM_L_IK_STRETCH,
            (True, False, 'R', 'IK_Stretch'): ControlType.ARM_R_IK_STRETCH,
            (True, False, 'L', 'IK_parent'): ControlType.ARM_L_IK_PARENT,
            (True, False, 'R', 'IK_parent'): ControlType.ARM_R_IK_PARENT,
            (True, False, 'L', 'pole_vector'): ControlType.ARM_L_POLE_VECTOR,
            (True, False, 'R', 'pole_vector'): ControlType.ARM_R_POLE_VECTOR,
            (False, True, 'L', 'IK_FK'): ControlType.LEG_L_IK_FK,
            (False, True, 'R', 'IK_FK'): ControlType.LEG_R_IK_FK,
            (False, True, 'L', 'IK_Stretch'): ControlType.LEG_L_IK_STRETCH,
            (False, True, 'R', 'IK_Stretch'): ControlType.LEG_R_IK_STRETCH,
            (False, True, 'L', 'IK_parent'): ControlType.LEG_L_IK_PARENT,
            (False, True, 'R', 'IK_parent'): ControlType.LEG_R_IK_PARENT,
            (False, True, 'L', 'pole_vector'): ControlType.LEG_L_POLE_VECTOR,
            (False, True, 'R', 'pole_vector'): ControlType.LEG_R_POLE_VECTOR,
            (False, True, 'L', 'pole_parent'): ControlType.LEG_L_POLE_PARENT,
            (False, True, 'R', 'pole_parent'): ControlType.LEG_R_POLE_PARENT,
        }

        datapaths: Dict[ControlType, DataPath] = {
            ControlType.BIND_MMD_UUUNYAA: DataPath(self.prop_storage_bone_name, self.prop_name_mmd_uuunyaa_bind_mmd_rigify),
            ControlType.EYE_MMD_UUUNYAA: DataPath(self.prop_storage_bone_name, 'mmd_uuunyaa_eye_mmd_rigify'),
            ControlType.LEG_L_MMD_UUUNYAA: DataPath(self.prop_storage_bone_name, 'mmd_uuunyaa_leg_l_mmd_rigify'),
            ControlType.LEG_R_MMD_UUUNYAA: DataPath(self.prop_storage_bone_name, 'mmd_uuunyaa_leg_r_mmd_rigify'),
            ControlType.TOE_L_MMD_UUUNYAA: DataPath(self.prop_storage_bone_name, 'mmd_uuunyaa_toe_l_mmd_rigify'),
            ControlType.TOE_R_MMD_UUUNYAA: DataPath(self.prop_storage_bone_name, 'mmd_uuunyaa_toe_r_mmd_rigify'),
            ControlType.TORSO_NECK_FOLLOW: DataPath(self.prop_storage_bone_name, 'neck_follow'),
            ControlType.TORSO_HEAD_FOLLOW: DataPath(self.prop_storage_bone_name, 'head_follow'),
        }

        pose_bones = self.pose_bones
        for pose_bone in pose_bones:
            bone_name = pose_bone.name

            is_arm_bone_name = 'upper_arm_parent' in bone_name
            is_leg_bone_name = 'thigh_parent' in bone_name
            bone_suffix = self.to_bone_suffix(bone_name)

            for key in pose_bone.keys():
                if key in {'IK_FK', 'IK/FK'}:
                    prop_name = 'IK_FK'
                elif key in {'IK_Stretch', 'IK_parent', 'pole_vector', 'pole_parent'}:
                    prop_name = key
                else:
                    continue

                control_type = control_types.get((is_arm_bone_name, is_leg_bone_name, bone_suffix, prop_name))
                if control_type is None:
                    continue

                datapaths[control_type] = DataPath(bone_name, key)

        self.datapaths = datapaths

    def has_face_bones(self) -> bool:
        require_bone_names = {'ORG-spine.006', 'ORG-eye.L', 'ORG-eye.R', 'ORG-face', 'master_eye.L', 'master_eye.R'}
        return len(require_bone_names - set(self.bones.keys())) == 0

    @property
    def bind_mmd_rigify(self):
        return self._get_property(ControlType.BIND_MMD_UUUNYAA)

    @bind_mmd_rigify.setter
    def bind_mmd_rigify(self, value):
        self._set_property(ControlType.BIND_MMD_UUUNYAA, value)

    @property
    def eye_mmd_rigify(self):
        return self._get_property(ControlType.EYE_MMD_UUUNYAA)

    @eye_mmd_rigify.setter
    def eye_mmd_rigify(self, value):
        self._set_property(ControlType.EYE_MMD_UUUNYAA, value)

    @property
    def toe_l_mmd_rigify(self):
        return self._get_property(ControlType.TOE_L_MMD_UUUNYAA)

    @toe_l_mmd_rigify.setter
    def toe_l_mmd_rigify(self, value):
        self._set_property(ControlType.TOE_L_MMD_UUUNYAA, value)

    @property
    def toe_r_mmd_rigify(self):
        return self._get_property(ControlType.TOE_R_MMD_UUUNYAA)

    @toe_r_mmd_rigify.setter
    def toe_r_mmd_rigify(self, value):
        self._set_property(ControlType.TOE_R_MMD_UUUNYAA, value)

    def _add_upper_arm_twist_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        # add upper arm twist (腕捩)
        upper_arm_twist_fk_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_upper_arm_twist_fk.L')
        upper_arm_twist_fk_l_bone.layers = [i in {8} for i in range(32)]
        upper_arm_twist_fk_l_bone.head = rig_edit_bones['upper_arm_fk.L'].tail - rig_edit_bones['upper_arm_fk.L'].vector / 3
        upper_arm_twist_fk_l_bone.tail = rig_edit_bones['upper_arm_fk.L'].tail
        upper_arm_twist_fk_l_bone.parent = rig_edit_bones['upper_arm_fk.L']
        self.fit_edit_bone_rotation(upper_arm_twist_fk_l_bone, rig_edit_bones['upper_arm_fk.L'])
        rig_edit_bones['forearm_fk.L'].use_connect = False
        rig_edit_bones['forearm_fk.L'].parent = upper_arm_twist_fk_l_bone

        upper_arm_twist_fk_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_upper_arm_twist_fk.R')
        upper_arm_twist_fk_r_bone.layers = [i in {11} for i in range(32)]
        upper_arm_twist_fk_r_bone.head = rig_edit_bones['upper_arm_fk.R'].tail - rig_edit_bones['upper_arm_fk.R'].vector / 3
        upper_arm_twist_fk_r_bone.tail = rig_edit_bones['upper_arm_fk.R'].tail
        upper_arm_twist_fk_r_bone.parent = rig_edit_bones['upper_arm_fk.R']
        self.fit_edit_bone_rotation(upper_arm_twist_fk_r_bone, rig_edit_bones['upper_arm_fk.R'])
        rig_edit_bones['forearm_fk.R'].use_connect = False
        rig_edit_bones['forearm_fk.R'].parent = upper_arm_twist_fk_r_bone

        return upper_arm_twist_fk_l_bone, upper_arm_twist_fk_r_bone

    def _add_wrist_twist_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        # add wrist twist (手捩)
        wrist_twist_fk_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_wrist_twist_fk.L')
        wrist_twist_fk_l_bone.layers = [i in {8} for i in range(32)]
        wrist_twist_fk_l_bone.head = rig_edit_bones['forearm_fk.L'].tail - rig_edit_bones['forearm_fk.L'].vector / 3
        wrist_twist_fk_l_bone.tail = rig_edit_bones['forearm_fk.L'].tail
        wrist_twist_fk_l_bone.parent = rig_edit_bones['forearm_fk.L']
        self.fit_edit_bone_rotation(wrist_twist_fk_l_bone, rig_edit_bones['forearm_fk.L'])
        rig_edit_bones['MCH-hand_fk.L'].use_connect = False
        rig_edit_bones['MCH-hand_fk.L'].parent = wrist_twist_fk_l_bone

        wrist_twist_fk_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_wrist_twist_fk.R')
        wrist_twist_fk_r_bone.layers = [i in {11} for i in range(32)]
        wrist_twist_fk_r_bone.head = rig_edit_bones['forearm_fk.R'].tail - rig_edit_bones['forearm_fk.R'].vector / 3
        wrist_twist_fk_r_bone.tail = rig_edit_bones['forearm_fk.R'].tail
        wrist_twist_fk_r_bone.parent = rig_edit_bones['forearm_fk.R']
        self.fit_edit_bone_rotation(wrist_twist_fk_r_bone, rig_edit_bones['forearm_fk.R'])
        rig_edit_bones['MCH-hand_fk.R'].use_connect = False
        rig_edit_bones['MCH-hand_fk.R'].parent = wrist_twist_fk_r_bone

        return wrist_twist_fk_l_bone, wrist_twist_fk_r_bone

    def _add_leg_ik_parent_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        # add Leg IKP (足IK親) bone
        leg_ik_parent_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_leg_ik_parent.L')
        leg_ik_parent_l_bone.layers = [i in {15} for i in range(32)]
        leg_ik_parent_l_bone.tail = rig_edit_bones['ORG-foot.L'].head
        leg_ik_parent_l_bone.head = leg_ik_parent_l_bone.tail.copy()
        leg_ik_parent_l_bone.head.z = rig_edit_bones['ORG-foot.L'].tail.z
        leg_ik_parent_l_bone.roll = 0

        if 'MCH-foot_ik.parent.L' in rig_edit_bones:
            leg_ik_parent_l_bone.parent = rig_edit_bones['MCH-foot_ik.parent.L']
        else:
            leg_ik_parent_l_bone.parent = rig_edit_bones['root']
        rig_edit_bones['foot_ik.L'].parent = leg_ik_parent_l_bone

        leg_ik_parent_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_leg_ik_parent.R')
        leg_ik_parent_r_bone.layers = [i in {18} for i in range(32)]
        leg_ik_parent_r_bone.tail = rig_edit_bones['ORG-foot.R'].head
        leg_ik_parent_r_bone.head = leg_ik_parent_r_bone.tail.copy()
        leg_ik_parent_r_bone.head.z = rig_edit_bones['ORG-foot.R'].tail.z
        leg_ik_parent_r_bone.roll = 0

        if 'MCH-foot_ik.parent.R' in rig_edit_bones:
            leg_ik_parent_r_bone.parent = rig_edit_bones['MCH-foot_ik.parent.R']
        else:
            leg_ik_parent_r_bone.parent = rig_edit_bones['root']
        rig_edit_bones['foot_ik.R'].parent = leg_ik_parent_r_bone

        return leg_ik_parent_l_bone, leg_ik_parent_r_bone

    def _add_toe_ik_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        # add toe IK (つま先ＩＫ)
        toe_ik_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_toe_ik.L')
        toe_ik_l_bone.layers = [i in {15} for i in range(32)]
        toe_ik_l_bone.head = rig_edit_bones['ORG-foot.L'].tail
        toe_ik_l_bone.tail = toe_ik_l_bone.head - Vector([0, 0, rig_edit_bones['mmd_uuunyaa_leg_ik_parent.L'].length])
        toe_ik_l_bone.parent = rig_edit_bones['foot_ik.L']
        self.fit_edit_bone_rotation(toe_ik_l_bone, rig_edit_bones['foot_ik.L'])

        toe_ik_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_toe_ik.R')
        toe_ik_r_bone.layers = [i in {18} for i in range(32)]
        toe_ik_r_bone.head = rig_edit_bones['ORG-foot.R'].tail
        toe_ik_r_bone.tail = toe_ik_r_bone.head - Vector([0, 0, rig_edit_bones['mmd_uuunyaa_leg_ik_parent.R'].length])
        toe_ik_r_bone.parent = rig_edit_bones['foot_ik.R']
        self.fit_edit_bone_rotation(toe_ik_r_bone, rig_edit_bones['foot_ik.R'])

        return toe_ik_l_bone, toe_ik_r_bone

    def _add_eye_fk_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone, bpy.types.EditBone):
        rig_eyes_fk_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_eyes_fk')
        rig_eyes_fk_bone.head = rig_edit_bones['ORG-spine.006'].tail + rig_edit_bones['ORG-spine.006'].vector
        rig_eyes_fk_bone.head.y = rig_edit_bones['ORG-eye.L'].head.y
        rig_eyes_fk_bone.tail = rig_eyes_fk_bone.head - Vector([0, rig_edit_bones['ORG-eye.L'].length * 2, 0])
        rig_eyes_fk_bone.layers = [i in {0} for i in range(32)]
        rig_eyes_fk_bone.parent = rig_edit_bones['ORG-face']
        self.fit_edit_bone_rotation(rig_eyes_fk_bone, rig_edit_bones['master_eye.L'])

        rig_eye_fk_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_eye_fk.L')
        rig_eye_fk_l_bone.head = rig_edit_bones['master_eye.L'].head
        rig_eye_fk_l_bone.tail = rig_edit_bones['master_eye.L'].tail
        rig_eye_fk_l_bone.layers = [i in {0} for i in range(32)]
        rig_eye_fk_l_bone.parent = rig_edit_bones['ORG-face']
        self.fit_edit_bone_rotation(rig_eye_fk_l_bone, rig_edit_bones['master_eye.L'])

        rig_eye_fk_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_eye_fk.R')
        rig_eye_fk_r_bone.head = rig_edit_bones['master_eye.R'].head
        rig_eye_fk_r_bone.tail = rig_edit_bones['master_eye.R'].tail
        rig_eye_fk_r_bone.layers = [i in {0} for i in range(32)]
        rig_eye_fk_r_bone.parent = rig_edit_bones['ORG-face']
        self.fit_edit_bone_rotation(rig_eye_fk_r_bone, rig_edit_bones['master_eye.R'])

        return rig_eye_fk_l_bone, rig_eye_fk_r_bone, rig_eyes_fk_bone

    def _adjust_torso_bone(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> bpy.types.EditBone:
        thigh_center = self.to_center(rig_edit_bones['ORG-thigh.L'].head, rig_edit_bones['ORG-thigh.R'].head)
        length = (rig_edit_bones['ORG-spine'].tail.z - thigh_center.z) / 2
        rig_edit_bones['torso'].head = Vector([0, rig_edit_bones['ORG-spine'].tail.y + length, thigh_center.z + length])
        rig_edit_bones['torso'].tail = rig_edit_bones['ORG-spine'].tail
        rig_edit_bones['torso'].roll = 0

        return rig_edit_bones['torso']

    def _add_root_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        # add center (センター) bone
        thigh_center = self.to_center(rig_edit_bones['ORG-thigh.L'].head, rig_edit_bones['ORG-thigh.L'].head)

        center_bone = self.get_or_create_bone(rig_edit_bones, 'center')
        center_bone.layers = [i in {28} for i in range(32)]
        center_bone.head = Vector([0.0, 0.0, thigh_center.z * 0.7])
        center_bone.tail = Vector([0.0, 0.0, 0.0])
        center_bone.roll = 0

        # add groove (グルーブ) bone
        groove_bone = self.get_or_create_bone(rig_edit_bones, 'groove')
        groove_bone.layers = [i in {28} for i in range(32)]
        groove_bone.head = center_bone.head
        groove_bone.tail = groove_bone.head + Vector([0.0, 0.0, center_bone.length/6])
        groove_bone.roll = 0

        return center_bone, groove_bone

    def _add_shoulder_parent_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        shoulder_parent_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_parent.L')
        shoulder_parent_l_bone.head = rig_edit_bones['ORG-shoulder.L'].head
        shoulder_parent_l_bone.tail = shoulder_parent_l_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.L'].length/2])
        shoulder_parent_l_bone.layers = [i in {8} for i in range(32)]
        shoulder_parent_l_bone.parent = rig_edit_bones['ORG-spine.003']
        rig_edit_bones['shoulder.L'].parent = shoulder_parent_l_bone
        shoulder_parent_l_bone.roll = 0

        shoulder_parent_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_parent.R')
        shoulder_parent_r_bone.head = rig_edit_bones['ORG-shoulder.R'].head
        shoulder_parent_r_bone.tail = shoulder_parent_r_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.R'].length/2])
        shoulder_parent_r_bone.layers = [i in {11} for i in range(32)]
        shoulder_parent_r_bone.parent = rig_edit_bones['ORG-spine.003']
        rig_edit_bones['shoulder.R'].parent = shoulder_parent_r_bone
        shoulder_parent_r_bone.roll = 0

        return shoulder_parent_l_bone, shoulder_parent_r_bone

    def _add_shoulder_cancel_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        shoulder_cancel_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_cancel.L')
        shoulder_cancel_l_bone.head = rig_edit_bones['ORG-shoulder.L'].tail
        shoulder_cancel_l_bone.tail = shoulder_cancel_l_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.L'].length/2])
        shoulder_cancel_l_bone.layers = [i in {8} for i in range(32)]
        self.insert_edit_bone(shoulder_cancel_l_bone, parent_bone=rig_edit_bones['ORG-shoulder.L'])
        shoulder_cancel_l_bone.roll = 0

        shoulder_cancel_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_cancel.R')
        shoulder_cancel_r_bone.head = rig_edit_bones['ORG-shoulder.R'].tail
        shoulder_cancel_r_bone.tail = shoulder_cancel_r_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.R'].length/2])
        shoulder_cancel_r_bone.layers = [i in {11} for i in range(32)]
        self.insert_edit_bone(shoulder_cancel_r_bone, parent_bone=rig_edit_bones['ORG-shoulder.R'])
        shoulder_cancel_r_bone.roll = 0

        return shoulder_cancel_l_bone, shoulder_cancel_r_bone

    def _add_shoulder_cancel_dummy_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        shoulder_cancel_dummy_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_cancel_dummy.L')
        shoulder_cancel_dummy_l_bone.head = rig_edit_bones['ORG-shoulder.L'].head
        shoulder_cancel_dummy_l_bone.tail = shoulder_cancel_dummy_l_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.L'].length/2])
        shoulder_cancel_dummy_l_bone.layers = [i in {27} for i in range(32)]
        shoulder_cancel_dummy_l_bone.parent = rig_edit_bones['mmd_uuunyaa_shoulder_parent.L']
        shoulder_cancel_dummy_l_bone.roll = 0

        shoulder_cancel_dummy_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_cancel_dummy.R')
        shoulder_cancel_dummy_r_bone.head = rig_edit_bones['ORG-shoulder.R'].head
        shoulder_cancel_dummy_r_bone.tail = shoulder_cancel_dummy_r_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.R'].length/2])
        shoulder_cancel_dummy_r_bone.layers = [i in {27} for i in range(32)]
        shoulder_cancel_dummy_r_bone.parent = rig_edit_bones['mmd_uuunyaa_shoulder_parent.R']
        shoulder_cancel_dummy_r_bone.roll = 0

        return shoulder_cancel_dummy_l_bone, shoulder_cancel_dummy_r_bone

    def _add_shoulder_cancel_shadow_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones) -> (bpy.types.EditBone, bpy.types.EditBone):
        shoulder_cancel_shadow_l_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_cancel_shadow.L')
        shoulder_cancel_shadow_l_bone.head = rig_edit_bones['ORG-shoulder.L'].head
        shoulder_cancel_shadow_l_bone.tail = shoulder_cancel_shadow_l_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.L'].length/2])
        shoulder_cancel_shadow_l_bone.layers = [i in {26} for i in range(32)]
        shoulder_cancel_shadow_l_bone.parent = rig_edit_bones['ORG-spine.003']
        shoulder_cancel_shadow_l_bone.roll = 0

        shoulder_cancel_shadow_r_bone = self.get_or_create_bone(rig_edit_bones, 'mmd_uuunyaa_shoulder_cancel_shadow.R')
        shoulder_cancel_shadow_r_bone.head = rig_edit_bones['ORG-shoulder.R'].head
        shoulder_cancel_shadow_r_bone.tail = shoulder_cancel_shadow_r_bone.head + Vector([0, 0, rig_edit_bones['ORG-shoulder.R'].length/2])
        shoulder_cancel_shadow_r_bone.layers = [i in {26} for i in range(32)]
        shoulder_cancel_shadow_r_bone.parent = rig_edit_bones['ORG-spine.003']
        shoulder_cancel_shadow_r_bone.roll = 0

        return shoulder_cancel_shadow_l_bone, shoulder_cancel_shadow_r_bone

    def _adjust_leg_bones(self, rig_edit_bones: bpy.types.ArmatureEditBones):
        rig_edit_bones['thigh_fk.L'].layers = list(map(any, zip(rig_edit_bones['thigh_ik.L'].layers, rig_edit_bones['thigh_fk.L'].layers)))
        rig_edit_bones['thigh_fk.R'].layers = list(map(any, zip(rig_edit_bones['thigh_ik.R'].layers, rig_edit_bones['thigh_fk.R'].layers)))

    def imitate_mmd_bone_structure(self, _: MMDArmatureObject):
        # pylint: disable=too-many-statements
        rig_edit_bones = self.edit_bones

        # add center (センター) groove (グルーブ) bone
        center_bone, groove_bone = self._add_root_bones(rig_edit_bones)

        # set spine parent-child relationship
        if 'MCH-torso.parent' in rig_edit_bones:
            spine_root_bone = rig_edit_bones['MCH-torso.parent']
        else:
            spine_root_bone = rig_edit_bones['root']

        center_bone.parent = spine_root_bone
        groove_bone.parent = center_bone
        rig_edit_bones['torso'].parent = groove_bone

        self._add_shoulder_parent_bones(rig_edit_bones)
        self._add_shoulder_cancel_bones(rig_edit_bones)
        self._add_shoulder_cancel_dummy_bones(rig_edit_bones)
        self._add_shoulder_cancel_shadow_bones(rig_edit_bones)

        self._add_upper_arm_twist_bones(rig_edit_bones)

        self._add_wrist_twist_bones(rig_edit_bones)

        self._add_leg_ik_parent_bones(rig_edit_bones)

        self._add_toe_ik_bones(rig_edit_bones)

        # add spine fk bones
        spine_fk_bone = self.get_or_create_bone(rig_edit_bones, 'spine_fk')
        spine_fk_bone.layers = [i in {4} for i in range(32)]
        spine_fk_bone.head = rig_edit_bones['ORG-spine'].tail
        spine_fk_bone.tail = rig_edit_bones['ORG-spine'].tail + rig_edit_bones['ORG-spine'].vector
        spine_fk_bone.roll = 0
        self.insert_edit_bone(spine_fk_bone, parent_bone=rig_edit_bones['MCH-spine'])

        spine_fk_001_bone = self.get_or_create_bone(rig_edit_bones, 'spine_fk.001')
        spine_fk_001_bone.layers = [i in {4} for i in range(32)]
        spine_fk_001_bone.head = rig_edit_bones['ORG-spine.001'].tail
        spine_fk_001_bone.tail = rig_edit_bones['ORG-spine.001'].tail + rig_edit_bones['ORG-spine.001'].vector
        spine_fk_001_bone.roll = 0
        self.insert_edit_bone(spine_fk_001_bone, parent_bone=rig_edit_bones['MCH-spine.001'])

        spine_fk_002_bone = self.get_or_create_bone(rig_edit_bones, 'spine_fk.002')
        spine_fk_002_bone.layers = [i in {4} for i in range(32)]
        spine_fk_002_bone.head = rig_edit_bones['ORG-spine.002'].head
        spine_fk_002_bone.tail = rig_edit_bones['ORG-spine.002'].tail
        spine_fk_002_bone.roll = 0
        self.insert_edit_bone(spine_fk_002_bone, parent_bone=rig_edit_bones['MCH-spine.002'])

        spine_fk_003_bone = self.get_or_create_bone(rig_edit_bones, 'spine_fk.003')
        spine_fk_003_bone.layers = [i in {4} for i in range(32)]
        spine_fk_003_bone.head = rig_edit_bones['ORG-spine.003'].head
        spine_fk_003_bone.tail = rig_edit_bones['ORG-spine.003'].tail
        spine_fk_003_bone.roll = 0
        self.insert_edit_bone(spine_fk_003_bone, parent_bone=rig_edit_bones['MCH-spine.003'])

        # split spine.001 (上半身) and spine (下半身) bones
        rig_edit_bones['ORG-spine.001'].use_connect = False
        rig_edit_bones['DEF-spine.001'].use_connect = False

        rig_edit_bones['MCH-spine'].parent = rig_edit_bones['torso']
        rig_edit_bones['MCH-spine.002'].parent = rig_edit_bones['spine_fk.001']

        def move_bone(edit_bone: bpy.types.EditBone, head: Vector = None, tail: Vector = None):
            vector: Vector = edit_bone.vector
            if head is not None:
                edit_bone.head = head
                edit_bone.tail = head + vector
            elif tail is not None:
                edit_bone.head = tail - vector
                edit_bone.tail = tail

        move_bone(rig_edit_bones['tweak_spine.001'], head=rig_edit_bones['ORG-spine.001'].head)
        move_bone(rig_edit_bones['spine_fk.001'], head=rig_edit_bones['ORG-spine.001'].head)
        move_bone(rig_edit_bones['MCH-spine.001'], head=rig_edit_bones['ORG-spine.001'].head)
        move_bone(rig_edit_bones['chest'], head=rig_edit_bones['ORG-spine.001'].head)

        move_bone(rig_edit_bones['hips'], head=rig_edit_bones['ORG-spine'].tail)

        # adjust torso bone
        self._adjust_torso_bone(rig_edit_bones)

        # adjust leg bones
        self._adjust_leg_bones(rig_edit_bones)

        # set face bones
        if not self.has_face_bones():
            # There are not enough bones for the setup.
            return

        self._add_eye_fk_bones(rig_edit_bones)

    def imitate_mmd_pose_behavior(self):
        """Imitate the behavior of MMD armature as much as possible."""
        # pylint: disable=too-many-statements

        pose_bones: Dict[str, bpy.types.PoseBone] = self.pose_bones

        self.create_props(pose_bones[self.prop_storage_bone_name])
        self.remove_constraints(pose_bones)

        self._imitate_mmd_eye_behavior(pose_bones)

        def list_constraints(pose_bone: bpy.types.PoseBone, constraint_type: str) -> Iterable[bpy.types.Constraint]:
            for constraint in pose_bone.constraints:
                if constraint.type == constraint_type:
                    yield constraint

        def edit_constraints(pose_bone: bpy.types.PoseBone, constraint_type: str, **kwargs):
            for constraint in list_constraints(pose_bone, constraint_type):
                for key, value in kwargs.items():
                    setattr(constraint, key, value)

        def add_constraint(pose_bone: bpy.types.PoseBone, constraint_type: str, name: str, **kwargs) -> bpy.types.Constraint:
            constraints = pose_bone.constraints
            constraint = constraints.new(constraint_type)
            constraint.name = name
            for key, value in kwargs.items():
                setattr(constraint, key, value)
            return constraint

        # set spine
        edit_constraints(pose_bones['MCH-pivot'], 'COPY_TRANSFORMS', influence=0.000)
        edit_constraints(pose_bones['ORG-spine.001'], 'COPY_TRANSFORMS', subtarget='spine_fk.001')

        # reset rest_length
        # https://blenderartists.org/t/resetting-stretch-to-constraints-via-python/650628
        edit_constraints(pose_bones['ORG-spine'], 'STRETCH_TO', rest_length=0.000)
        edit_constraints(pose_bones['ORG-spine.001'], 'STRETCH_TO', rest_length=0.000)
        edit_constraints(pose_bones['ORG-spine.002'], 'STRETCH_TO', rest_length=0.000)
        edit_constraints(pose_bones['ORG-spine.003'], 'STRETCH_TO', rest_length=0.000)

        # shoulders
        add_constraint(
            pose_bones['mmd_uuunyaa_shoulder_cancel_shadow.L'],
            'COPY_TRANSFORMS', 'mmd_uuunyaa_transform_shoulder_cancel',
            target=self.raw_object, subtarget='mmd_uuunyaa_shoulder_cancel_dummy.L',
            target_space='POSE', owner_space='POSE'
        )

        add_constraint(
            pose_bones['mmd_uuunyaa_shoulder_cancel_shadow.R'],
            'COPY_TRANSFORMS', 'mmd_uuunyaa_transform_shoulder_cancel',
            target=self.raw_object, subtarget='mmd_uuunyaa_shoulder_cancel_dummy.R',
            target_space='POSE', owner_space='POSE'
        )

        add_constraint(
            pose_bones['mmd_uuunyaa_shoulder_cancel.L'],
            'TRANSFORM', 'mmd_uuunyaa_transform_shoulder_cancel',
            target=self.raw_object, subtarget='mmd_uuunyaa_shoulder_cancel_shadow.L',
            map_from='ROTATION', map_to='ROTATION',
            from_min_x_rot=math.radians(-180), to_min_x_rot=math.radians(+180),
            from_max_x_rot=math.radians(+180), to_max_x_rot=math.radians(-180),
            from_min_y_rot=math.radians(-180), to_min_y_rot=math.radians(+180),
            from_max_y_rot=math.radians(+180), to_max_y_rot=math.radians(-180),
            from_min_z_rot=math.radians(-180), to_min_z_rot=math.radians(+180),
            from_max_z_rot=math.radians(+180), to_max_z_rot=math.radians(-180),
            target_space='LOCAL', owner_space='LOCAL'
        )

        add_constraint(
            pose_bones['mmd_uuunyaa_shoulder_cancel.R'],
            'TRANSFORM', 'mmd_uuunyaa_transform_shoulder_cancel',
            target=self.raw_object, subtarget='mmd_uuunyaa_shoulder_cancel_shadow.R',
            map_from='ROTATION', map_to='ROTATION',
            from_min_x_rot=math.radians(-180), to_min_x_rot=math.radians(+180),
            from_max_x_rot=math.radians(+180), to_max_x_rot=math.radians(-180),
            from_min_y_rot=math.radians(-180), to_min_y_rot=math.radians(+180),
            from_max_y_rot=math.radians(+180), to_max_y_rot=math.radians(-180),
            from_min_z_rot=math.radians(-180), to_min_z_rot=math.radians(+180),
            from_max_z_rot=math.radians(+180), to_max_z_rot=math.radians(-180),
            target_space='LOCAL', owner_space='LOCAL'
        )

        bones = self.bones
        bones['mmd_uuunyaa_shoulder_cancel.L'].hide = True
        bones['mmd_uuunyaa_shoulder_cancel.R'].hide = True

        # arms
        pose_bones['mmd_uuunyaa_upper_arm_twist_fk.L'].lock_location = [True, True, True]
        pose_bones['mmd_uuunyaa_upper_arm_twist_fk.L'].lock_rotation_w = False
        pose_bones['mmd_uuunyaa_upper_arm_twist_fk.L'].lock_rotation = [True, False, True]

        pose_bones['mmd_uuunyaa_upper_arm_twist_fk.R'].lock_location = [True, True, True]
        pose_bones['mmd_uuunyaa_upper_arm_twist_fk.R'].lock_rotation_w = False
        pose_bones['mmd_uuunyaa_upper_arm_twist_fk.R'].lock_rotation = [True, False, True]

        # wrists
        pose_bones['mmd_uuunyaa_wrist_twist_fk.L'].lock_location = [True, True, True]
        pose_bones['mmd_uuunyaa_wrist_twist_fk.L'].lock_rotation_w = False
        pose_bones['mmd_uuunyaa_wrist_twist_fk.L'].lock_rotation = [True, False, True]

        pose_bones['mmd_uuunyaa_wrist_twist_fk.R'].lock_location = [True, True, True]
        pose_bones['mmd_uuunyaa_wrist_twist_fk.R'].lock_rotation_w = False
        pose_bones['mmd_uuunyaa_wrist_twist_fk.R'].lock_rotation = [True, False, True]

        # fingers
        for pose_bone_name in [
            'thumb.02.R', 'thumb.03.R', 'thumb.02.L', 'thumb.03.L',
            'f_index.02.R', 'f_index.03.R', 'f_index.02.L', 'f_index.03.L',
            'f_middle.02.R', 'f_middle.03.R', 'f_middle.02.L', 'f_middle.03.L',
            'f_ring.02.R', 'f_ring.03.R', 'f_ring.02.L', 'f_ring.03.L',
            'f_pinky.02.R', 'f_pinky.03.R', 'f_pinky.02.L', 'f_pinky.03.L',
        ]:
            edit_constraints(pose_bones[pose_bone_name], 'COPY_ROTATION', mute=True)

        # legs
        def bind_fk2ik(from_bone_name: str, ik_bone_name: str, cotrol_data_path: str):
            add_influence_driver(
                add_constraint(
                    pose_bones[ik_bone_name],
                    'COPY_TRANSFORMS',
                    'mmd_uuunyaa_copy_transforms',
                    target=self.raw_object,
                    subtarget=from_bone_name,
                    target_space='LOCAL',
                    owner_space='LOCAL'
                ),
                self.raw_object,
                cotrol_data_path,
                invert=True
            )

        leg_l_mmd_uuunyaa_data_path = f'pose.bones{self.datapaths[ControlType.LEG_L_MMD_UUUNYAA].data_path}'
        bind_fk2ik('thigh_fk.L', 'thigh_ik.L', leg_l_mmd_uuunyaa_data_path)
        bind_fk2ik('shin_fk.L', 'MCH-shin_ik.L', leg_l_mmd_uuunyaa_data_path)
        bind_fk2ik('foot_fk.L', 'MCH-thigh_ik_target.L', leg_l_mmd_uuunyaa_data_path)

        shin_ik_l_bone = pose_bones['MCH-shin_ik.L'] if 'MCH-shin_ik.L' in pose_bones else pose_bones['MCH-thigh_ik.L']
        edit_constraints(shin_ik_l_bone, 'IK', iterations=200)
        shin_ik_l_bone.use_ik_limit_x = True
        shin_ik_l_bone.ik_min_x = math.radians(0)
        shin_ik_l_bone.ik_max_x = math.radians(180)

        leg_r_mmd_uuunyaa_data_path = f'pose.bones{self.datapaths[ControlType.LEG_R_MMD_UUUNYAA].data_path}'
        bind_fk2ik('thigh_fk.R', 'thigh_ik.R', leg_r_mmd_uuunyaa_data_path)
        bind_fk2ik('shin_fk.R', 'MCH-shin_ik.R', leg_r_mmd_uuunyaa_data_path)
        bind_fk2ik('foot_fk.R', 'MCH-thigh_ik_target.R', leg_r_mmd_uuunyaa_data_path)

        shin_ik_r_bone = pose_bones['MCH-shin_ik.R'] if 'MCH-shin_ik.R' in pose_bones else pose_bones['MCH-thigh_ik.R']
        edit_constraints(shin_ik_r_bone, 'IK', iterations=200)
        shin_ik_r_bone.use_ik_limit_x = True
        shin_ik_r_bone.ik_min_x = math.radians(0)
        shin_ik_r_bone.ik_max_x = math.radians(180)

        # toe IK
        leg_l_ik_fk_data_path = f'pose.bones{self.datapaths[ControlType.LEG_L_IK_FK].data_path}'
        leg_r_ik_fk_data_path = f'pose.bones{self.datapaths[ControlType.LEG_R_IK_FK].data_path}'
        self.create_mmd_ik_constraint(pose_bones['ORG-foot.L'], 'mmd_uuunyaa_toe_ik.L', leg_l_ik_fk_data_path, 1, 3)
        self.create_mmd_ik_constraint(pose_bones['ORG-foot.R'], 'mmd_uuunyaa_toe_ik.R', leg_r_ik_fk_data_path, 1, 3)

        self._set_bone_custom_shapes(pose_bones)

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
        self.leg_l_ik_stretch = 0.000
        self.leg_r_ik_stretch = 0.000
        self.leg_l_ik_parent = 1  # root
        self.leg_r_ik_parent = 1  # root
        self.leg_l_pole_vector = 0  # disable
        self.leg_r_pole_vector = 0  # disable
        self.leg_l_pole_parent = 2  # torso
        self.leg_r_pole_parent = 2  # torso

        # set bind mode
        self.bind_mmd_rigify = 1.000  # Bind

        # set eye motion mode
        self.eye_mmd_rigify = 0.000  # MMD

        # set toe fix mode
        self.toe_l_mmd_rigify = 0.000  # MMD
        self.toe_r_mmd_rigify = 0.000  # MMD

        # torso hack
        self.torso_neck_follow = 1.000  # follow chest
        self.torso_head_follow = 1.000  # follow chest

    def _set_bone_custom_shapes(self, pose_bones: Dict[str, bpy.types.PoseBone]):

        bone_widgets = [
            ('center', 'WGT-Root.Round.', 10.0, 'Root'),
            ('groove', 'WGT-Root.2Way', 20.0, 'Root'),
            ('torso', 'WGT-rig_torso', 2.5, 'Special'),
            ('spine_fk', 'WGT-rig_spine_fk', 1.0, 'Tweak'),
            ('spine_fk.001', 'WGT-rig_spine_fk.002', 1.0, 'Tweak'),
            ('spine_fk.002', 'WGT-rig_spine_fk.002', 1.0, 'Tweak'),
            ('spine_fk.003', 'WGT-rig_spine_fk.003', 1.0, 'Tweak'),
            ('mmd_uuunyaa_shoulder_parent.L', 'WGT-rig_upper_arm_tweak.L', 0.5, 'Tweak'),
            ('mmd_uuunyaa_shoulder_parent.R', 'WGT-rig_upper_arm_tweak.R', 0.5, 'Tweak'),
            ('mmd_uuunyaa_upper_arm_twist_fk.L', 'WGT-rig_upper_arm_fk.L', 1.0, 'Tweak'),
            ('mmd_uuunyaa_upper_arm_twist_fk.R', 'WGT-rig_upper_arm_fk.R', 1.0, 'Tweak'),
            ('mmd_uuunyaa_wrist_twist_fk.L', 'WGT-rig_forearm_fk.L', 1.0, 'Tweak'),
            ('mmd_uuunyaa_wrist_twist_fk.R', 'WGT-rig_forearm_fk.R', 1.0, 'Tweak'),
            ('mmd_uuunyaa_leg_ik_parent.L', 'WGT-Bowl.Horizontal.001', 20.0, 'Tweak'),
            ('mmd_uuunyaa_leg_ik_parent.R', 'WGT-Bowl.Horizontal.001', 20.0, 'Tweak'),
            ('mmd_uuunyaa_toe_ik.L', 'WGT-Visor.Wide', 1.0, 'Tweak'),
            ('mmd_uuunyaa_toe_ik.R', 'WGT-Visor.Wide', 1.0, 'Tweak'),
        ]

        rig_bone_groups = self.pose_bone_groups

        # add Rigify bone groups
        # see: https://github.com/sobotka/blender-addons/blob/master/rigify/metarigs/human.py

        if 'Root' not in rig_bone_groups:
            bone_group = rig_bone_groups.new(name='Root')
            bone_group.color_set = 'CUSTOM'
            bone_group.colors.normal = Color((0.4352940022945404, 0.18431399762630463, 0.4156860113143921))
            bone_group.colors.select = Color((0.31372547149658203, 0.7843138575553894, 1.0))
            bone_group.colors.active = Color((0.5490196347236633, 1.0, 1.0))

        if 'Special' not in rig_bone_groups:
            bone_group = rig_bone_groups.new(name='Special')
            bone_group.color_set = 'CUSTOM'
            bone_group.colors.normal = Color((0.9568629860877991, 0.7882350087165833, 0.04705899953842163))
            bone_group.colors.select = Color((0.31372547149658203, 0.7843138575553894, 1.0))
            bone_group.colors.active = Color((0.5490196347236633, 1.0, 1.0))

        if 'Tweak' not in rig_bone_groups:
            bone_group = rig_bone_groups.new(name='Tweak')
            bone_group.color_set = 'CUSTOM'
            bone_group.colors.normal = Color((0.03921600058674812, 0.21176500618457794, 0.5803920030593872))
            bone_group.colors.select = Color((0.31372547149658203, 0.7843138575553894, 1.0))
            bone_group.colors.active = Color((0.5490196347236633, 1.0, 1.0))

        if 'FK' not in rig_bone_groups:
            bone_group = rig_bone_groups.new(name='FK')
            bone_group.color_set = 'CUSTOM'
            bone_group.colors.normal = Color((0.11764699965715408, 0.5686269998550415, 0.035294000059366226))
            bone_group.colors.select = Color((0.31372547149658203, 0.7843138575553894, 1.0))
            bone_group.colors.active = Color((0.5490196347236633, 1.0, 1.0))

        insufficient_custom_shapes = list({custom_shape_name for _, custom_shape_name, _, _ in bone_widgets} - set(bpy.data.objects.keys()))
        if len(insufficient_custom_shapes) > 0:
            with bpy.data.libraries.load(PATH_BLENDS_RIGSHAPELIBRARY, link=False) as (_, data_to):
                data_to.objects = insufficient_custom_shapes

        for bone_name, custom_shape_name, custom_shape_scale, bone_group_name in bone_widgets:
            pose_bones[bone_name].custom_shape = bpy.data.objects[custom_shape_name]
            pose_bones[bone_name].custom_shape_scale = custom_shape_scale
            pose_bones[bone_name].bone_group = rig_bone_groups[bone_group_name]

        if not self.has_face_bones():
            return

        pose_bones['mmd_uuunyaa_eyes_fk'].bone_group = rig_bone_groups['FK']
        pose_bones['mmd_uuunyaa_eye_fk.L'].bone_group = rig_bone_groups['FK']
        pose_bones['mmd_uuunyaa_eye_fk.R'].bone_group = rig_bone_groups['FK']

    def _imitate_mmd_eye_behavior(self, pose_bones: Dict[str, bpy.types.PoseBone]):
        if not self.has_face_bones():
            return

        eye_mmd_rigify = self.datapaths[ControlType.EYE_MMD_UUUNYAA]

        def create_mmd_rotation_constraint(rig_bone: bpy.types.PoseBone, subtarget: str, influence_data_path: str) -> bpy.types.Constraint:
            constraint = rig_bone.constraints.new('COPY_ROTATION')
            constraint.name = 'mmd_uuunyaa_copy_rotation_mmd'
            constraint.target = self.raw_object
            constraint.subtarget = subtarget
            constraint.target_space = 'LOCAL'
            constraint.owner_space = 'LOCAL'
            add_influence_driver(constraint, self.raw_object, influence_data_path, invert=True)
            return constraint

        create_mmd_rotation_constraint(pose_bones['MCH-eye.L'], 'mmd_uuunyaa_eye_fk.L', f'pose.bones{eye_mmd_rigify.data_path}')
        create_mmd_rotation_constraint(pose_bones['MCH-eye.R'], 'mmd_uuunyaa_eye_fk.R', f'pose.bones{eye_mmd_rigify.data_path}')
        create_mmd_rotation_constraint(pose_bones['mmd_uuunyaa_eye_fk.L'], 'mmd_uuunyaa_eyes_fk', f'pose.bones{eye_mmd_rigify.data_path}').mix_mode = 'ADD'
        create_mmd_rotation_constraint(pose_bones['mmd_uuunyaa_eye_fk.R'], 'mmd_uuunyaa_eyes_fk', f'pose.bones{eye_mmd_rigify.data_path}').mix_mode = 'ADD'

    def pose_mmd_rest(self, dependency_graph: bpy.types.Depsgraph, iterations: int, pose_arms: bool, pose_legs: bool, pose_fingers: bool):
        # pylint: disable=too-many-arguments
        pose_bones = self.pose_bones

        self.arm_l_ik_fk = 1.000  # use FK
        self.arm_r_ik_fk = 1.000  # use FK
        self.leg_l_ik_fk = 0.000  # use IK
        self.leg_r_ik_fk = 0.000  # use IK

        def set_rotation(pose_bone: bpy.types.PoseBone, rotation_matrix: Matrix):
            pose_bone.matrix = Matrix.Translation(pose_bone.matrix.to_translation()) @ rotation_matrix

        def to_rotation_matrix(pose_bone: bpy.types.PoseBone) -> Matrix:
            return pose_bone.matrix.to_euler().to_matrix().to_4x4()

        arm_l_target_rotation = Euler([math.radians(+90), math.radians(+123), math.radians(0)]).to_matrix().to_4x4()
        arm_r_target_rotation = Euler([math.radians(+90), math.radians(-123), math.radians(0)]).to_matrix().to_4x4()

        for _ in range(iterations):
            if pose_arms:
                # arm.L
                for bone_name in ['upper_arm_fk.L', 'forearm_fk.L', 'hand_fk.L', ]:
                    set_rotation(pose_bones[bone_name], arm_l_target_rotation)

                # arm.R
                for bone_name in ['upper_arm_fk.R', 'forearm_fk.R', 'hand_fk.R', ]:
                    set_rotation(pose_bones[bone_name], arm_r_target_rotation)

            if pose_legs:
                # foot.L
                pose_bones['mmd_uuunyaa_leg_ik_parent.L'].matrix = (
                    pose_bones['mmd_uuunyaa_leg_ik_parent.L'].matrix
                    @ Matrix.Translation(Vector([pose_bones['ORG-thigh.L'].head[0]-pose_bones['ORG-foot.L'].head[0], 0, 0]))
                )
                pose_bones['foot_ik.L'].matrix = (
                    pose_bones['foot_ik.L'].matrix
                    @ Matrix.Rotation(-pose_bones['ORG-foot.L'].matrix.to_euler().z, 4, 'Z')
                )

                # foot.R
                pose_bones['mmd_uuunyaa_leg_ik_parent.R'].matrix = (
                    pose_bones['mmd_uuunyaa_leg_ik_parent.R'].matrix
                    @ Matrix.Translation(Vector([pose_bones['ORG-thigh.R'].head[0]-pose_bones['ORG-foot.R'].head[0], 0, 0]))
                )
                pose_bones['foot_ik.R'].matrix = (
                    pose_bones['foot_ik.R'].matrix
                    @ Matrix.Rotation(-pose_bones['ORG-foot.R'].matrix.to_euler().z, 4, 'Z')
                )

            if pose_fingers:
                # finger.L
                target_rotation = to_rotation_matrix(pose_bones['f_middle.01.L'])
                for bone_name in [
                    'f_index.01.L', 'f_index.02.L', 'f_index.03.L',
                    'f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L',
                    'f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L',
                    'f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L',
                ]:
                    set_rotation(pose_bones[bone_name], target_rotation)

                # finger.R
                target_rotation = to_rotation_matrix(pose_bones['f_middle.01.R'])
                for bone_name in [
                    'f_index.01.R', 'f_index.02.R', 'f_index.03.R',
                    'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R',
                    'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R',
                    'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R',
                ]:
                    set_rotation(pose_bones[bone_name], target_rotation)

            dependency_graph.update()


class MMDRigifyArmatureObject(RigifyArmatureObject):
    @staticmethod
    def is_mmd_integrated_object(obj: bpy.types.Object):
        if not RigifyArmatureObject.is_rigify_armature_object(obj):
            return False

        if not MMDArmatureObject.is_mmd_armature_object(obj):
            return False

        pose_bones: Dict[str, bpy.types.PoseBone] = obj.pose.bones

        prop_storage_bone = pose_bones[RigifyArmatureObject.prop_storage_bone_name]
        if RigifyArmatureObject.prop_name_mmd_uuunyaa_bind_mmd_rigify not in prop_storage_bone:
            return False

        return True

    @classmethod
    def _fit_bone(cls, rig_edit_bone: bpy.types.EditBone, mmd_edit_bone: bpy.types.EditBone):
        rig_edit_bone.head = mmd_edit_bone.head
        rig_edit_bone.tail = mmd_edit_bone.tail
        cls.fit_edit_bone_rotation(mmd_edit_bone, rig_edit_bone)

    def imitate_mmd_bone_structure(self, mmd_armature_object: MMDArmatureObject):
        # pylint: disable=too-many-locals,too-many-statements
        rig_edit_bones: bpy.types.ArmatureEditBones = self.edit_bones
        mmd_edit_bones: bpy.types.ArmatureEditBones = mmd_armature_object.strict_edit_bones

        # add center (センター) groove (グルーブ) bone
        center_bone, groove_bone = self._add_root_bones(rig_edit_bones)
        self._fit_bone(center_bone, mmd_edit_bones['センター'])

        if MMDBoneType.GROOVE in mmd_armature_object.exist_bone_types:
            self._fit_bone(groove_bone, mmd_edit_bones['グルーブ'])
        else:
            groove_bone.head = mmd_edit_bones['センター'].head
            groove_bone.tail = groove_bone.head + Vector([0.0, 0.0, mmd_edit_bones['センター'].length/6])
            groove_bone.roll = 0

        # set spine parent-child relationship
        center_bone.parent = rig_edit_bones['MCH-torso.parent']
        groove_bone.parent = center_bone
        rig_edit_bones['torso'].parent = groove_bone

        # add shoulder parent, cancel (肩P, 肩C)
        shoulder_parent_l_bone, shoulder_parent_r_bone = self._add_shoulder_parent_bones(rig_edit_bones)
        shoulder_cancel_l_bone, shoulder_cancel_r_bone = self._add_shoulder_cancel_bones(rig_edit_bones)
        shoulder_cancel_dummy_l_bone, shoulder_cancel_dummy_r_bone = self._add_shoulder_cancel_dummy_bones(rig_edit_bones)
        shoulder_cancel_shadow_l_bone, shoulder_cancel_shadow_r_bone = self._add_shoulder_cancel_shadow_bones(rig_edit_bones)

        if MMDBoneType.SHOULDER_CANCEL in mmd_armature_object.exist_bone_types:
            self._fit_bone(shoulder_parent_l_bone, mmd_edit_bones['左肩P'])
            self._fit_bone(shoulder_parent_r_bone, mmd_edit_bones['右肩P'])

            self._fit_bone(shoulder_cancel_l_bone, mmd_edit_bones['左肩C'])
            self._fit_bone(shoulder_cancel_r_bone, mmd_edit_bones['右肩C'])

            self._fit_bone(shoulder_cancel_dummy_l_bone, mmd_edit_bones['左肩P'])
            self._fit_bone(shoulder_cancel_dummy_r_bone, mmd_edit_bones['右肩P'])

            self._fit_bone(shoulder_cancel_shadow_l_bone, mmd_edit_bones['左肩P'])
            self._fit_bone(shoulder_cancel_shadow_r_bone, mmd_edit_bones['右肩P'])

        # add arm twist (腕捩)
        upper_arm_twist_fk_l_bone, upper_arm_twist_fk_r_bone = self._add_upper_arm_twist_bones(rig_edit_bones)
        if MMDBoneType.UPPER_ARM_TWIST in mmd_armature_object.exist_bone_types:
            self._fit_bone(upper_arm_twist_fk_l_bone, mmd_edit_bones['左腕捩'])
            self._fit_bone(upper_arm_twist_fk_r_bone, mmd_edit_bones['右腕捩'])

        # add wrist twist (手捩)
        wrist_twist_fk_l_bone, wrist_twist_fk_r_bone = self._add_wrist_twist_bones(rig_edit_bones)
        if MMDBoneType.WRIST_TWIST in mmd_armature_object.exist_bone_types:
            self._fit_bone(wrist_twist_fk_l_bone, mmd_edit_bones['左手捩'])
            self._fit_bone(wrist_twist_fk_r_bone, mmd_edit_bones['右手捩'])

        # add Leg IKP (足IK親)
        leg_ik_parent_l_bone, leg_ik_parent_r_bone = self._add_leg_ik_parent_bones(rig_edit_bones)
        if MMDBoneType.LEG_IK_PARENT in mmd_armature_object.exist_bone_types:
            self._fit_bone(leg_ik_parent_l_bone, mmd_edit_bones['左足IK親'])
            self._fit_bone(leg_ik_parent_r_bone, mmd_edit_bones['右足IK親'])

        # add toe IK (つま先ＩＫ)
        toe_ik_l_bone, toe_ik_r_bone = self._add_toe_ik_bones(rig_edit_bones)
        self._fit_bone(toe_ik_l_bone, mmd_edit_bones['左つま先ＩＫ'])
        self._fit_bone(toe_ik_r_bone, mmd_edit_bones['右つま先ＩＫ'])

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
        rig_edit_bones['ORG-spine'].tail = mmd_edit_bones['下半身'].head
        rig_edit_bones['DEF-spine'].tail = mmd_edit_bones['下半身'].head

        rig_edit_bones['MCH-spine'].parent = rig_edit_bones['torso']
        rig_edit_bones['MCH-spine.002'].parent = rig_edit_bones['spine_fk.001']

        move_bone(rig_edit_bones['tweak_spine.001'], head=mmd_edit_bones['上半身'].head)
        move_bone(rig_edit_bones['spine_fk.001'], head=mmd_edit_bones['上半身'].head)
        move_bone(rig_edit_bones['MCH-spine.001'], head=mmd_edit_bones['上半身'].head)
        move_bone(rig_edit_bones['chest'], head=mmd_edit_bones['上半身'].head)

        rig_edit_bones['ORG-spine'].tail = mmd_edit_bones['下半身'].head
        rig_edit_bones['DEF-spine'].tail = mmd_edit_bones['下半身'].head
        move_bone(rig_edit_bones['spine_fk'], head=mmd_edit_bones['下半身'].head)
        move_bone(rig_edit_bones['MCH-spine'], head=mmd_edit_bones['下半身'].head)
        move_bone(rig_edit_bones['hips'], head=mmd_edit_bones['下半身'].head)

        # adjust torso
        torso_bone = self._adjust_torso_bone(rig_edit_bones)
        if MMDBoneType.TOLSO in mmd_armature_object.exist_bone_types:
            torso_bone.head = mmd_edit_bones['腰'].head
            torso_bone.tail = mmd_edit_bones['腰'].tail
            self.fit_edit_bone_rotation(mmd_edit_bones['腰'], torso_bone)

        # adjust leg bones
        self._adjust_leg_bones(rig_edit_bones)

        # set face bones
        if not self.has_face_bones():
            # There are not enough bones for the setup.
            return

        eye_height_translation_vector = Vector([0.0, 0.0, mmd_edit_bones['左目'].head[2] - rig_edit_bones['ORG-eye.L'].head[2]])

        rig_edit_bones['ORG-eye.L'].parent = rig_edit_bones['ORG-face']
        rig_edit_bones['ORG-eye.L'].length = mmd_edit_bones['左目'].length
        move_bone(rig_edit_bones['ORG-eye.L'], head=mmd_edit_bones['左目'].head)
        self._fit_bone(rig_edit_bones['ORG-eye.L'], mmd_edit_bones['左目'])

        rig_edit_bones['ORG-eye.R'].parent = rig_edit_bones['ORG-face']
        rig_edit_bones['ORG-eye.R'].length = mmd_edit_bones['右目'].length
        move_bone(rig_edit_bones['ORG-eye.R'], head=mmd_edit_bones['右目'].head)
        self._fit_bone(rig_edit_bones['ORG-eye.R'], mmd_edit_bones['右目'])

        rig_edit_bones['eyes'].translate(eye_height_translation_vector)
        rig_edit_bones['eye.L'].translate(eye_height_translation_vector)
        rig_edit_bones['eye.R'].translate(eye_height_translation_vector)
        rig_edit_bones['master_eye.L'].translate(eye_height_translation_vector)
        rig_edit_bones['master_eye.R'].translate(eye_height_translation_vector)
        rig_edit_bones['MCH-eye.R'].translate(eye_height_translation_vector)
        rig_edit_bones['MCH-eye.L'].translate(eye_height_translation_vector)

        # add eyes fk bones
        rig_eye_fk_l_bone, rig_eye_fk_r_bone, rig_eyes_fk_bone = self._add_eye_fk_bones(rig_edit_bones)
        rig_eyes_fk_bone.head = mmd_edit_bones['両目'].head
        rig_eyes_fk_bone.tail = rig_eyes_fk_bone.head - Vector([0, mmd_edit_bones['両目'].length, 0])
        self.fit_edit_bone_rotation(mmd_edit_bones['両目'], rig_eyes_fk_bone)
        self.fit_edit_bone_rotation(mmd_edit_bones['左目'], rig_eye_fk_l_bone)
        self.fit_edit_bone_rotation(mmd_edit_bones['右目'], rig_eye_fk_r_bone)

    def bind_bones(self, mmd_armature_object: MMDArmatureObject):
        bind_mmd_rigify = self.datapaths[ControlType.BIND_MMD_UUUNYAA]
        data_path = f'pose.bones{bind_mmd_rigify.data_path}'

        # bind rigify -> mmd
        mmd_pose_bones: Dict[str, bpy.types.PoseBone] = mmd_armature_object.strict_pose_bones
        for mmd_bind_info in self.mmd_bind_infos:  # pylint: disable=maybe-no-member
            if mmd_bind_info.bind_type == MMDBindType.NONE:
                continue

            mmd_bone_name = mmd_bind_info.bone_info.mmd_bone_name

            if mmd_bone_name not in mmd_pose_bones:
                continue

            mmd_pose_bone = mmd_pose_bones[mmd_bone_name]

            for constraint in mmd_pose_bone.constraints:
                if constraint.name == 'IK' and constraint.type == 'IK':
                    add_influence_driver(constraint, self.raw_object, data_path, invert=True)

                elif mmd_bind_info.bind_type == MMDBindType.COPY_EYE:
                    # mmd internal eye influence
                    add_influence_driver(constraint, self.raw_object, data_path, invert=True)

            binders[mmd_bind_info.bind_type](
                mmd_pose_bone,
                self.raw_object,
                mmd_bind_info.bind_bone_name,
                data_path
            )

    def remove_unused_face_bones(self):
        rig_pose_bones: Dict[str, bpy.types.PoseBone] = self.pose_bones

        def remove_influence_drivers(pose_bone_name: str):
            if pose_bone_name not in rig_pose_bones:
                return

            for constraint in rig_pose_bones[pose_bone_name].constraints:
                constraint.driver_remove('influence')

        # remove unused face drivers
        remove_influence_drivers('MCH-jaw_master')
        remove_influence_drivers('MCH-jaw_master.001')
        remove_influence_drivers('MCH-jaw_master.002')
        remove_influence_drivers('MCH-jaw_master.003')

        # remove unused face bones
        use_bone_names = {
            'MCH-eyes_parent',
            'eyes',
            'eye.L', 'eye.R',
            'master_eye.L', 'master_eye.R',
            'MCH-eye.L', 'MCH-eye.R',
            'ORG-eye.L', 'ORG-eye.R',
            'mmd_uuunyaa_eyes_fk',
            'mmd_uuunyaa_eye_fk.L', 'mmd_uuunyaa_eye_fk.R',
            'jaw_master',
        }
        rig_edit_bones: bpy.types.ArmatureEditBones = self.edit_bones
        for rig_edit_bone in rig_edit_bones['ORG-face'].children_recursive:
            if rig_edit_bone.name in use_bone_names:
                continue

            rig_edit_bones.remove(rig_edit_bone)

    def imitate_mmd_pose_behavior(self):
        super().imitate_mmd_pose_behavior()

        # hide unused face bones
        hide_bone_names = {
            'jaw_master',
        }
        rig_bones: bpy.types.ArmatureBones = self.bones
        for hide_bone_name in hide_bone_names:
            rig_bones[hide_bone_name].hide = True

    def fit_bone_rotations(self, mmd_armature_object: MMDArmatureObject):
        rig_edit_bones: bpy.types.ArmatureEditBones = self.edit_bones
        mmd_edit_bones: bpy.types.ArmatureEditBones = mmd_armature_object.strict_edit_bones

        for mmd_bind_info in self.mmd_bind_infos:  # pylint: disable=maybe-no-member
            bind_bone_name = mmd_bind_info.bind_bone_name
            if bind_bone_name is None:
                continue

            mmd_bone_name = mmd_bind_info.bone_info.mmd_bone_name
            if mmd_bone_name not in mmd_edit_bones or bind_bone_name not in rig_edit_bones:
                continue

            mmd_edit_bones[mmd_bone_name].roll = rig_edit_bones[bind_bone_name].roll
