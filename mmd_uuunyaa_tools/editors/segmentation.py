# -*- coding: utf-8 -*-
# Copyright 2023 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.


import bisect
import collections
import dataclasses
import itertools
import math
import random
import sys
from typing import Dict, List, Optional, Set, Tuple

import bmesh
import bpy
import mathutils


def _to_blender_color(uint8_color: int) -> float:
    color: float = min(max(0, uint8_color), 255) / 255
    return color
    return color / 12.92 if color < 0.04045 else math.pow((color + 0.055) / 1.055, 2.4)


RGBA = Tuple[float, float, float, float]
SEGMANTATION_COLORS: List[RGBA] = [
    (
        _to_blender_color(0xff & (rgb >> 16)),  # Red
        _to_blender_color(0xff & (rgb >> 8)),  # Blue
        _to_blender_color(0xff & (rgb)),  # Green
        1.0,  # Alpha
    )
    for rgb in [
        0xff0000, 0xffa300, 0xff6600, 0xc2ff00, 0x008fff, 0x33ff00, 0x0052ff, 0x00ff29,
        0x00ffad, 0x0a00ff, 0xadff00, 0x00ff99, 0xff5c00, 0xff00ff, 0xff00f5, 0xff0066,
        0xffad00, 0xff0014, 0xffb8b8, 0x001fff, 0x00ff3d, 0x0047ff, 0xff00cc, 0x00ffc2,
        0x00ff52, 0x000aff, 0x0070ff, 0x3300ff, 0x00c2ff, 0x007aff, 0x00ffa3, 0xff9900,
        0x00ff0a, 0xff7000, 0x8fff00, 0x5200ff, 0xa3ff00, 0xffeb00, 0x08b8aa, 0x8500ff,
        0x00ff5c, 0xb800ff, 0xff001f, 0x00b8ff, 0x00d6ff, 0xff0070, 0x5cff00, 0x00e0ff,
        0x70e0ff, 0x46b8a0, 0xa300ff, 0x9900ff, 0x47ff00, 0xff00a3, 0xffcc00, 0xff008f,
        0x00ffeb, 0x85ff00, 0xff00eb, 0xf500ff, 0xff007a, 0xfff500, 0x0abed4, 0xd6ff00,
        0x00ccff, 0x1400ff, 0xffff00, 0x0099ff, 0x0029ff, 0x00ffcc, 0x2900ff, 0x29ff00,
        0xad00ff, 0x00f5ff, 0x4700ff, 0x7a00ff, 0x00ffb8, 0x005cff, 0xb8ff00, 0x0085ff,
        0xffd600, 0x19c2c2, 0x66ff00, 0x5c00ff,
    ]
]

TriLoopIndex = int
LoopPairId = int
VertexPairId = int
VertexIndex = int
VertexGroupPairId = int
SegmentContactId = int
SegmentPairId = int


@dataclasses.dataclass
class Segment:
    index: int
    area: float = 0.0
    tri_loop0s: Set[bmesh.types.BMLoop] = dataclasses.field(default_factory=set)
    segment_contact_ids: Set[SegmentContactId] = dataclasses.field(default_factory=set)

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index


@dataclasses.dataclass
class SegmentContact:
    index: SegmentContactId
    cost: float
    cost_normalized: float
    length: float
    segment0: Segment
    segment1: Segment

    def segment_contacts(self, segment: Segment) -> bool:
        return self.segment0 == segment or self.segment1 == segment

    def segment_replace(self, src: Segment, dst: Segment) -> bool:
        if self.segment0 == src:
            self.segment0 = dst
            if self.segment1 == src:
                self.segment1 = dst
            return True
        if self.segment1 == src:
            self.segment1 = dst
            return True
        return False

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index


@dataclasses.dataclass
class SegmentResult:
    segments: Set[Segment]
    remain_segment_contacts: List[SegmentContact]
    last_merged_cost: float
    tri_loops: List[bmesh.types.BMLoop]


def _to_loop_pair_id(loop0: bmesh.types.BMLoop, loop1: bmesh.types.BMLoop, loop_pair_shift: int) -> LoopPairId:
    loop0_index = loop0.index
    loop1_index = loop1.index
    if loop0_index > loop1_index:
        return loop1_index + (loop0_index << loop_pair_shift)
    return loop0_index + (loop1_index << loop_pair_shift)


