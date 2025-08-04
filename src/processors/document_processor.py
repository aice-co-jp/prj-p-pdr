"""
Azure Document Intelligence を使用してドキュメントを処理するモジュール
"""
import os
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from src.utils.file_mapping import get_display_filename

load_dotenv()


class DocumentProcessor:
    """Azure Document Intelligence を使用してドキュメントを解析するクラス"""
    
    def __init__(self):
        """Azure Document Intelligence クライアントの初期化"""
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        if not endpoint or not key:
            raise ValueError(
                "Azure Document Intelligence の認証情報が設定されていません。"
                ".env ファイルに AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT と "
                "AZURE_DOCUMENT_INTELLIGENCE_KEY を設定してください。"
            )
        
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        logger.info("Azure Document Intelligence クライアントを初期化しました")
    
    def process_document(self, file_path: str) -> Dict[str, any]:
        """
        ドキュメントを解析して構造化データを取得
        
        Args:
            file_path: 解析するファイルのパス
            
        Returns:
            解析結果の辞書
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        logger.info(f"ドキュメントを解析中: {file_path.name}")
        
        try:
            # ファイル形式に応じてモデルを選択
            suffix = file_path.suffix.lower()
            if suffix in ['.docx', '.pptx']:
                # Office files は prebuilt-read モデルを使用
                model_id = "prebuilt-read"
                logger.info(f"Office ファイル検出: {model_id} モデルを使用")
            else:
                # PDF や他の形式は prebuilt-layout モデルを使用
                model_id = "prebuilt-layout"
            
            with open(file_path, "rb") as f:
                poller = self.client.begin_analyze_document(
                    model_id, document=f
                )
            result = poller.result()
            
            # 表示用のファイル名を取得
            display_name = get_display_filename(file_path.name)
            
            extracted_data = {
                "file_name": display_name,
                "pages": [],
                "tables": [],
                "key_value_pairs": [],
                "paragraphs": []
            }
            
            # ページごとのテキスト抽出
            for page in result.pages:
                page_text = ""
                if hasattr(page, 'lines') and page.lines:
                    for line in page.lines:
                        page_text += line.content + "\n"
                elif hasattr(page, 'words') and page.words:
                    # Read モデルの場合、lines がない場合は words を使用
                    for word in page.words:
                        page_text += word.content + " "
                
                extracted_data["pages"].append({
                    "page_number": page.page_number,
                    "text": page_text.strip(),
                    "width": getattr(page, 'width', None),
                    "height": getattr(page, 'height', None)
                })
            
            # テーブルの抽出
            if hasattr(result, 'tables') and result.tables:
                for table in result.tables:
                    table_data = {
                        "row_count": table.row_count,
                        "column_count": table.column_count,
                        "cells": []
                    }
                    
                    for cell in table.cells:
                        table_data["cells"].append({
                            "row_index": cell.row_index,
                            "column_index": cell.column_index,
                            "content": cell.content,
                            "row_span": getattr(cell, 'row_span', 1),
                            "column_span": getattr(cell, 'column_span', 1)
                        })
                    
                    extracted_data["tables"].append(table_data)
            
            # 段落の抽出
            if hasattr(result, 'paragraphs') and result.paragraphs:
                for paragraph in result.paragraphs:
                    extracted_data["paragraphs"].append({
                        "content": paragraph.content,
                        "role": getattr(paragraph, 'role', None),
                        "page_numbers": [region.page_number for region in paragraph.bounding_regions]
                        if hasattr(paragraph, 'bounding_regions') else []
                    })
            
            # キーバリューペアの抽出
            if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
                for kv_pair in result.key_value_pairs:
                    if kv_pair.key and kv_pair.value:
                        extracted_data["key_value_pairs"].append({
                            "key": kv_pair.key.content,
                            "value": kv_pair.value.content
                        })
            
            logger.success(f"ドキュメント解析完了: {file_path.name}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"ドキュメント解析エラー: {e}")
            raise
    
    def process_multiple_documents(self, file_paths: List[str]) -> List[Dict[str, any]]:
        """
        複数のドキュメントを一括処理
        
        Args:
            file_paths: 解析するファイルパスのリスト
            
        Returns:
            解析結果のリスト
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.process_document(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"ファイル {file_path} の処理中にエラー: {e}")
                display_name = get_display_filename(Path(file_path).name)
                results.append({
                    "file_name": display_name,
                    "error": str(e)
                })
        
        return results
    
    def extract_text_content(self, processed_data: Dict[str, any]) -> str:
        """
        処理済みデータからテキストコンテンツを抽出
        
        Args:
            processed_data: process_document の戻り値
            
        Returns:
            抽出されたテキスト
        """
        text_content = []
        
        # ページごとのテキストを結合
        for page in processed_data.get("pages", []):
            if page.get("text"):
                text_content.append(page["text"])
        
        # 段落がある場合は段落を優先
        if processed_data.get("paragraphs"):
            text_content = []
            for paragraph in processed_data["paragraphs"]:
                text_content.append(paragraph["content"])
        
        return "\n\n".join(text_content)