"""
ファイル名のマッピング管理
日本語ファイル名と実際のファイル名の対応を管理
"""

# ファイル名のマッピング（表示名 -> 実際のファイル名）
FILE_NAME_MAPPING = {
    "材料：記事化希望箇所.doc": "materal_.doc",
    "企画：6JNETS記録集_企画案v2.docx": "plan.docx",
    "材料：JNETS記録集_資材化スライド候補.pptx": "material_slide.pptx",
    "材料：20180908_LS富士フイルムRI.mp3": "voice_material.mp3",
}

# 逆マッピング（実際のファイル名 -> 表示名）
REVERSE_FILE_NAME_MAPPING = {v: k for k, v in FILE_NAME_MAPPING.items()}


def get_actual_filename(display_name: str) -> str:
    """表示名から実際のファイル名を取得"""
    return FILE_NAME_MAPPING.get(display_name, display_name)


def get_display_filename(actual_name: str) -> str:
    """実際のファイル名から表示名を取得"""
    return REVERSE_FILE_NAME_MAPPING.get(actual_name, actual_name)