def _to_vertex_pair_id(vert0: bmesh.types.BMVert, vert1: bmesh.types.BMVert, vertex_pair_shift: int) -> VertexPairId:
    vert0_index = vert0.index
    vert1_index = vert1.index
    if vert0_index > vert1_index:
        return vert1_index + (vert0_index << vertex_pair_shift)
    return vert0_index + (vert1_index << vertex_pair_shift)


def _to_segment_pair_id(segment0: Segment, segment1: Segment, segment_pair_shift: int) -> SegmentPairId:
    segment0_index = segment0.index
    segment1_index = segment1.index
    if segment0_index > segment1_index:
        return segment1_index + (segment0_index << segment_pair_shift)
    return segment0_index + (segment1_index << segment_pair_shift)


def _to_tri_loop_index(loop: bmesh.types.BMLoop) -> TriLoopIndex:
    li0 = loop.index
    li1 = loop.link_loop_next.index
    li2 = loop.link_loop_prev.index

    # return min(i0, i1, i2)
    if li0 > li1:
        if li1 > li2:
            return li2
        return li1
    if li0 > li2:
        return li2
    return li0


def _get_cost_normalized(segment_contact: SegmentContact) -> float:
    return segment_contact.cost_normalized


def _setup_output_aov(node_tree: bpy.types.NodeTree, segmentation_output_aov_name: str):
    nodes = node_tree.nodes
    segmentation_output_aov_node: Optional[bpy.types.ShaderNodeOutputAOV] = next((n for n in nodes if n.type == 'OUTPUT_AOV' and n.name == segmentation_output_aov_name), None)
    if segmentation_output_aov_node is None:
        segmentation_output_aov_node = nodes.new(type=bpy.types.ShaderNodeOutputAOV.__name__)
        segmentation_output_aov_node.name = segmentation_output_aov_name
        segmentation_output_aov_node.location = (300, 600)

    if len(segmentation_output_aov_node.inputs['Color'].links) > 0:
        return

    segmentation_vertex_color_node: bpy.types.ShaderNodeVertexColor = nodes.new(type=bpy.types.ShaderNodeVertexColor.__name__)
    segmentation_vertex_color_node.layer_name = segmentation_output_aov_name
    segmentation_vertex_color_node.location = (0, 600)
    node_tree.links.new(
        segmentation_vertex_color_node.outputs[0],
        segmentation_output_aov_node.inputs[0]
    )


