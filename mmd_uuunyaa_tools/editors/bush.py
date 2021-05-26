# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
import random
from typing import Iterable, List, Tuple

import bpy
import bpy_extras
from mathutils import Quaternion, Vector


def create_bush(
    length: float,
    width: float,
    height: float,
    max_bend_angle: float,
    number_of_cuts: int,
    length_around_factor: float,
    pitch: float,
    fluctuation: float,
    thickness: float,
    segments: int,
) -> Tuple[List[Vector], List[Tuple[int, int, int, int]]]:
    vertices: List[Vector] = []
    faces: List[Tuple[int, int, int, int]] = []

    segment_cos = [math.cos(i * math.pi * 2 / segments) for i in range(segments)]
    segment_sin = [math.sin(i * math.pi * 2 / segments) for i in range(segments)]

    def sprout(position: Vector, length: float):

        quaternion = Quaternion()
        vertices.extend(calc_edge_vertices(position, quaternion, thickness, 0))

        for cut_count in range(1, number_of_cuts+1):
            theta = random.random() * math.pi * 2
            quaternion @= Quaternion(  # pylint: disable=too-many-function-args
                [math.cos(theta), 0, math.sin(theta)],
                random.random() * max_bend_angle
            )

            cut_radius = thickness * (1 - cut_count / number_of_cuts)
            cut_length = length / number_of_cuts

            vertices.extend(calc_edge_vertices(position, quaternion, cut_radius, cut_length))
            vertex_count = len(vertices)

            faces.extend([
                (v1, v2, v4, v3)
                for (v1, v2), (v3, v4)
                in zip(
                    sliding(range(vertex_count-2*segments, vertex_count-1*segments)),
                    sliding(range(vertex_count-1*segments, vertex_count-0*segments))
                )
            ])

            position += quaternion @ Vector([0, length / number_of_cuts, 0])

    def sliding(target: List[int]) -> Iterable[Tuple[int, int]]:
        for i in range(len(target)-1):
            yield (target[i], target[i+1])

        yield (target[-1], target[0])

    def calc_edge_vertices(origin: Vector, rotation: Quaternion, radius: float, length: float) -> List[Vector]:
        return [
            origin + rotation @ Vector([radius * segment_cos[i], length, radius * segment_sin[i]])
            for i in range(segments)
        ]

    def frange(start: float, stop: float, step: float = 1.0) -> Iterable[float]:
        if step == 0:
            return

        value = start

        if step > 0:
            count: int = 0
            while value < stop:
                value = float(start + count * step)
                yield value
                count += 1
        else:
            count: int = 0
            while value > stop:
                value = float(start + count * step)
                yield value
                count += 1

    for xpos in frange(-width/2, +width/2, pitch):
        xpos_factor = 1-(2*xpos/width)**2 * (1-length_around_factor)
        for zpos in frange(-height/2, +height/2, pitch):
            zpos_factor = 1-(2*zpos/height)**2 * (1-length_around_factor)
            theta = random.random() * math.pi * 2
            band = random.random() * fluctuation
            sprout(Vector([
                xpos + band * math.cos(theta),
                0,
                zpos + band * math.sin(theta)
            ]), length * xpos_factor * zpos_factor)
    return vertices, faces


class AddBushMesh(bpy.types.Operator, bpy_extras.object_utils.AddObjectHelper):
    bl_idname = 'mmd_uuunyaa_tools.add_bush_mesh'
    bl_label = 'Bush'
    bl_description = 'Construct a bush mesh'
    bl_options = {'REGISTER', 'UNDO'}

    length: bpy.props.FloatProperty(default=0.04, min=0.0, precision=2, unit='LENGTH')
    width: bpy.props.FloatProperty(default=0.006, min=0.0, precision=4, unit='LENGTH')
    height: bpy.props.FloatProperty(default=0.025, min=0.0, precision=4, unit='LENGTH')
    max_bend_angle: bpy.props.FloatProperty(default=math.pi / 4, min=-math.pi, max=+math.pi, unit='ROTATION')
    number_of_cuts: bpy.props.IntProperty(default=20, min=1)
    length_around_factor: bpy.props.FloatProperty(default=1.0, min=0.0, precision=2)
    pitch: bpy.props.FloatProperty(default=0.001, min=0.0, precision=5, unit='LENGTH')
    fluctuation: bpy.props.FloatProperty(default=0.0004, min=0.0, precision=4, unit='LENGTH')
    thickness: bpy.props.FloatProperty(default=0.00004, min=0.0, precision=5, unit='LENGTH')
    segments: bpy.props.IntProperty(default=3, min=3)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context: bpy.types.Context):
        verts, faces = create_bush(
            self.length,
            self.width,
            self.height,
            self.max_bend_angle,
            self.number_of_cuts,
            self.length_around_factor,
            self.pitch,
            self.fluctuation,
            self.thickness,
            self.segments,
        )
        mesh = bpy.data.meshes.new('Bush')
        mesh.from_pydata(verts, [], faces)
        bpy_extras.object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


class VIEW3D_MT_uuunyaa_mesh_extras(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_uuunyaa_mesh_extras"
    bl_label = "UuuNyaa"

    def draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.operator(AddBushMesh.bl_idname, text='Bush')

    @staticmethod
    def draw_menu(this, _):
        this.layout.menu(VIEW3D_MT_uuunyaa_mesh_extras.bl_idname, text='UuuNyaa Extras')

    @staticmethod
    def register():
        bpy.types.VIEW3D_MT_mesh_add.append(VIEW3D_MT_uuunyaa_mesh_extras.draw_menu)

    @staticmethod
    def unregister():
        bpy.types.VIEW3D_MT_mesh_add.remove(VIEW3D_MT_uuunyaa_mesh_extras.draw_menu)
