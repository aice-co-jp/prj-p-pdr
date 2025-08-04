"""
パンフレット構成を生成するモジュール
"""
import os
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class StructureGenerator:
    """パンフレットの構成を生成するクラス"""
    
    def __init__(self):
        """Gemini API の初期化"""
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Gemini の認証情報が設定されていません。"
                ".env ファイルに GEMINI_API_KEY を設定してください。"
            )
        
        genai.configure(api_key=api_key)
        # .env からモデル名を取得、なければデフォルト値を使用
        model_name = os.getenv("MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Gemini API を初期化しました (モデル: {model_name})")
    
    def generate_structure(self, 
                         document_contents: List[Dict],
                         audio_transcripts: List[Dict],
                         reference_structure: str) -> str:
        """
        入力データから構成を生成
        
        Args:
            document_contents: ドキュメント処理結果のリスト
            audio_transcripts: 音声文字起こし結果のリスト
            reference_structure: 参考構成（output1.txt の内容）
            
        Returns:
            生成された構成（テキスト形式）
        """
        logger.info("パンフレット構成を生成中...")
        
        # 入力データを整理
        context = self._prepare_context(document_contents, audio_transcripts)
        
        # プロンプトを作成
        prompt = self._create_structure_prompt(context, reference_structure)
        
        try:
            # Gemini で構成を生成
            response = self.model.generate_content(prompt)
            generated_structure = response.text
            
            logger.success("構成生成が完了しました")
            return generated_structure
            
        except Exception as e:
            logger.error(f"構成生成エラー: {e}")
            raise
    
    def _prepare_context(self, 
                        document_contents: List[Dict],
                        audio_transcripts: List[Dict]) -> str:
        """入力データからコンテキストを準備"""
        context_parts = []
        
        # ドキュメントからの情報
        context_parts.append("【ドキュメントからの情報】")
        for doc in document_contents:
            if "error" in doc:
                continue
            
            context_parts.append(f"\n■ {doc['file_name']}")
            
            # テキスト内容を抽出
            text_content = []
            for page in doc.get("pages", []):
                if page.get("text"):
                    text_content.append(page["text"])
            
            if text_content:
                combined_text = "\n".join(text_content)
                # 長すぎる場合は要約
                if len(combined_text) > 3000:
                    combined_text = combined_text[:3000] + "..."
                context_parts.append(combined_text)
            
            # キーバリューペアがある場合
            if doc.get("key_value_pairs"):
                context_parts.append("\n【抽出された重要項目】")
                for kv in doc["key_value_pairs"][:10]:  # 最大10個
                    context_parts.append(f"- {kv['key']}: {kv['value']}")
        
        # 音声からの情報
        if audio_transcripts:
            context_parts.append("\n\n【音声文字起こしからの情報】")
            for audio in audio_transcripts:
                if "error" in audio:
                    continue
                
                context_parts.append(f"\n■ {audio['file_name']}")
                
                # 発話単位で整理
                if audio.get("utterances"):
                    for i, utterance in enumerate(audio["utterances"][:20]):  # 最大20発話
                        speaker = utterance.get("speaker", "話者不明")
                        text = utterance.get("transcript", "")
                        if text:
                            context_parts.append(f"話者{speaker}: {text}")
                else:
                    # 全体の文字起こし
                    transcript = audio.get("transcript", "")
                    if transcript:
                        if len(transcript) > 3000:
                            transcript = transcript[:3000] + "..."
                        context_parts.append(transcript)
        
        return "\n".join(context_parts)
    
    def _create_structure_prompt(self, context: str, reference_structure: str) -> str:
        """構成生成用のプロンプトを作成"""
        prompt = f"""
        あなたは医療パンフレット作成の専門家です。
        以下の情報を基に、医療関係者向けパンフレットの構成を作成してください。

        【参考構成フォーマット】
        {reference_structure}
        この内容はフォーマットであって、実際の内容ではありません。内容は入力情報のみを参考にして作成してください。

        【入力情報】
        {context}

        【作成指示】
        1. 上記の参考構成フォーマットに従って、新しいパンフレットの構成を作成してください
        2. 「#大構成」と「#詳細構成」の2段階で構成してください
        3. 各セクションには以下を含めてください：
        - セクション名
        - 文字数の目安
        - 概要説明
        - 主要な内容の抜粋（入力情報から引用）
        4. 医療関係者向けの専門的な内容として適切な構成にしてください
        5. 入力情報から重要なポイントを抽出し、論理的な流れで配置してください

        構成を作成してください：
        """
        
        return prompt
    
    def enhance_with_keywords(self, 
                            base_structure: str,
                            keywords: List[str]) -> str:
        """
        キーワードを使って構成を強化
        
        Args:
            base_structure: 基本構成
            keywords: 関連キーワードのリスト
            
        Returns:
            強化された構成
        """
        if not keywords:
            return base_structure
        
        prompt = f"""
        以下の構成に、関連キーワードから得られた知見を追加して強化してください。

        【現在の構成】
        {base_structure}

        【関連キーワード】
        {', '.join(keywords)}

        【指示】
        1. キーワードに関連する最新の医学的知見を考慮してください
        2. 必要に応じて新しいセクションを追加してください
        3. 既存のセクションに関連情報を追記してください
        4. 全体の流れと整合性を保ってください

        強化された構成：
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"構成強化エラー: {e}")
            return base_structure