def auto_segment(
    target_bmesh: bmesh.types.BMesh,
    cost_threshold: float,
    maximum_area_threshold: float,
    minimum_area_threshold: float,
    contact_length_factor: float,
    face_angle_cost_factor: float,
    vertex_group_weight_cost_factor: float,
    vertex_group_change_cost_factor: float,
    material_change_cost_factor: float,
    edge_sharp_cost_factor: float,
    edge_seam_cost_factor: float,
    ignore_vertex_group_indices: Set[int],
) -> SegmentResult:
    tri_loops = target_bmesh.calc_loop_triangles()
    sci2segment_contacts, segment_count = _calc_segment_contacts(
        contact_length_factor,
        face_angle_cost_factor,
        vertex_group_weight_cost_factor,
        vertex_group_change_cost_factor,
        material_change_cost_factor,
        edge_sharp_cost_factor,
        edge_seam_cost_factor,
        _calc_vi2vgi2weights(target_bmesh, ignore_vertex_group_indices),
        target_bmesh,
        tri_loops
    )

    if segment_count == 0:
        return SegmentResult(set(), [], 0.0, [])

    segment_pair_shift = int(math.log2(segment_count) / 2 + 1)

    cost_sorted_segment_contacts = sorted(sci2segment_contacts.values(), key=_get_cost_normalized)

    def _remove_segment_contact(sci: SegmentContactId):
        sc = sci2segment_contacts.pop(sci)
        sc.segment0.segment_contact_ids.discard(sci)
        sc.segment1.segment_contact_ids.discard(sci)
        for i in range(bisect.bisect_left(cost_sorted_segment_contacts, sc.cost_normalized, key=_get_cost_normalized), len(cost_sorted_segment_contacts)):
            if sc != cost_sorted_segment_contacts[i]:
                continue
            del cost_sorted_segment_contacts[i]
            return

    result_segments: Set[Segment] = set()
    result_loop_count: int = 0

    last_merged_cost: float = 0

    merging = True
    while merging:

        merging = False

        for segment_contact in cost_sorted_segment_contacts:
            sci = segment_contact.index

            cost = segment_contact.cost_normalized
            if cost > cost_threshold:
                break

            dst_segment = segment_contact.segment0
            src_segment = segment_contact.segment1

            src_segment_area = src_segment.area
            if src_segment_area > minimum_area_threshold and dst_segment.area + src_segment_area > maximum_area_threshold:
                continue

            merging = True
            last_merged_cost = cost

            dst_segment.tri_loop0s.update(src_segment.tri_loop0s)
            dst_segment.area += src_segment_area

            _remove_segment_contact(sci)

            dst_segment_contact_ids = dst_segment.segment_contact_ids
            src_segment_contact_ids = src_segment.segment_contact_ids
            for src_sci in list(src_segment_contact_ids):
                sc = sci2segment_contacts[src_sci]
                if sc.segment_replace(src_segment, dst_segment):
                    if sc.segment0 == sc.segment1:
                        _remove_segment_contact(src_sci)
                    else:
                        dst_segment_contact_ids.add(src_sci)
                        src_segment_contact_ids.discard(src_sci)

            if len(dst_segment_contact_ids) == 0:
                # dst_segment is isolated
                result_segments.add(dst_segment)
                result_loop_count += len(dst_segment.tri_loop0s)
                continue

            # collect mergable segment contacts
            spi2mergable_segment_contacts: Dict[SegmentPairId, Set[SegmentContact]] = collections.defaultdict(set)
            for edge_sci in dst_segment_contact_ids:
                sc = sci2segment_contacts[edge_sci]
                spi = _to_segment_pair_id(sc.segment0, sc.segment1, segment_pair_shift)
                spi2mergable_segment_contacts[spi].add(sc)

            # merge mergable segment contacts
            for mergable_segment_contacts in spi2mergable_segment_contacts.values():
                if len(mergable_segment_contacts) <= 1:
                    continue

                mergable_segment_contacts_iter = iter(mergable_segment_contacts)
                merged_sc = next(mergable_segment_contacts_iter)
                for sc in mergable_segment_contacts_iter:
                    merged_sc.cost += sc.cost
                    merged_sc.length += sc.length
                    _remove_segment_contact(sc.index)

                for i in range(bisect.bisect_left(cost_sorted_segment_contacts, merged_sc.cost_normalized, key=_get_cost_normalized), len(cost_sorted_segment_contacts)):
                    if merged_sc != cost_sorted_segment_contacts[i]:
                        continue
                    break

                # update the cost and then sort cost_sorted_segment_contacts
                merged_sc.cost_normalized = merged_sc.cost / (merged_sc.length * contact_length_factor if contact_length_factor > 0 else 1)
                bisect.insort_left(
                    cost_sorted_segment_contacts,
                    cost_sorted_segment_contacts.pop(i),
                    key=_get_cost_normalized
                )

            # since the cost has been updated, it must enter a new loop to follow the sort results.
            break

    result_segments.update({
        s
        for sc in cost_sorted_segment_contacts
        for s in (sc.segment0, sc.segment1)
    })

    return SegmentResult(result_segments, cost_sorted_segment_contacts, last_merged_cost, tri_loops)


def get_color_layer(target_bmesh: bmesh.types.BMesh, segmentation_vertex_color_attribute_name: str) -> bmesh.types.BMLayerItem:
    return (
        target_bmesh.loops.layers.color[segmentation_vertex_color_attribute_name]
        if segmentation_vertex_color_attribute_name in target_bmesh.loops.layers.color
        else target_bmesh.loops.layers.color.new(segmentation_vertex_color_attribute_name)
    )


def assign_vertex_colors(
        segments: Set[Segment],
        color_layer: bmesh.types.BMLayerItem,
        segmentation_vertex_color_random_seed: int,
):
    segmantation_colors = SEGMANTATION_COLORS.copy()
    segmantation_color_count = len(segmantation_colors)

    if segmentation_vertex_color_random_seed != 0:
        rng = random.Random(segmentation_vertex_color_random_seed)
        rng.shuffle(segmantation_colors)

    for index, segment in enumerate(segments):
        segmentation_color = segmantation_colors[index % segmantation_color_count]
        for tri_loop0 in segment.tri_loop0s:
            tri_loop0[color_layer] = segmentation_color
            tri_loop0.link_loop_prev[color_layer] = segmentation_color
            tri_loop0.link_loop_next[color_layer] = segmentation_color


