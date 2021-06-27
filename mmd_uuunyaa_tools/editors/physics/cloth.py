# -*- coding: utf-8 -*-
# Copyright 2021
#   小威廉伯爵 https://github.com/958261649/Miku_Miku_Rig
#   UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Set, Tuple, Union

import bmesh
import bpy
from mmd_uuunyaa_tools.m17n import _, iface_
from mmd_uuunyaa_tools.tuners import TunerABC, TunerRegistry
from mmd_uuunyaa_tools.utilities import MessageException, import_mmd_tools

mmd_tools = import_mmd_tools()


class PhysicsMode(Enum):
    AUTO = 'Auto'
    BONE_CONSTRAINT = 'Bone Constraint'
    SURFACE_DEFORM = 'Surface Deform'


translation_properties = [
    _('Auto'),
    _('Bone Constraint'),
    _('Surface Deform'),
]


class AdjustMeshCollision(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.adjust_mesh_collision'
    bl_label = _('Adjust Mesh Collision')
    bl_options = {'REGISTER', 'UNDO'}

    damping: bpy.props.FloatProperty(name=_('Damping'), min=0.0, max=1.0, default=0.1, precision=3)
    thickness_outer: bpy.props.FloatProperty(name=_('Thickness Outer'), min=0.001, max=1.000, default=0.001, precision=3)
    thickness_inner: bpy.props.FloatProperty(name=_('Thickness Inner'), min=0.001, max=1.000, default=0.200, precision=3)
    cloth_friction: bpy.props.FloatProperty(name=_('Cloth Friction'), min=0, max=80, default=5, precision=3)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        return MeshEditor.mesh_object_is_contained_in(context.selected_objects)

    def execute(self, context: bpy.types.Context):
        try:
            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    continue

                MeshEditor(obj).edit_collision_modifier(
                    name='mmd_uuunyaa_physics_collision',
                    damping=self.damping,
                    thickness_outer=self.thickness_outer,
                    thickness_inner=self.thickness_inner,
                    cloth_friction=self.cloth_friction,
                )

        except MessageException as ex:
            self.report(type={'ERROR'}, message=str(ex))
            return {'CANCELLED'}

        return {'FINISHED'}


class SelectMeshCloth(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.select_mesh_cloth'
    bl_label = _('Select Mesh Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    only_in_mmd_model: bpy.props.BoolProperty(name=_('Only in the MMD Model'))
    only_same_settings: bpy.props.BoolProperty(name=_('Only the same Settings'))

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        active_object = context.active_object
        if active_object is None:
            return False

        if active_object.type != 'MESH':
            return False

        return MeshEditor(active_object).find_cloth_modifier() is not None

    @staticmethod
    def filter_only_in_mmd_model(key_object: bpy.types.Object) -> Iterable[bpy.types.Object]:
        mmd_root = mmd_tools.core.model.Model.findRoot(key_object)
        if mmd_root is None:
            return []

        return mmd_tools.core.model.Model(mmd_root).meshes()

    def execute(self, context: bpy.types.Context):
        key_object = context.active_object
        key_settings = key_object.mmd_uuunyaa_tools_cloth_settings

        obj: bpy.types.Object
        for obj in self.filter_only_in_mmd_model(key_object) if self.only_in_mmd_model else bpy.data.objects:
            if obj.type != 'MESH':
                continue

            if MeshEditor(obj).find_cloth_modifier() is None:
                continue
            elif self.only_same_settings and obj.mmd_uuunyaa_tools_cloth_settings != key_settings:
                continue

            obj.select_set(True)

        return {'FINISHED'}


class CopyClothAdjusterSettings(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.copy_cloth_adjuster_settings'
    bl_label = _('Copy Cloth Adjuster Settings')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return len([o for o in context.selected_objects if o.type == 'MESH']) >= 2

    def execute(self, context: bpy.types.Context):
        from_object = context.active_object
        from_settings = from_object.mmd_uuunyaa_tools_cloth_settings
        from_modifier = MeshEditor(from_object).get_cloth_modifier()

        for to_object in context.selected_objects:
            if to_object.type != 'MESH':
                continue

            if from_object == to_object:
                continue

            MeshEditor(to_object).get_cloth_modifier(from_modifier.name)

            to_settings = to_object.mmd_uuunyaa_tools_cloth_settings
            to_settings.presets = from_settings.presets
            to_settings.mass = from_settings.mass
            to_settings.stiffness = from_settings.stiffness
            to_settings.damping = from_settings.damping
            to_settings.collision_quality = from_settings.collision_quality
            to_settings.distance_min = from_settings.distance_min
            to_settings.impulse_clamp = from_settings.impulse_clamp
            to_settings.frame_start = from_settings.frame_start
            to_settings.frame_end = from_settings.frame_end

        return {'FINISHED'}


class AdjustMeshCloth(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.adjust_mesh_cloth'
    bl_label = _('Adjust Mesh Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def update_presets(prop, _):
        prop.damping += 0.001

    presets: bpy.props.EnumProperty(
        name=_('Presets'),
        items=[(m.name, m.value, '') for m in PhysicsMode],
        default=PhysicsMode.AUTO.name,
        update=update_presets.__func__
    )

    stiffness: bpy.props.FloatProperty(name=_('Stiffness'), min=0.001, max=1.000, default=0.001, precision=3)
    damping: bpy.props.FloatProperty(name=_('Damping'), min=0.0, max=1.0, default=0.1, precision=3)
    thickness_inner: bpy.props.FloatProperty(name=_('Thickness Inner'), min=0.001, max=1.000, default=0.200, precision=3)
    cloth_friction: bpy.props.FloatProperty(name=_('Cloth Friction'), min=0, max=80, default=5, precision=3)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        return MeshEditor.mesh_object_is_contained_in(context.selected_objects)

    def execute(self, context: bpy.types.Context):
        print(self.damping)
        return {'FINISHED'}


class RemoveMeshCollision(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.remove_mesh_collision'
    bl_label = _('Remove Mesh Collision')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False
        return MeshEditor.mesh_object_is_contained_in(context.selected_objects)

    def execute(self, context: bpy.types.Context):
        try:
            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    continue

                MeshEditor(obj).remove_collision_modifier()

        except MessageException as ex:
            self.report(type={'ERROR'}, message=str(ex))
            return {'CANCELLED'}

        return {'FINISHED'}


class ConvertRigidBodyToClothOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_rigid_body_to_cloth'
    bl_label = _('Convert Rigid Body to Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    subdivision_level: bpy.props.IntProperty(name=_('Subdivision Level'), min=0, max=5, default=0)
    physics_mode: bpy.props.EnumProperty(
        name=_('Physics Mode'),
        items=[(m.name, m.value, '') for m in PhysicsMode],
        default=PhysicsMode.AUTO.name
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        selected_mesh_mmd_root = None
        selected_rigid_body_mmd_root = None

        mmd_find_root = mmd_tools.core.model.Model.findRoot
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                return False

            if obj.mmd_type == 'RIGID_BODY':
                selected_rigid_body_mmd_root = mmd_find_root(obj)
            elif obj.mmd_type == 'NONE':
                selected_mesh_mmd_root = mmd_find_root(obj)

            if selected_rigid_body_mmd_root == selected_mesh_mmd_root:
                return selected_rigid_body_mmd_root is not None

        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context):
        try:
            mmd_find_root = mmd_tools.core.model.Model.findRoot

            target_mmd_root_object = None
            rigid_body_objects: List[bpy.types.Object] = []
            mesh_objects: List[bpy.types.Object] = []

            obj: bpy.types.Object
            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    continue

                mmd_root_object = mmd_find_root(obj)
                if mmd_root_object is None:
                    continue

                if target_mmd_root_object is None:
                    target_mmd_root_object = mmd_root_object
                elif target_mmd_root_object != mmd_root_object:
                    raise MessageException(_('Multiple MMD models selected. Please select single model at a time.'))

                if obj.mmd_type == 'RIGID_BODY':
                    rigid_body_objects.append(obj)
                elif obj.mmd_type == 'NONE':
                    mesh_objects.append(obj)

            ClothEditor.convert_physics_rigid_body_to_cloth(
                target_mmd_root_object,
                rigid_body_objects,
                mesh_objects,
                self.subdivision_level,
                PhysicsMode[self.physics_mode]
            )

        except MessageException as ex:
            self.report(type={'ERROR'}, message=str(ex))
            return {'CANCELLED'}

        return {'FINISHED'}


@dataclass
class Edges:
    up_edges: Set[bmesh.types.BMEdge] = field(default_factory=set)
    down_edges: Set[bmesh.types.BMEdge] = field(default_factory=set)
    side_edges: Set[bmesh.types.BMEdge] = field(default_factory=set)


@dataclass
class Vertices:
    up_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    down_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    # wire_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    hair_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    side_verts: Set[bmesh.types.BMVert] = field(default_factory=set)


class UuuNyaaPhysicsClothAdjuster(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_physics_cloth_adjuster'
    bl_label = _('UuuNyaa Cloth Adjuster')
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'physics'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return MeshEditor(context.active_object).find_cloth_modifier() is not None

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        mesh_object: bpy.types.Object = context.active_object
        cloth_settings = mesh_object.mmd_uuunyaa_tools_cloth_settings

        col = layout.column()
        col.prop(cloth_settings, 'presets')
        col.prop(cloth_settings, 'mass')
        col.prop(cloth_settings, 'stiffness')
        col.prop(cloth_settings, 'damping')

        col = layout.column()
        col.label(text='Collisions:')
        col.prop(cloth_settings, 'collision_quality')
        col.prop(cloth_settings, 'distance_min', slider=True)
        col.prop(cloth_settings, 'impulse_clamp')

        col = layout.column()
        col.label(text='Cache:')
        row = col.row(align=True)
        row.prop(cloth_settings, 'frame_start', text='Simulation Start')
        row.prop(cloth_settings, 'frame_end', text='Simulation End')

        col = layout.column()
        col.label(text='Batch Operation:')
        col.operator(CopyClothAdjusterSettings.bl_idname, text=_('Copy to Selected'), icon='DUPLICATE')


class UuuNyaaPhysicsPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_physics'
    bl_label = _('UuuNyaa Physics')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text='Relevant Selection:', icon='RESTRICT_SELECT_OFF')
        col.operator_context = 'EXEC_DEFAULT'
        operator = col.operator('mmd_tools.rigid_body_select', text=_('Select Rigid Body'), icon='RIGID_BODY')
        operator.properties = set(['collision_group_number', 'shape'])
        col.operator(SelectMeshCloth.bl_idname, text=_('Select Cloth Mesh'), icon='MOD_CLOTH')

        col = layout.column(align=True)
        col.label(text='MMD Model:', icon='OUTLINER_OB_ARMATURE')
        box = col.box()
        root_object = mmd_tools.core.model.Model.findRoot(context.active_object)
        if root_object is None:
            box.label(text=_('MMD Model not selected.'), icon='ERROR')
        else:
            mmd_root = root_object.mmd_root

            col = box.column(align=True)
            col.label(text='Visibility:', icon='HIDE_OFF')
            row = col.row(align=True)
            row.prop(mmd_root, 'show_meshes', text='Mesh', toggle=True)
            row.prop(mmd_root, 'show_armature', text='Armature', toggle=True)
            row.prop(mmd_root, 'show_rigid_bodies', text='Rigid Body', toggle=True)

            col = box.column(align=True)
            col.label(text='Converter:', icon='SHADERFX')

            row = col.split(factor=0.9, align=True)
            row.operator_context = 'EXEC_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_('Rigid Body to Cloth'), icon='MATCLOTH')
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_(''), icon='WINDOW')

        col = layout.column(align=True)
        col.label(text='Remove:', icon='TRASH')
        col.operator(RemoveMeshCollision.bl_idname, text=_('Remove Collision'), icon='MOD_PHYSICS')
        col.operator(RemoveMeshCollision.bl_idname, text=_('Remove Cloth'), icon='MOD_CLOTH')


SettingsOrNone = Union[Dict[str, Any], None]


class MeshEditor:
    def __init__(self, mesh_object: bpy.types.Object):
        self.mesh_object = mesh_object

    @staticmethod
    def edit_modifier(modifier: bpy.types.Modifier, settings: SettingsOrNone = None, **kwargs) -> bpy.types.Modifier:
        for key, value in kwargs.items():
            setattr(modifier, key, value)

        if settings is None:
            return modifier

        for key, value in settings.items():
            setattr(modifier.settings, key, value)

        return modifier

    def add_modifier(self, modifier_type: str, name: str, settings: SettingsOrNone = None, **kwargs) -> bpy.types.Modifier:
        return self.edit_modifier(
            self.mesh_object.modifiers.new(name, modifier_type),
            settings=settings,
            **kwargs
        )

    def add_subsurface_modifier(self, name: str, levels: int, render_levels: int, **kwargs) -> bpy.types.Modifier:
        return self.add_modifier(
            'SUBSURF', name,
            levels=levels,
            render_levels=render_levels,
            boundary_smooth='PRESERVE_CORNERS',
            show_only_control_edges=False,
            **kwargs
        )

    def add_armature_modifier(self, name: str, armature_object: bpy.types.Object, **kwargs) -> bpy.types.Modifier:
        return self.add_modifier(
            'ARMATURE', name,
            object=armature_object,
            **kwargs
        )

    def add_corrective_smooth_modifier(self, name: str, **kwargs) -> bpy.types.Modifier:
        return self.add_modifier(
            'CORRECTIVE_SMOOTH', name,
            **kwargs
        )

    def add_surface_deform_modifier(self, name: str, **kwargs) -> bpy.types.Modifier:
        return self.add_modifier(
            'SURFACE_DEFORM', name,
            **kwargs
        )

    def find_singleton_modifier(self, modifier_type: str) -> Union[bpy.types.Modifier, None]:
        if modifier_type not in {'CLOTH', 'COLLISION'}:
            raise NotImplementedError(f'{modifier_type} is not supported.')

        for modifier in self.mesh_object.modifiers:
            if modifier.type == modifier_type:
                return modifier

        return None

    def get_singleton_modifier(self, modifier_type: str, name: str) -> bpy.types.Modifier:
        modifier = self.find_singleton_modifier(modifier_type)
        if modifier is None:
            modifier = self.add_modifier(modifier_type, name=name)
        return modifier

    def edit_singleton_modifier(self, modifier: bpy.types.Modifier, **kwargs) -> bpy.types.Modifier:
        return self.edit_modifier(modifier, settings=kwargs)

    def remove_singleton_modifier(self, modifier_type: str):
        modifier = self.find_singleton_modifier(modifier_type)
        if modifier is None:
            return

        self.mesh_object.modifiers.remove(modifier)

    def find_cloth_modifier(self) -> Union[bpy.types.Modifier, None]:
        return self.find_singleton_modifier('CLOTH')

    def get_cloth_modifier(self, name: str = 'Cloth') -> bpy.types.Modifier:
        return self.get_singleton_modifier('CLOTH', name)

    def edit_cloth_modifier(self, name: str, **kwargs) -> bpy.types.Modifier:
        return self.edit_singleton_modifier(self.get_cloth_modifier(name), **kwargs)

    def find_cloth_settings(self) -> Union[bpy.types.ClothSettings, None]:
        modifier = self.find_cloth_modifier()
        if modifier is None:
            return None
        return modifier.settings

    def find_cloth_collision_settings(self) -> Union[bpy.types.ClothCollisionSettings, None]:
        modifier = self.find_cloth_modifier()
        if modifier is None:
            return None
        return modifier.collision_settings

    def remove_cloth_modifier(self):
        self.remove_singleton_modifier('CLOTH')

    def find_collision_modifier(self) -> Union[bpy.types.Modifier, None]:
        return self.find_singleton_modifier('COLLISION')

    def get_collision_modifier(self, name: str = 'Collision') -> bpy.types.Modifier:
        return self.get_singleton_modifier('COLLISION', name)

    def edit_collision_modifier(
            self,
            name: str,
            damping: float = 0.1,
            thickness_outer: float = 0.001,
            thickness_inner: float = 0.200,
            cloth_friction: float = 5,
            **kwargs
    ) -> bpy.types.Modifier:
        return self.edit_singleton_modifier(
            self.get_collision_modifier(name),
            damping=damping,
            thickness_outer=thickness_outer,
            thickness_inner=thickness_inner,
            cloth_friction=cloth_friction,
            **kwargs
        )

    def remove_collision_modifier(self):
        self.remove_singleton_modifier('COLLISION')

    @staticmethod
    def mesh_object_is_contained_in(objects: Iterable[bpy.types.Object]):
        for obj in objects:
            if obj.type == 'MESH':
                return True

        return False


class RigidBodyEditor(MeshEditor):
    @staticmethod
    def rigid_body_object_is_contained_in(objects: Iterable[bpy.types.Object]):
        for obj in objects:
            if obj.type != 'MESH':
                return False

            if obj.rigid_body:
                return True

        return False


class ClothEditor:
    @classmethod
    def convert_physics_rigid_body_to_cloth(
        cls,
        mmd_root_object: bpy.types.Object,
        rigid_body_objects: List[bpy.types.Object],
        mesh_objects: List[bpy.types.Object],
        subdivision_level: int,
        physics_mode: PhysicsMode
    ):

        mmd_model = mmd_tools.core.model.Model(mmd_root_object)
        mmd_mesh_object = mesh_objects[0]
        mmd_armature_object = mmd_model.armature()

        rigid_bodys_count = len(rigid_body_objects)
        rigid_body_index_dict = {
            rigid_body_objects[i]: i
            for i in range(rigid_bodys_count)
        }

        pose_bones: List[bpy.types.PoseBone] = []
        for rigid_body_object in rigid_body_objects:
            pose_bone = mmd_armature_object.pose.bones.get(rigid_body_object.mmd_rigid.bone)

            if pose_bone is None:
                raise MessageException(
                    iface_('No bones related with {rigid_body_name}, Please relate a bone to the Rigid Body.')
                    .format(rigid_body_name=rigid_body_object.name)
                )

            pose_bones.append(pose_bone)

        rigid_body_mean_radius: float = sum([
            min(r.mmd_rigid.size) if r.mmd_rigid.shape == 'BOX'
            else r.mmd_rigid.size[0]
            for r in rigid_body_objects
        ]) / rigid_bodys_count

        def remove_objects(objects: Iterable[bpy.types.Object]):
            for obj in objects:
                bpy.data.objects.remove(obj)

        joint_objects, joint_edge_indices, side_joint_objects = cls.collect_joints(mmd_model, rigid_body_index_dict)

        remove_objects(joint_objects)

        cloth_mesh = bpy.data.meshes.new('mmd_uuunyaa_physics_cloth')
        cloth_mesh.from_pydata([r.location for r in rigid_body_objects], joint_edge_indices, [])
        cloth_mesh.validate()

        cloth_mesh_object = cls.new_mesh_object('mmd_uuunyaa_physics_cloth', cloth_mesh)
        cloth_mesh_object.parent = mmd_armature_object
        cloth_mesh_object.display_type = 'WIRE'

        cls.add_edge_faces(cloth_mesh_object)
        cls.clean_mesh(cloth_mesh, joint_edge_indices)

        cls.select_hair_ribbon_vertices(cloth_mesh_object)

        # 标记出特殊边和点
        # These are special edge and vertex
        cloth_bm: bmesh.types.BMesh = bmesh.new()
        cloth_bm.from_mesh(cloth_mesh)

        # 标出头部，尾部，飘带顶点
        # try mark head,tail,ribbon vertex
        cloth_bm.verts.ensure_lookup_table()
        cloth_bm.edges.ensure_lookup_table()

        vertices = cls.collect_vertices(cloth_bm, pose_bones, physics_mode)
        edges = cls.collect_edges(cloth_bm, vertices)

        new_up_verts = cls.extend_up_edges(cloth_bm, pose_bones, vertices, edges, physics_mode)
        new_down_verts = cls.extend_down_edges(cloth_bm, pose_bones, vertices, edges)

        cloth_bm.verts.index_update()

        cls.fill_faces(cloth_bm, edges.up_edges, new_up_verts)
        cls.fill_faces(cloth_bm, edges.down_edges, new_down_verts)

        cloth_bm.verts.index_update()

        new_side_verts = cls.extend_side_vertices(cloth_bm, vertices, edges)

        cls.fill_faces(cloth_bm, edges.side_edges, new_side_verts)

        cloth_bm.edges.ensure_lookup_table()
        cloth_bm.verts.ensure_lookup_table()
        cloth_bm.to_mesh(cloth_mesh)

        cls.normals_make_consistent(cloth_mesh_object)

        pin_vertex_group = cls.new_pin_vertex_group(cloth_mesh_object, side_joint_objects, new_up_verts, new_side_verts, rigid_body_index_dict)

        remove_objects(side_joint_objects)

        deform_vertex_group: bpy.types.VertexGroup = mmd_mesh_object.vertex_groups.new(name='mmd_uuunyaa_physics_cloth_deform')

        mesh_editor = MeshEditor(cloth_mesh_object)
        mesh_editor.add_subsurface_modifier('mmd_uuunyaa_physics_cloth_subsurface', subdivision_level, subdivision_level)
        mesh_editor.add_armature_modifier('mmd_uuunyaa_physics_cloth_armature', mmd_armature_object, vertex_group=pin_vertex_group.name)
        mesh_editor.edit_cloth_modifier('mmd_uuunyaa_physics_cloth', vertex_group_mass=pin_vertex_group.name)

        corrective_smooth_modifier = mesh_editor.add_corrective_smooth_modifier('mmd_uuunyaa_physics_cloth_smooth', smooth_type='LENGTH_WEIGHTED', rest_source='BIND')
        bpy.ops.object.correctivesmooth_bind(modifier=corrective_smooth_modifier.name)
        if subdivision_level == 0:
            corrective_smooth_modifier.show_viewport = False

        deform_vertex_group_index = deform_vertex_group.index
        vertices_hair_verts = vertices.hair_verts

        cls.bind_mmd_mesh(mmd_mesh_object, cloth_mesh_object, cloth_bm, pose_bones, deform_vertex_group_index, vertices_hair_verts, physics_mode)

        remove_objects(rigid_body_objects)

        cls.fix_mesh(cloth_mesh_object, rigid_body_mean_radius)

        if len(cloth_mesh.polygons) != 0 and physics_mode in {PhysicsMode.AUTO, PhysicsMode.SURFACE_DEFORM}:
            bpy.context.view_layer.objects.active = mmd_mesh_object
            bpy.ops.object.surfacedeform_bind(
                modifier=MeshEditor(mmd_mesh_object).add_surface_deform_modifier(
                    'mmd_uuunyaa_physics_cloth_deform',
                    target=cloth_mesh_object,
                    vertex_group=deform_vertex_group.name
                ).name
            )

        cloth_bm.free()

    @staticmethod
    def fix_mesh(cloth_mesh_object: bpy.types.Object, radius: float):
        # 挤出孤立边
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={'value': (0, 0.01, 0)})
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.transform.shrink_fatten(value=radius, use_even_offset=False, mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def bind_mmd_mesh(mmd_mesh_object, cloth_mesh_object, cloth_bm, pose_bones, deform_vertex_group_index, vertices_hair_verts, physics_mode):
        unnecessary_vertex_groups: List[bpy.types.VertexGroup] = []

        mmd_mesh: bpy.types.Mesh = mmd_mesh_object.data
        mmd_bm: bmesh.types.BMesh = bmesh.new()
        mmd_bm.from_mesh(mmd_mesh)

        mmd_bm.verts.layers.deform.verify()
        deform_layer = mmd_bm.verts.layers.deform.active

        for i, bone in enumerate(pose_bones):
            vert = cloth_bm.verts[i]
            name = bone.name
            if vert in vertices_hair_verts and physics_mode in {PhysicsMode.AUTO, PhysicsMode.BONE_CONSTRAINT}:
                line_vertex_group = cloth_mesh_object.vertex_groups.new(name=name)
                line_vertex_group.add([i], 1, 'REPLACE')
                for c in bone.constraints:
                    bone.constraints.remove(c)
                con = bone.constraints.new(type='STRETCH_TO')
                con.target = cloth_mesh_object
                con.subtarget = name
                con.rest_length = bone.length
            else:
                # merge deform vertex weights
                from_vertex_group = mmd_mesh_object.vertex_groups[name]
                from_index = from_vertex_group.index
                unnecessary_vertex_groups.append(from_vertex_group)

                vert: bmesh.types.BMVert
                for vert in mmd_bm.verts:
                    deform_vert: bmesh.types.BMDeformVert = vert[deform_layer]
                    if from_index not in deform_vert:
                        continue

                    to_index = deform_vertex_group_index
                    deform_vert[to_index] = deform_vert.get(to_index, 0.0) + deform_vert[from_index]

        mmd_bm.to_mesh(mmd_mesh)
        mmd_bm.free()

        for vertex_group in unnecessary_vertex_groups:
            mmd_mesh_object.vertex_groups.remove(vertex_group)

    @staticmethod
    def new_pin_vertex_group(cloth_mesh_object, side_joint_objects, new_up_verts, new_side_verts, rigid_body_index_dict):
        pin_vertex_group = cloth_mesh_object.vertex_groups.new(name='mmd_uuunyaa_physics_cloth_pin')

        for obj in side_joint_objects:
            if obj.rigid_body_constraint.object1 in rigid_body_index_dict:
                side_rigid_body = obj.rigid_body_constraint.object1
                pin_rigid_body = obj.rigid_body_constraint.object2
            else:
                side_rigid_body = obj.rigid_body_constraint.object2
                pin_rigid_body = obj.rigid_body_constraint.object1

            index1 = rigid_body_index_dict[side_rigid_body]
            vert2 = new_up_verts[index1]
            if vert2 is None:
                pin_index = [index1]
            else:
                vert3 = new_side_verts[vert2.index]
                if vert3 is None:
                    pin_index = [vert2.index]
                else:
                    pin_index = [vert2.index, vert3.index]

            pin_bone_name = pin_rigid_body.mmd_rigid.bone

            skin_vertex_group = cloth_mesh_object.vertex_groups.get(pin_bone_name)
            if skin_vertex_group is None:
                skin_vertex_group = cloth_mesh_object.vertex_groups.new(name=pin_bone_name)

            skin_vertex_group.add(pin_index, 1, 'REPLACE')
            pin_vertex_group.add(pin_index, 1, 'REPLACE')

        return pin_vertex_group

    @staticmethod
    def normals_make_consistent(cloth_mesh_object):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def extend_side_vertices(cloth_bm, vertices, edges):
        new_side_verts = [None for i in range(len(cloth_bm.verts))]

        for vert in vertices.side_verts:
            for edge in vert.link_edges:
                if edge not in edges.side_edges:
                    if edge.verts[0] == vert:
                        new_location = vert.co*2-edge.verts[1].co
                    else:
                        new_location = vert.co*2-edge.verts[0].co
                    break
            new_vert = cloth_bm.verts.new(new_location)
            new_side_verts[vert.index] = new_vert

        return new_side_verts

    @staticmethod
    def fill_faces(cloth_bm, edges, new_verts):
        for edge in edges:
            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            vert3 = new_verts[vert2.index]
            vert4 = new_verts[vert1.index]

            if vert3 is not None and vert4 is not None:
                cloth_bm.faces.new([vert1, vert2, vert3, vert4])

    @staticmethod
    def extend_up_edges(cloth_bm, pose_bones: List[bpy.types.PoseBone], vertices: Vertices, edges: Edges, physics_mode: PhysicsMode):
        new_up_verts = [None for i in range(len(cloth_bm.verts))]

        # 延长头部顶点
        # extend root vertex
        for vert in vertices.up_verts:
            new_location = pose_bones[vert.index].head

            if (
                (physics_mode == PhysicsMode.AUTO and vert not in vertices.hair_verts)
                or physics_mode == PhysicsMode.SURFACE_DEFORM
            ):
                for edge in vert.link_edges:
                    if edge in edges.up_edges:
                        break

                    if edge.verts[0] == vert:
                        new_location = vert.co*2-edge.verts[1].co
                    else:
                        new_location = vert.co*2-edge.verts[0].co

            new_vert = cloth_bm.verts.new(new_location)
            new_edge = cloth_bm.edges.new([vert, new_vert])
            new_up_verts[vert.index] = new_vert

            if vert in vertices.side_verts:
                vertices.side_verts.add(new_vert)
                edges.side_edges.add(new_edge)

        return new_up_verts

    @staticmethod
    def extend_down_edges(cloth_bm, pose_bones: List[bpy.types.PoseBone], vertices: Vertices, edges: Edges):
        new_down_verts = [None for i in range(len(cloth_bm.verts))]
        # 延长尾部顶点
        # extend tail vertex
        for vert in vertices.down_verts:
            if vert in vertices.up_verts:
                continue

            new_location = pose_bones[vert.index].tail
            for edge in vert.link_edges:
                if edge in edges.down_edges:
                    break

                if edge.verts[0] == vert:
                    new_location = vert.co*2-edge.verts[1].co
                else:
                    new_location = vert.co*2-edge.verts[0].co

            new_vert = cloth_bm.verts.new(new_location)
            new_edge = cloth_bm.edges.new([vert, new_vert])
            new_down_verts[vert.index] = new_vert

            if vert in vertices.side_verts:
                vertices.side_verts.add(new_vert)
                edges.side_edges.add(new_edge)

        return new_down_verts

    @staticmethod
    def select_hair_ribbon_vertices(cloth_mesh_object: bpy.types.Object):
        # 尝试标记出头发,飘带
        # try mark hair or ribbon vertex
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def new_mesh_object(name: str, cloth_mesh: bpy.types.Mesh):
        cloth_mesh_object = bpy.data.objects.new(name, cloth_mesh)
        bpy.context.collection.objects.link(cloth_mesh_object)

        return cloth_mesh_object

    @staticmethod
    def add_edge_faces(cloth_mesh_object: bpy.types.Object):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def collect_joints(mmd_model, rigid_body_index_dict: Dict[bpy.types.Object, int]) -> Tuple[List[bpy.types.Object], List[Tuple[int, int]], List[bpy.types.Object]]:
        joint_objects: List[bpy.types.Object] = []
        joint_edge_indices: List[Tuple[int, int]] = []
        side_joint_objects: List[bpy.types.Object] = []

        for obj in mmd_model.joints():
            obj1 = obj.rigid_body_constraint.object1
            obj2 = obj.rigid_body_constraint.object2
            if obj1 in rigid_body_index_dict and obj2 in rigid_body_index_dict:
                joint_objects.append(obj)
                joint_edge_indices.append((rigid_body_index_dict[obj1], rigid_body_index_dict[obj2]))
            elif obj1 in rigid_body_index_dict or obj2 in rigid_body_index_dict:
                side_joint_objects.append(obj)

        return joint_objects, joint_edge_indices, side_joint_objects

    @staticmethod
    def collect_vertices(cloth_bm: bmesh.types.BMesh, pose_bones: List[bpy.types.PoseBone], physics_mode: PhysicsMode) -> Vertices:
        vertices = Vertices()

        vert: bmesh.types.BMVert
        for vert in cloth_bm.verts:
            bone = pose_bones[vert.index]
            if not bone.bone.use_connect:
                vertices.up_verts.add(vert)
            elif bone.parent not in pose_bones:
                vertices.up_verts.add(vert)
            elif len(bone.children) == 0:
                vertices.down_verts.add(vert)
            elif bone.children[0] not in pose_bones:
                vertices.down_verts.add(vert)

            # if vert.is_wire:
            #     vertices.wire_verts.add(vert)

            if vert.select:
                vertices.hair_verts.add(vert)
                if physics_mode == PhysicsMode.AUTO:
                    vert.co = bone.tail

            if physics_mode == PhysicsMode.BONE_CONSTRAINT:
                vert.co = bone.tail

        return vertices

    @staticmethod
    def collect_edges(cloth_bm: bmesh.types.BMesh, vertices: Vertices) -> Edges:
        edges = Edges()

        for edge in cloth_bm.edges:
            if not edge.is_boundary:
                continue

            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            if vert1 in vertices.up_verts and vert2 in vertices.up_verts:
                edges.up_edges.add(edge)
            elif vert1 in vertices.down_verts and vert2 in vertices.down_verts:
                edges.down_edges.add(edge)
            else:
                edges.side_edges.add(edge)
                if edge.verts[0] not in vertices.side_verts:
                    vertices.side_verts.add(edge.verts[0])
                if edge.verts[1] not in vertices.side_verts:
                    vertices.side_verts.add(edge.verts[1])
        return edges

    @staticmethod
    def clean_mesh(mesh: bpy.types.Mesh, save_edges: List[Tuple[int, int]]):
        def remove_ngon(cloth_bm):
            # 删除大于四边的面
            # remove ngon
            for face in cloth_bm.faces:
                if len(face.verts) > 4:
                    cloth_bm.faces.remove(face)

        def remove_edges(cloth_bm: bmesh.types.BMesh, save_edges):
            # 删除多余边
            # remove extra edge
            for edge in cloth_bm.edges:
                is_save_edge = False
                for i in save_edges:
                    if edge.verts[0].index in i and edge.verts[1].index in i:
                        is_save_edge = True
                        break

                if not is_save_edge:
                    cloth_bm.edges.remove(edge)

        cloth_bm = bmesh.new()  # pylint: disable=assignment-from-no-return,invalid-name
        cloth_bm.from_mesh(mesh)
        remove_ngon(cloth_bm)
        remove_edges(cloth_bm, save_edges)
        cloth_bm.to_mesh(mesh)
        cloth_bm.free()


class PhysicsClothTunerABC(TunerABC, MeshEditor):
    pass


class PhysicsClothCottonTuner(PhysicsClothTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'PHYSICS_CLOTH_COTTON'

    @classmethod
    def get_name(cls) -> str:
        return _('Cotton')

    def execute(self):
        cloth_settings: bpy.types.ClothSettings = self.find_cloth_settings()
        cloth_settings.mass = 0.300
        cloth_settings.air_damping = 1.000
        cloth_settings.tension_stiffness = 15
        cloth_settings.compression_stiffness = 15
        cloth_settings.shear_stiffness = 15
        cloth_settings.bending_stiffness = 0.500
        cloth_settings.tension_damping = 5
        cloth_settings.compression_damping = 5
        cloth_settings.shear_damping = 5
        cloth_settings.bending_damping = 0.5


class PhysicsClothSilkTuner(PhysicsClothTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'PHYSICS_CLOTH_SILK'

    @classmethod
    def get_name(cls) -> str:
        return _('Silk')

    def execute(self):
        cloth_settings: bpy.types.ClothSettings = self.find_cloth_settings()
        cloth_settings.mass = 0.150
        cloth_settings.air_damping = 1.000
        cloth_settings.tension_stiffness = 5
        cloth_settings.compression_stiffness = 5
        cloth_settings.shear_stiffness = 5
        cloth_settings.bending_stiffness = 0.05
        cloth_settings.tension_damping = 0
        cloth_settings.compression_damping = 0
        cloth_settings.shear_damping = 0
        cloth_settings.bending_damping = 0.5


TUNERS = TunerRegistry(
    (0, PhysicsClothCottonTuner),
    (1, PhysicsClothSilkTuner),
)


class PhysicsClothAdjusterSettingsPropertyGroup(bpy.types.PropertyGroup):
    @staticmethod
    def _update_presets(prop, _):
        TUNERS[prop.presets](prop.id_data).execute()

    presets: bpy.props.EnumProperty(
        name=_('Presets'),
        items=TUNERS.to_enum_property_items(),
        update=_update_presets.__func__,
        default=None
    )

    mass: bpy.props.FloatProperty(
        name=_('Vertex Mass'), min=0, soft_max=10, step=10, unit='MASS',
        get=lambda p: MeshEditor(p.id_data).find_cloth_settings().mass,
        set=lambda p, v: setattr(MeshEditor(p.id_data).find_cloth_settings(), 'mass', v),
    )

    @staticmethod
    def _set_stiffness(prop, value):
        cloth_settings: bpy.types.ClothSettings = MeshEditor(prop.id_data).find_cloth_settings()
        cloth_settings.tension_stiffness = value
        cloth_settings.compression_stiffness = value
        cloth_settings.shear_stiffness = value

    stiffness: bpy.props.FloatProperty(
        name=_('Stiffness'), min=0, soft_max=50, max=10000, precision=3, step=10,
        get=lambda p: MeshEditor(p.id_data).find_cloth_settings().tension_stiffness,
        set=_set_stiffness.__func__,
    )

    @staticmethod
    def _set_damping(prop, value):
        cloth_settings: bpy.types.ClothSettings = MeshEditor(prop.id_data).find_cloth_settings()
        cloth_settings.tension_damping = value
        cloth_settings.compression_damping = value
        cloth_settings.shear_damping = value

    damping: bpy.props.FloatProperty(
        name=_('Damping'), min=0, max=50, precision=3, step=10,
        get=lambda p: MeshEditor(p.id_data).find_cloth_settings().tension_damping,
        set=_set_damping.__func__,
    )

    collision_quality: bpy.props.IntProperty(
        name=_('Collision Quality'), min=1, max=20,
        get=lambda p: MeshEditor(p.id_data).find_cloth_collision_settings().collision_quality,
        set=lambda p, v: setattr(MeshEditor(p.id_data).find_cloth_collision_settings(), 'collision_quality', v),
    )

    distance_min: bpy.props.FloatProperty(
        name=_('Minimum Distance'), min=0.001, max=1.000, step=10, unit='LENGTH',
        get=lambda p: MeshEditor(p.id_data).find_cloth_collision_settings().distance_min,
        set=lambda p, v: setattr(MeshEditor(p.id_data).find_cloth_collision_settings(), 'distance_min', v),
    )

    impulse_clamp: bpy.props.FloatProperty(
        name=_('Impulse Clamping'), min=0, max=100, precision=3, step=10,
        get=lambda p: MeshEditor(p.id_data).find_cloth_collision_settings().impulse_clamp,
        set=lambda p, v: setattr(MeshEditor(p.id_data).find_cloth_collision_settings(), 'impulse_clamp', v),
    )

    frame_start: bpy.props.IntProperty(
        name=_('Simulation Start'), min=0, max=1048574,
        get=lambda p: MeshEditor(p.id_data).find_cloth_modifier().point_cache.frame_start,
        set=lambda p, v: setattr(MeshEditor(p.id_data).find_cloth_modifier().point_cache, 'frame_start', v),
    )

    frame_end: bpy.props.IntProperty(
        name=_('Simulation End'), min=1, max=1048574,
        get=lambda p: MeshEditor(p.id_data).find_cloth_modifier().point_cache.frame_end,
        set=lambda p, v: setattr(MeshEditor(p.id_data).find_cloth_modifier().point_cache, 'frame_end', v),
    )

    def __eq__(self, obj):
        return (
            isinstance(obj, PhysicsClothAdjusterSettingsPropertyGroup)
            and self.presets == obj.presets
            and self.mass == obj.mass
            and self.stiffness == obj.stiffness
            and self.damping == obj.damping
            and self.collision_quality == obj.collision_quality
            and self.distance_min == obj.distance_min
            and self.impulse_clamp == obj.impulse_clamp
            and self.frame_start == obj.frame_start
            and self.frame_end == obj.frame_end
        )

    def __ne__(self, obj):
        return not self == obj

    @staticmethod
    def register():
        # pylint: disable=assignment-from-no-return
        bpy.types.Object.mmd_uuunyaa_tools_cloth_settings = bpy.props.PointerProperty(type=PhysicsClothAdjusterSettingsPropertyGroup)

    @staticmethod
    def unregister():
        del bpy.types.Object.mmd_uuunyaa_tools_cloth_settings
