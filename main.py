#!/usr/bin/env python3
"""
医療パンフレット作成支援デモシステム - メインスクリプト
"""
import sys
import argparse
from pathlib import Path
from loguru import logger
from tqdm import tqdm
from dotenv import load_dotenv

# プロジェクトのモジュールをインポート
from src.processors.document_processor import DocumentProcessor
from src.processors.audio_processor import AudioProcessor
from src.generators.structure_generator import StructureGenerator
from src.utils.file_utils import (
    get_input_files,
    save_output,
    read_reference_structure,
    create_processing_summary
)
from src.utils.file_mapping import get_display_filename

# 環境変数を読み込み
load_dotenv()

# ロガーの設定
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
logger.add("logs/demo_system.log", rotation="10 MB", retention="7 days")


def process_documents(document_files: list, pdf_files: list) -> list:
    """ドキュメントと PDF ファイルを処理"""
    logger.info("ドキュメント処理を開始します...")
    
    processor = DocumentProcessor()
    results = []
    
    all_files = document_files + pdf_files
    
    for file_path in tqdm(all_files, desc="ドキュメント処理"):
        try:
            result = processor.process_document(file_path)
            results.append(result)
        except Exception as e:
            logger.error(f"ファイル {file_path} の処理に失敗: {e}")
            display_name = get_display_filename(Path(file_path).name)
            results.append({
                "file_name": display_name,
                "error": str(e)
            })
    
    return results


def process_audio_files(audio_files: list) -> list:
    """音声ファイルを処理"""
    if not audio_files:
        logger.info("音声ファイルが見つかりませんでした")
        return []
    
    logger.info("音声処理を開始します...")
    
    processor = AudioProcessor()
    results = []
    
    for file_path in tqdm(audio_files, desc="音声処理"):
        try:
            result = processor.transcribe_audio(file_path)
            results.append(result)
        except Exception as e:
            logger.error(f"ファイル {file_path} の処理に失敗: {e}")
            display_name = get_display_filename(Path(file_path).name)
            results.append({
                "file_name": display_name,
                "error": str(e)
            })
    
    return results


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="医療パンフレット作成支援デモシステム"
    )
    parser.add_argument(
        "--input-dir",
        default="input",
        help="入力ファイルのディレクトリ（デフォルト: input）"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="出力ディレクトリ（デフォルト: output）"
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="音声処理をスキップ"
    )
    parser.add_argument(
        "--skip-documents",
        action="store_true",
        help="ドキュメント処理をスキップ"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("医療パンフレット作成支援デモシステム")
    logger.info("=" * 50)
    
    try:
        # 入力ファイルを取得
        document_files, audio_files, pdf_files = get_input_files(args.input_dir)
        
        # ドキュメント処理
        document_results = []
        if not args.skip_documents:
            document_results = process_documents(document_files, pdf_files)
        else:
            logger.info("ドキュメント処理をスキップしました")
        
        # 音声処理
        audio_results = []
        if not args.skip_audio:
            audio_results = process_audio_files(audio_files)
        else:
            logger.info("音声処理をスキップしました")
        
        # 処理結果が空の場合は警告
        if not document_results and not audio_results:
            logger.warning("処理可能なファイルが見つかりませんでした")
            return
        
        # 参考構成を読み込み
        logger.info("参考構成を読み込み中...")
        reference_structure = read_reference_structure()
        
        # 構成を生成
        logger.info("パンフレット構成を生成中...")
        generator = StructureGenerator()
        generated_structure = generator.generate_structure(
            document_results,
            audio_results,
            reference_structure
        )
        
        # 結果を保存
        output_file = save_output(
            generated_structure,
            output_dir=args.output_dir
        )
        
        # サマリーを作成・保存
        summary = create_processing_summary(
            document_results,
            audio_results,
            output_file
        )
        summary_file = save_output(
            summary,
            filename="processing_summary.txt",
            output_dir=args.output_dir
        )
        
        logger.success(f"処理が完了しました！")
        logger.info(f"生成された構成: {output_file}")
        logger.info(f"処理サマリー: {summary_file}")
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()