def paint_selected_face_colors(
        mesh_object: bpy.types.Object,
        color: Optional[RGBA],
        segmentation_vertex_color_attribute_name: str
):
    target_bmesh: bmesh.types.BMesh = bmesh.new()
    mesh: bpy.types.Mesh = mesh_object.data
    target_bmesh.from_mesh(mesh, face_normals=False, vertex_normals=False)
    color_layer = get_color_layer(target_bmesh, segmentation_vertex_color_attribute_name)

    if color is None:
        color = random.choice(SEGMANTATION_COLORS)

    tri_loops = target_bmesh.calc_loop_triangles()
    tri_loop: List[bmesh.types.BMLoop]
    for tri_loop in tri_loops:
        if not tri_loop[0].face.select:
            continue

        for loop in tri_loop:
            loop[color_layer] = color

    target_bmesh.to_mesh(mesh)


def setup_materials(mesh: bpy.types.Mesh, segmentation_vertex_color_attribute_name: str):
    for material in mesh.materials:
        _setup_output_aov(material.node_tree, segmentation_vertex_color_attribute_name)


def setup_aovs(aovs: bpy.types.AOVs, segmentation_vertex_color_attribute_name: str):
    if segmentation_vertex_color_attribute_name in aovs:
        return

    aov = aovs.add()
    aov.name = segmentation_vertex_color_attribute_name


