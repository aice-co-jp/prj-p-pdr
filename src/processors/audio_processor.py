"""
Deepgram を使用して音声ファイルを処理するモジュール
"""
import os
from typing import Dict, Optional, List
from pathlib import Path
from loguru import logger
from deepgram import Deepgram
import asyncio
from dotenv import load_dotenv
from src.utils.file_mapping import get_display_filename

load_dotenv()


class AudioProcessor:
    """Deepgram を使用して音声ファイルを文字起こしするクラス"""
    
    def __init__(self):
        """Deepgram クライアントの初期化"""
        api_key = os.getenv("DEEPGRAM_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Deepgram の認証情報が設定されていません。"
                ".env ファイルに DEEPGRAM_API_KEY を設定してください。"
            )
        
        self.deepgram = Deepgram(api_key)
        logger.info("Deepgram クライアントを初期化しました")
    
    async def _transcribe_file_async(self, file_path: Path, options: Dict) -> Dict:
        """非同期で音声ファイルを文字起こし"""
        with open(file_path, "rb") as audio:
            audio_data = audio.read()
            source = {"buffer": audio_data, "mimetype": self._get_mimetype(file_path)}
            response = await self.deepgram.transcription.prerecorded(
                source, options
            )
        return response
    
    def transcribe_audio(self, file_path: str, language: str = "ja") -> Dict[str, any]:
        """
        音声ファイルを文字起こし
        
        Args:
            file_path: 音声ファイルのパス
            language: 言語コード（デフォルト: ja）
            
        Returns:
            文字起こし結果の辞書
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        logger.info(f"音声ファイルを文字起こし中: {file_path.name}")
        
        try:
            # Deepgram オプション設定
            options = {
                "language": language,
                "punctuate": True,
                "diarize": True,  # 話者分離
                "utterances": True,  # 発話単位で分割
                "model": "general",
                "tier": "enhanced"
            }
            
            # 非同期処理を実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self._transcribe_file_async(file_path, options)
            )
            loop.close()
            
            # 結果を整形（表示用ファイル名を使用）
            display_name = get_display_filename(file_path.name)
            result = self._format_transcription_result(response, display_name)
            
            logger.success(f"音声文字起こし完了: {file_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"音声文字起こしエラー: {e}")
            raise
    
    def _format_transcription_result(self, response: Dict, file_name: str) -> Dict[str, any]:
        """
        Deepgram のレスポンスを整形
        
        Args:
            response: Deepgram API のレスポンス
            file_name: ファイル名
            
        Returns:
            整形された結果
        """
        result = response.get("results", {})
        
        formatted_result = {
            "file_name": file_name,
            "duration": result.get("channels", [{}])[0].get("alternatives", [{}])[0].get("duration", 0),
            "transcript": "",
            "utterances": [],
            "words": [],
            "confidence": 0
        }
        
        # チャンネルごとの結果を処理
        if result.get("channels"):
            channel = result["channels"][0]
            if channel.get("alternatives"):
                alternative = channel["alternatives"][0]
                
                # 全体の文字起こし
                formatted_result["transcript"] = alternative.get("transcript", "")
                formatted_result["confidence"] = alternative.get("confidence", 0)
                
                # 単語レベルの情報
                if alternative.get("words"):
                    formatted_result["words"] = [
                        {
                            "word": word.get("word", ""),
                            "start": word.get("start", 0),
                            "end": word.get("end", 0),
                            "confidence": word.get("confidence", 0),
                            "speaker": word.get("speaker", None)
                        }
                        for word in alternative["words"]
                    ]
        
        # 発話単位の情報（話者分離）
        if result.get("utterances"):
            formatted_result["utterances"] = [
                {
                    "speaker": utterance.get("speaker", None),
                    "start": utterance.get("start", 0),
                    "end": utterance.get("end", 0),
                    "transcript": utterance.get("transcript", "")
                }
                for utterance in result["utterances"]
            ]
        
        return formatted_result
    
    def _get_mimetype(self, file_path: Path) -> str:
        """ファイルの MIME タイプを取得"""
        ext = file_path.suffix.lower()
        mime_types = {
            ".mp3": "audio/mp3",
            ".mp4": "audio/mp4",
            ".wav": "audio/wav",
            ".m4a": "audio/m4a",
            ".aac": "audio/aac",
            ".flac": "audio/flac"
        }
        return mime_types.get(ext, "audio/mpeg")
    
    def extract_key_points(self, transcription_result: Dict[str, any], 
                          min_confidence: float = 0.8) -> List[str]:
        """
        文字起こし結果から重要な発言を抽出
        
        Args:
            transcription_result: transcribe_audio の戻り値
            min_confidence: 最小信頼度
            
        Returns:
            重要な発言のリスト
        """
        key_points = []
        
        # 発話単位で処理
        for utterance in transcription_result.get("utterances", []):
            transcript = utterance.get("transcript", "").strip()
            
            # 短すぎる発話はスキップ
            if len(transcript) < 20:
                continue
            
            # 重要そうなキーワードを含む発話を抽出
            important_keywords = [
                "重要", "ポイント", "結論", "まとめ", "注意",
                "特に", "必ず", "結果", "効果", "目的"
            ]
            
            if any(keyword in transcript for keyword in important_keywords):
                key_points.append({
                    "speaker": utterance.get("speaker", "不明"),
                    "text": transcript,
                    "time": f"{utterance.get('start', 0):.1f}秒"
                })
        
        return key_points