# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from mmd_uuunyaa_tools.editors.armatures import GroupType, MMDBindInfo, MMDBindType, MMDBoneInfo

# pose.bones["c_hand_ik.l"]["ik_fk_switch"] = 1.000 # FK
# pose.bones["c_hand_ik.l"]["auto_stretch"] = 0.000 # No stretch

# pose.bones["c_foot_ik.l"]["ik_fk_switch"] = 1.000 # IK
# pose.bones["c_foot_ik.l"]["auto_stretch"] = 0.000 # No stretch

# pose.bones["c_head.x"]["head_free"] = 1 # Free

# disable pole target
# pose.bones["leg_ik_nostr.l"].constraints["IK"].pole_target #???
# pose.bones["c_leg_pole.l"]["pole_parent"] = 1 # first choice

# c_root.x 下半身


# pose.bones["c_eye_target.x"]["eye_target"] -> IK/FK

mmd_rigify_bones = [
    MMDBindInfo(MMDBoneInfo.全ての親, 'c_pos', 'c_pos', GroupType.TORSO, MMDBindType.COPY_ROOT),
    MMDBindInfo(MMDBoneInfo.センター, 'c_traj', 'c_traj', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.グルーブ, 'groove', 'groove', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.腰, 'c_root_master.x', '	c_root_master.x', GroupType.TORSO, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.上半身, 'c_spine_01.x', 'spine_01.x', GroupType.TORSO, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.上半身1, None, None, GroupType.TORSO, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.上半身2, 'c_spine_02.x', 'spine_02.x', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.首, 'c_neck.x', 'neck.x', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.頭, 'c_head.x', 'head.x', GroupType.TORSO, MMDBindType.COPY_PARENT),

    MMDBindInfo(MMDBoneInfo.両目, 'mmd_rigify_eyes_fk', 'mmd_rigify_eyes_fk', GroupType.FACE, MMDBindType.COPY_EYE),
    MMDBindInfo(MMDBoneInfo.左目, 'mmd_rigify_eye_fk.l', 'c_eye.l', GroupType.FACE, MMDBindType.COPY_EYE),
    MMDBindInfo(MMDBoneInfo.右目, 'mmd_rigify_eye_fk.r', 'c_eye.r', GroupType.FACE, MMDBindType.COPY_EYE),

    MMDBindInfo(MMDBoneInfo.左肩, 'c_shoulder.l', 'shoulder.l', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左腕, 'c_arm_fk.l', 'arm.l', GroupType.ARM_L, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.左腕捩, 'mmd_rigify_upper_arm_twist_fk.l', None, GroupType.ARM_L, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.左ひじ, 'c_forearm_fk.l', 'forearm.l', GroupType.ARM_L, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.左手捩, 'mmd_rigify_wrist_twist_fk.l', None, GroupType.ARM_L, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.左手首, 'c_hand_fk.l', 'hand.l', GroupType.ARM_L, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.左親指０, 'c_thumb1.l', 'thumb1.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左親指１, 'c_thumb2.l', 'thumb2.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左親指２, 'c_thumb3.l', 'thumb3.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左人指０, None, None, GroupType.ARM_L, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.左人指１, 'c_index1.l', 'index1.l', GroupType.ARM_L, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左人指２, 'c_index2.l', 'index2.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左人指３, 'c_index3.l', 'index3.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左中指０, None, None, GroupType.ARM_L, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.左中指１, 'c_middle1.l', 'middle1.l', GroupType.ARM_L, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左中指２, 'c_middle2.l', 'middle2.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左中指３, 'c_middle3.l', 'middle3.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左薬指０, None, None, GroupType.ARM_L, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.左薬指１, 'c_ring1.l', 'ring1.l', GroupType.ARM_L, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左薬指２, 'c_ring2.l', 'ring2.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左薬指３, 'c_ring3.l', 'ring3.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左小指０, None, None, GroupType.ARM_L, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.左小指１, 'c_pinky1.l', 'pinky1.l', GroupType.ARM_L, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左小指２, 'c_pinky2.l', 'pinky2.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左小指３, 'c_pinky3.l', 'pinky3.l', GroupType.ARM_L, MMDBindType.COPY_LOCAL),

    MMDBindInfo(MMDBoneInfo.右肩, 'c_shoulder.r', 'shoulder.r', GroupType.TORSO, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右腕, 'c_arm_fk.r', 'arm.r', GroupType.ARM_R, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.右腕捩, 'mmd_rigify_upper_arm_twist_fk.r', None, GroupType.NONE, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右ひじ, 'c_forearm_fk.r', 'forearm.r', GroupType.ARM_R, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.右手捩, 'mmd_rigify_wrist_twist_fk.r', None, GroupType.ARM_R, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右手首, 'c_hand_fk.r', 'hand.r', GroupType.ARM_R, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.右親指０, 'c_thumb1.r', 'thumb1.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右親指１, 'c_thumb2.r', 'thumb2.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右親指２, 'c_thumb3.r', 'thumb3.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右人指０, None, None, GroupType.ARM_R, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右人指１, 'c_index1.l', 'index1.r', GroupType.ARM_R, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右人指２, 'c_index2.l', 'index2.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右人指３, 'c_index3.l', 'index3.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右中指０, None, None, GroupType.ARM_R, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右中指１, 'c_middle1.r', 'middle1.r', GroupType.ARM_R, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右中指２, 'c_middle2.r', 'middle2.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右中指３, 'c_middle3.r', 'middle3.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右薬指０, None, None, GroupType.ARM_R, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右薬指１, 'c_ring1.r', 'ring1.r', GroupType.ARM_R, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右薬指２, 'c_ring2.r', 'ring2.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右薬指３, 'c_ring3.r', 'ring3.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右小指０, None, None, GroupType.ARM_R, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右小指１, 'c_pinky1.r', 'pinky1.r', GroupType.ARM_R, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右小指２, 'c_pinky2.r', 'pinky2.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右小指３, 'c_pinky3.r', 'pinky3.r', GroupType.ARM_R, MMDBindType.COPY_LOCAL),

    MMDBindInfo(MMDBoneInfo.下半身, 'c_root.x', 'root.x', GroupType.TORSO, MMDBindType.COPY_PARENT),

    MMDBindInfo(MMDBoneInfo.左足, 'c_thigh_ik.l', 'thigh.l', GroupType.LEG_L, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左ひざ, None, 'leg.l', GroupType.LEG_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左足首, None, 'foot.l', GroupType.LEG_L, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.左足ＩＫ, 'c_foot_ik.l', 'c_foot_ik.l', GroupType.LEG_L, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.左足先EX, 'c_toes_ik.l', 'toes_01.l', GroupType.LEG_L, MMDBindType.COPY_TOE),

    MMDBindInfo(MMDBoneInfo.右足, 'c_thigh_ik.r', 'thigh.r', GroupType.LEG_R, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右ひざ, None, 'leg.r', GroupType.LEG_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右足首, None, 'foot.r', GroupType.LEG_R, MMDBindType.COPY_LOCAL),
    MMDBindInfo(MMDBoneInfo.右足ＩＫ, 'c_foot_ik.r', 'c_foot_ik.r', GroupType.LEG_R, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.右足先EX, 'c_toes_ik.r', 'toes_01.r', GroupType.LEG_R, MMDBindType.COPY_TOE),

    MMDBindInfo(MMDBoneInfo.左つま先ＩＫ, 'mmd_rigify_toe_ik.l', 'mmd_rigify_toe_ik.l', GroupType.LEG_L, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右つま先ＩＫ, 'mmd_rigify_toe_ik.r', 'mmd_rigify_toe_ik.r', GroupType.LEG_R, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左つま先, None, None, GroupType.LEG_L, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右つま先, None, None, GroupType.LEG_R, MMDBindType.NONE),

    MMDBindInfo(MMDBoneInfo.左肩C, 'mmd_rigify_shoulder_cancel.l', 'mmd_rigify_shoulder_cancel.l', GroupType.NONE, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左肩P, 'mmd_rigify_shoulder_parent.l', 'mmd_rigify_shoulder_parent.l', GroupType.NONE, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右肩C, 'mmd_rigify_shoulder_cancel.r', 'mmd_rigify_shoulder_cancel.r', GroupType.NONE, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.右肩P, 'mmd_rigify_shoulder_parent.r', 'mmd_rigify_shoulder_parent.r', GroupType.NONE, MMDBindType.COPY_PARENT),
    MMDBindInfo(MMDBoneInfo.左ダミー, None, None, GroupType.NONE, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.右ダミー, None, None, GroupType.NONE, MMDBindType.NONE),
    MMDBindInfo(MMDBoneInfo.左足IK親, 'mmd_rigify_leg_ik_parent.l', 'mmd_rigify_leg_ik_parent.l', GroupType.LEG_L, MMDBindType.COPY_POSE),
    MMDBindInfo(MMDBoneInfo.右足IK親, 'mmd_rigify_leg_ik_parent.r', 'mmd_rigify_leg_ik_parent.r', GroupType.LEG_R, MMDBindType.COPY_POSE),
]