def _calc_segment_contacts(
    contact_length_factor: float,
    face_angle_cost_factor: float,
    vertex_group_weight_cost_factor: float,
    vertex_group_change_cost_factor: float,
    material_change_cost_factor: float,
    edge_sharp_cost_factor: float,
    edge_seam_cost_factor: float,
    vi2vgi2weights: Dict[int, Dict[int, float]],
    target_bmesh: bmesh.types.BMesh,
    tri_loops: List[bmesh.types.BMLoop],
) -> Tuple[Dict[SegmentContactId, SegmentContact], int]:
    vertex_count = len(target_bmesh.verts)
    vertex_pair_shift = int(math.log2(vertex_count) / 2 + 1)

    vpi2weights: Dict[VertexPairId, float] = {}

    def _calc_vertex_group_weight_cost(vert0: bmesh.types.BMVert, vert1: bmesh.types.BMVert) -> float:
        vpi = _to_vertex_pair_id(vert0, vert1, vertex_pair_shift)
        if vpi in vpi2weights:
            return vpi2weights[vpi]

        vgi2weights0 = vi2vgi2weights[vert0.index]
        vgi2weights1 = vi2vgi2weights[vert1.index]

        weight = 0.0
        for vgi0, weight0 in vgi2weights0.items():
            weight += abs(weight0 - vgi2weights1.get(vgi0, 0.0))

        for vgi1, weight1 in vgi2weights1.items():
            weight += abs(weight1 - vgi2weights0.get(vgi1, 0.0))

        return vpi2weights.setdefault(vpi, weight)

    tli2heaviest_vgi: Dict[TriLoopIndex, int] = {}

    def _calc_heaviest_vertex_group_index(tli: TriLoopIndex, loop: bmesh.types.BMLoop) -> int:
        if tli in tli2heaviest_vgi:
            return tli2heaviest_vgi[tli]

        max_vgi: int = -1
        max_weight: float = -1.0
        vgi2weights: Dict[int, float] = {}
        for vgi, weight in itertools.chain(
            vi2vgi2weights[loop.vert.index].items(),
            vi2vgi2weights[loop.link_loop_next.vert.index].items(),
            vi2vgi2weights[loop.link_loop_prev.vert.index].items()
        ):
            weight += vgi2weights.get(vgi, 0)
            if weight > max_weight:
                max_vgi = vgi
                max_weight = weight
            vgi2weights[vgi] = weight
        return tli2heaviest_vgi.setdefault(tli, max_vgi)

    # loop_pair_id
    processed_loop_pair_ids: Set[LoopPairId] = set()

    __next_segment_id: int = 0

    def _new_segment():
        nonlocal __next_segment_id
        __next_segment_id += 1
        return Segment(__next_segment_id)

    loop_count = 3 * len(tri_loops)
    loop_pair_shift = int(math.log2(loop_count) / 2 + 1)

    # tri_loop_index to segment map
    tli2segment: Dict[TriLoopIndex, Segment] = collections.defaultdict(_new_segment)

    # segment_contact_index to segment_contact map
    sci2segment_contacts: Dict[SegmentContactId, SegmentContact] = {}

    half_pi_inverse = 2 / math.pi

    next_segment_contact_id: SegmentContactId = 0

    tri_loop: List[bmesh.types.BMLoop]
    for tri_loop in tri_loops:
        tri_loop0 = tri_loop[0]
        this_face = tri_loop0.face

        if not this_face.select:
            continue

        this_tli = _to_tri_loop_index(tri_loop0)
        this_heaviest_vertex_group_index = _calc_heaviest_vertex_group_index(this_tli, tri_loop0)

        this_segment = tli2segment[this_tli]
        this_segment.area = mathutils.geometry.area_tri(tri_loop0.vert.co, tri_loop[1].vert.co, tri_loop[2].vert.co)  # pylint: disable=assignment-from-no-return
        this_segment.tri_loop0s.add(tri_loop0)

        for this_loop in tri_loop:
            edge_length = -1
            that_loop = this_loop
            while (that_loop := that_loop.link_loop_radial_next) != this_loop:
                lpi = _to_loop_pair_id(this_loop, that_loop, loop_pair_shift)
                if lpi in processed_loop_pair_ids:
                    continue
                processed_loop_pair_ids.add(lpi)

                that_face = that_loop.face
                if not that_face.select:
                    continue

                if edge_length < 0:
                    this_edge = this_loop.edge
                    edge_length = this_edge.calc_length()
                    this_verts = this_edge.verts
                    vert0 = this_verts[0]
                    vert1 = this_verts[1]
                    this_vert2 = this_loop.link_loop_prev.vert

                    this_loop_vertex_group_weight_cost = _calc_vertex_group_weight_cost(vert0, this_vert2) + _calc_vertex_group_weight_cost(vert1, this_vert2)
                    this_loop_edge_sharp_cost = (0 if this_edge.smooth else 1)
                    this_loop_edge_seam_cost = (1 if this_edge.seam else 0)

                    # cost:sharp = 1:1
                    cost_edge_sharp = edge_length * this_loop_edge_sharp_cost

                    # cost:seam = 1:1
                    cost_edge_seam = edge_length * this_loop_edge_seam_cost

                that_tli = _to_tri_loop_index(that_loop)
                that_heaviest_vertex_group_index = _calc_heaviest_vertex_group_index(that_tli, that_loop)
                that_vert2 = that_loop.link_loop_prev.vert
                that_segment = tli2segment[that_tli]

                # cost:vertex weight = 1:1
                cost_vertex_group_weight = edge_length * 0.25 * (this_loop_vertex_group_weight_cost + _calc_vertex_group_weight_cost(vert0, that_vert2) + _calc_vertex_group_weight_cost(vert1, that_vert2))

                # cost:vertex group change = 1:1
                cost_vertex_group_change = edge_length * (0 if this_heaviest_vertex_group_index == that_heaviest_vertex_group_index else 1)

                # cost:angle = 1:90 degrees
                cost_face_angle = edge_length * half_pi_inverse * this_loop.calc_normal().angle(that_loop.calc_normal())

                # cost:material = 1:1
                cost_material_change = edge_length * (0 if this_face.material_index == that_face.material_index else 1)

                cost_total = sum((
                    vertex_group_weight_cost_factor * cost_vertex_group_weight,
                    vertex_group_change_cost_factor * cost_vertex_group_change,
                    face_angle_cost_factor * cost_face_angle,
                    material_change_cost_factor * cost_material_change,
                    edge_sharp_cost_factor * cost_edge_sharp,
                    edge_seam_cost_factor * cost_edge_seam,
                ))

                segment_contact = SegmentContact(
                    next_segment_contact_id := next_segment_contact_id+1,
                    cost_total,
                    cost_total/(edge_length * contact_length_factor if contact_length_factor > 0 else 1),
                    edge_length,
                    this_segment,
                    that_segment
                )
                sci2segment_contacts[segment_contact.index] = segment_contact
                this_segment.segment_contact_ids.add(segment_contact.index)
                that_segment.segment_contact_ids.add(segment_contact.index)

    return sci2segment_contacts, len(tli2segment)


def _calc_vi2vgi2weights(target_bmesh: bmesh.types.BMesh, ignore_vertex_group_indices: Set[int]) -> Dict[int, Dict[int, float]]:
    deform_layer = target_bmesh.verts.layers.deform.verify()
    return {
        v.index: {
            vgi: weight
            for vgi, weight in v[deform_layer].items()
            if vgi not in ignore_vertex_group_indices
        }
        for v in target_bmesh.verts
    }


def get_ignore_vertex_group_indices(mesh_object: bpy.types.Object) -> Set[int]:
    deform_bone_names = {
        b.name
        for m in mesh_object.modifiers
        if m.is_active and m.type == 'ARMATURE'
        for b in m.object.data.bones
        if b.use_deform
    }

    ignore_vertex_group_indices = {
        vg.index
        for vg in mesh_object.vertex_groups
        if vg.name in deform_bone_names
    }
    return ignore_vertex_group_indices
