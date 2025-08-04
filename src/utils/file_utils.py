"""
ファイル操作に関するユーティリティ
"""
import os
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
from loguru import logger


def get_input_files(input_dir: str = "input") -> Tuple[List[str], List[str], List[str]]:
    """
    入力ディレクトリからファイルを分類して取得
    
    Args:
        input_dir: 入力ディレクトリのパス
        
    Returns:
        (文書ファイル, 音声ファイル, PDFファイル) のタプル
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"入力ディレクトリが見つかりません: {input_dir}")
    
    document_files = []
    audio_files = []
    pdf_files = []
    
    # サポートするファイル拡張子
    document_extensions = {'.docx', '.doc', '.pptx'}
    audio_extensions = {'.mp3', '.wav', '.m4a'}
    pdf_extensions = {'.pdf'}
    
    # ファイルを分類
    for file_path in input_path.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            
            if ext in document_extensions:
                document_files.append(str(file_path))
            elif ext in audio_extensions:
                audio_files.append(str(file_path))
            elif ext in pdf_extensions:
                pdf_files.append(str(file_path))
    
    logger.info(f"入力ファイルを検出: "
               f"文書 {len(document_files)}件, "
               f"音声 {len(audio_files)}件, "
               f"PDF {len(pdf_files)}件")
    
    return document_files, audio_files, pdf_files


def save_output(content: str, filename: str = "generated_structure.txt", 
                output_dir: str = "output") -> str:
    """
    生成された構成をファイルに保存
    
    Args:
        content: 保存する内容
        filename: ファイル名
        output_dir: 出力ディレクトリ
        
    Returns:
        保存したファイルのパス
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # ファイル名に日時を追加
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_stem = Path(filename).stem
    file_ext = Path(filename).suffix
    filename_with_timestamp = f"{file_stem}_{timestamp}{file_ext}"
    
    file_path = output_path / filename_with_timestamp
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"ファイルを保存しました: {file_path}")
    return str(file_path)


def read_reference_structure(file_path: str = "input/output_reference/output1.txt") -> str:
    """
    参考構成ファイルを読み込む
    
    Args:
        file_path: 参考構成ファイルのパス
        
    Returns:
        ファイルの内容
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"参考構成ファイルが見つかりません: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content


def create_processing_summary(
    document_results: List[dict],
    audio_results: List[dict],
    output_file: str
) -> str:
    """
    処理結果のサマリーを作成
    
    Args:
        document_results: ドキュメント処理結果
        audio_results: 音声処理結果
        output_file: 出力ファイルパス
        
    Returns:
        サマリーテキスト
    """
    summary_parts = [
        "# 処理結果サマリー",
        f"\n生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"出力ファイル: {output_file}",
        "\n## 処理したファイル",
        "\n### ドキュメント"
    ]
    
    for doc in document_results:
        status = "✓ 成功" if "error" not in doc else "✗ エラー"
        summary_parts.append(f"- {doc['file_name']} {status}")
        if "error" in doc:
            summary_parts.append(f"  エラー: {doc['error']}")
    
    summary_parts.append("\n### 音声ファイル")
    for audio in audio_results:
        status = "✓ 成功" if "error" not in audio else "✗ エラー"
        summary_parts.append(f"- {audio['file_name']} {status}")
        if "error" in audio:
            summary_parts.append(f"  エラー: {audio['error']}")
        elif "duration" in audio:
            summary_parts.append(f"  長さ: {audio['duration']:.1f}秒")
    
    return "\n".join(summary_parts)