# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy

from mmd_uuunyaa_tools import REGISTER_HOOKS
from mmd_uuunyaa_tools.utilities import get_preferences


def initialize_mmd_tools_translation():
    preferences = get_preferences()

    if preferences.mmd_tools_translation_enabled:
        bpy.app.translations.register(__name__, translation_dict)


REGISTER_HOOKS.append(initialize_mmd_tools_translation)

translation_dict = {
    "ja_JP": {
        ("Operator", "Create Model"): "モデルを作成",
        ("Operator", "Create a MMD Model Root Object"): "MMDモデルルートオブジェクトを作成",

        ("Operator", "Convert Model"): "モデルを変換",
        ("Operator", "Convert to a MMD Model"): "MMDモデルへ変換",
        ("*", "Ambient Color Source"): "アンビエントカラーソース",
        ("*", "Edge Threshold"): "輪郭しきい値",
        ("*", "Minimum Edge Alpha"): "最小輪郭アルファ",

        ("Operator", "Convert Materials For Cycles"): "マテリアルをCycles用に変換",
        ("Operator", "Separate By Materials"): "マテリアルで分解",
        ("Operator", "Join Meshes"): "メッシュを統合",
        ("Operator", "Attach Meshes to Model"): "メッシュをモデルに取付",
        ("Operator", "Translation"): "翻訳",

        ("*", "Bone Constraints:"): "ボーンコンストレイント:",
        ("*", "Physics:"): "物理演算:",
        ("Operator", "Build"): "構築",
        ("*", "Edge Preview:"): "輪郭プレビュー:",
        ("*", "Create"): "生成",
        ("*", "Clean"): "クリーン",
        ("*", "Model:"): "モデル:",

        ("*", "Types"): "タイプ",
        ("*", "Morphs"): "モーフ",
        ("*", "Clean Model"): "モデルをクリーン",
        ("*", "Fix IK Links"): "IKリンクを修正",
        ("*", "Apply Bone Fixed Axis"): "ボーン修正回転軸を適用",
        ("*", "Rename Bones - L / R Suffix"): "ボーンをリネーム - L / R接尾辞",
        ("*", "Rename Bones - Use Underscore"): "ボーンをリネーム - アンダースコア使用",
        ("*", "Rename Bones To English"): "ボーンを英語にリネーム",
        ("*", "Internal Dictionary"): "内蔵辞書",
        ("*", "use MIP maps for UV textures"): "UVテクスチャへミップマップを使用",
        ("*", "influence of .sph textures"): ".sphテクスチャの影響度",
        ("*", "influence of .spa textures"): ".spaテクスチャの影響度",
        ("*", "Log level"): "ログレベル",
        ("*", "Create a log file"): "ログファイルを作成",
        ("*", "Copy textures"): "テクスチャをコピー",
        ("*", "Sort Materials"): "マテリアルをソート",
        ("*", "Disable SPH/SPA"): "SPH/SPAを無効化",
        ("*", "Visible Meshes Only"): "可視メッシュのみ",
        ("*", "Sort Vertices"): "頂点をソート",

        ("*", "Motion:"): "モーション:",
        ("*", "Bone Mapper"): "ボーンマッパー",
        ("*", "Renamed bones"): "リネームしたボーン",
        ("*", "Treat Current Pose as Rest Pose"): "現在のポーズをレストポーズとして処理",
        ("*", "Mirror Motion"): "モージョンをミラー",
        ("*", "Update scene settings"): "シーン設定を更新",
        ("*", "Use Frame Range"): "フレーム範囲を使用",

        ("*", "Pose:"): "ポーズ:",
        ("*", "Current Pose"): "現在のポーズ",
        ("*", "Active Pose"): "アクティブなポーズ",
        ("*", "All Poses"): "全てのポーズ",

        ("*", "Display Panel"): "表示パネル",
        ("Operator", "Bone"): "ボーン",
        ("Operator", "Morph"): "モーフ",
        ("*", "Load Facial Items"): "表情項目をロード",
        ("*", "Load Bone Groups"): "ボーングループをロード",
        ("*", "Apply Bone Groups"): "ボーングループを適用",
        ("Operator", "Move To Top"): "最初へ移動",
        ("Operator", "Move To Bottom"): "最後へ移動",
        ("Operator", "Delete All"): "全て削除",

        ("*", "Morph Tools"): "モーフツール",
        ("*", "Eye"): "目",
        ("*", "Eye Brow"): "眉毛",
        ("*", "Mouth"): "口",
        ("Operator", "Copy Morph"): "モーフをコピー",
        ("*", "Rigid Bodies"): "リジッドボディ",
        ("*", "Active Model"): "選択中のモデル",
        ("*", "All Models"): "全てのモデル",
        ("Operator", "Select Similar..."): "類似を選択...",
        ("*", "Collision Group"): "コリジョングループ",
        ("*", "Collision Group Mask"): "コリジョングループマスク",
        ("*", "Rigid Type"): "リジッドタイプ",
        ("*", "Hide Others"): "他を隠す",

        ("*", "Material Sorter"): "マテリアルソーター",
        ("*", "Select a mesh object"): "メッシュを選択してください",
        ("*", "Use the arrows to sort"): "矢印を使って並べ替えてください",

        ("*", "Meshes Sorter"): "メッシュソーター",
        ("*", "Select a MMD Model"): "MMDモデルを選択してください",

        ("*", "Bone Order"): "ボーン順序",
        ("*", "Select a MMD Model"): "MMDモデルを選択してください",
        ("*", "After Dynamics"): "物理演算後",
        ("*", "Transform Order"): "変形順序",

        ("*", "MMD Display"): "MMD表示",
        ("*", "Temporary Object"): "テンポラリオブジェクト",
        ("*", "Rigid Body Name"): "リジッドボティ名",
        ("*", "Joint"): "ジョイント",
        ("*", "Joint Name"): "ジョイント名",
        ("*", "Toon Texture"): "トゥーンテクスチャ",
        ("*", "Sphere Texture"): "スフィアテクスチャ",
        ("*", "Property Drivers"): "プロパティドライバー",

        ("*", "MMD Shading"): "MMDシェーディング",
        ("Operator", "Shadeless"): "影なし",

        ("*", "MMD SDEF Driver"): "MMD SDEFドライバー",
        ("Operator", "Bind"): "バインド",
        ("Operator", "Unbind"): "アンバインド",
        ("*", "Bind SDEF Driver"): "SDEFドライバーをバインド",
        ("*", "- Auto -"): "自動",
        ("*", "Bulk"): "バルク",
        ("*", "Skip"): "スキップ",

        ("*", "MMD Model Information"): "MMDモデル情報",
        ("Operator", "Change MMD IK Loop Factor"): "MMD IK反復係数を変更",
        ("*", "MMD IK Loop Factor"): "MMD IK反復係数",
        ("Operator", "Recalculate bone roll"): "ボーンロールを再計算",
        ("*", "This operation will break existing f-curve/action."): "この操作は既存のFカーブ/アクションを破壊します。",
        ("*", "Click [OK] to run the operation."): "[OK]をクリックして操作を実行してください。",

        ("*", "MMD Material"): "MMDマテリアル",
        ("*", "Color:"): "カラー:",
        ("*", "Shadow:"): "シャドウ:",
        ("*", "Double Sided"): "両面表示",
        ("*", "Ground Shadow"): "地面シャドウ",
        ("*", "Self Shadow Map"): "セルフシャドウマップ",
        ("*", "Self Shadow"): "セルフシャドウ",
        ("*", "Toon Edge"): "トゥーン輪郭",
        ("*", "Edge Color"): "輪郭カラー",
        ("*", "Edge Weight"): "輪郭ウェイト",

        ("*", "MMD Texture"): "MMDテクスチャ",
        ("*", "Texture:"): "テクスチャ:",
        ("*", "Sphere Texture:"): "スフィアテクスチャ:",
        ("*", "SubTexture"): "サブテクスチャ",
        ("*", "Use Shared Toon Texture"): "共有トゥーンテクスチャを使用",
        ("*", "Shared Toon Texture"): "共有トゥーンテクスチャ",

        ("*", "MMD Bone Tools"): "MMDボーンツール",
        ("*", "Information:"): "情報:",
        ("*", "Controllable"): "操作可能",
        ("*", "Tip Bone"): "ティップボーン",
        ("*", "Fixed Axis"): "回転軸固定",
        ("*", "Local Axes"): "ローカル回転軸",
        ("*", "Local X-Axis"): "ローカルX軸",
        ("*", "Local Z-Axis"): "ローカルZ軸",
        ("*", "Rotate +"): "回転 +",
        ("*", "Move +"): "移動 +",

        # Shader Nodes
        ("*", "Base Tex Fac"): "ベーステクスチャ係数",
        ("*", "Base Tex"): "ベーステクスチャ",
        ("*", "Base Alpha"): "ベースアルファ",
        ("*", "Base UV"): "ベースUV",
        ("*", "Toon Tex Fac"): "トゥーンテクスチャ係数",
        ("*", "Toon Tex"): "トゥーンテクスチャ",
        ("*", "Toon Alpha"): "トゥーンアルファ",
        ("*", "Toon UV"): "トゥーンUV",
        ("*", "Sphere Tex Fac"): "スフィアテクスチャ係数",
        ("*", "Sphere Tex"): "スフィアテクスチャ",
        ("*", "Sphere Alpha"): "スフィアアルファ",
        ("*", "Sphere UV"): "スフィアUV",
        ("*", "Sphere Mul/Add"): "スフィア 乗算/加算",
        ("*", "SubTex UV"): "サブテクスチャUV",
    },
}
