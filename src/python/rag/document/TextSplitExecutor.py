import ginza
import spacy
import re
from util.PropertyManager import PropertyManager

nlp = spacy.load('ja_core_news_lg')


class TextSplitExecutor:
    def __init__(self):
        self.manager = PropertyManager()
        self.max_length = 700
        self.nlp = spacy.load("ja_core_news_lg")
        self.keyword_terms = self.manager.select_keyword.split(',')
        
        # 意味解析パターンの定義
        self.semantic_patterns = {
            'new_terms': {
                'target_char': '新',
                'exclusions': ['PROPN'],  # 除外する品詞
                'patterns': [
                    {'exact': '更新'},
                    {'pos': 'ADJ', 'contains': '新'},
                    {'pos': 'NOUN', 'contains': '新'}
                ]
            },
            'first_terms': {
                'target_char': '初',
                'exclusions': ['PROPN'],
                'patterns': [
                    {'pos': 'NOUN', 'contains': '初'},
                    {'exact': '初めて'},
                    {'exact': '初期'},
                    {'exact': '初年度'},
                    {'exact': '世界初'},
                    {'exact': '日本初'},
                    {'exact': '業界初'}
                ]
            },
            'most_terms': {
                'target_char': '最',
                'exclusions': ['PROPN'],
                'patterns': [
                    {'exact': '最高'},
                    {'exact': '最低'},
                    {'exact': '最長'},
                    {'exact': '最多'},
                    {'exact': '最古'},
                    {'exact': '最大'},
                    {'pos': 'ADJ', 'contains': '最'},
                    {'pos': 'NOUN', 'contains': '最'}
                ]
            },
            'hatsu_terms': {
                'target_char': '発',
                'exclusions': ['PROPN'],
                'patterns': [
                    {'exact': '発見'},
                    {'exact': '発明'},
                    {'exact': '発表'},
                    {'exact': '日本発'},
                    {'pos': 'VERB', 'contains': '発'},
                    {'pos': 'NOUN', 'contains': '発'}
                ]
            },
            'ten_terms': {
                'target_char': '転',
                'exclusions': ['PROPN'],
                'patterns': [
                    {'exact': '転換'},
                    {'exact': '反転'},
                    {'exact': '転機'},
                    {'exact': '移転'},
                    {'pos': 'VERB', 'contains': '転'},
                    {'pos': 'NOUN', 'contains': '転'}
                ]
            },
            'datsu_terms': {
                'target_char': '脱',
                'exclusions': ['PROPN'],
                'patterns': [
                    {'exact': '脱退'},
                    {'pos': 'VERB', 'contains': '脱'},
                    {'pos': 'NOUN', 'contains': '脱'}
                ]
            },
            'kai_terms': {
                'target_char': '改',
                'exclusions': ['PROPN'],
                'patterns': [
                    {'exact': '改革'},
                    {'exact': '改正'},
                    {'pos': 'VERB', 'contains': '改'},
                    {'pos': 'NOUN', 'contains': '改'}
                ]
            }
        }

    def split_article(self, text, metadata):
        """記事を意味的なチャンクに分割する"""
        doc = self.nlp(text)
        
        chunks = []
        current_chunk = []
        current_length = 0

        try:        
            for sent in doc.sents:
                if self._should_start_new_chunk(sent, current_length, current_chunk):
                    chunks.append(self._create_chunk(current_chunk, metadata, self.keyword_terms))
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(sent.text)
                current_length += len(sent.text)
            
            # 残りのチャンクを処理
            if current_chunk:
                chunks.append(self._create_chunk(current_chunk, metadata, self.keyword_terms))
        except BaseException as e:
             print(f"Warning: Failed to split {text}: {str(e)}")
             raise

        return chunks

    def _should_start_new_chunk(self, sent, current_length, current_chunk):
        """新しいチャンクを開始すべきかを判断する"""
        if not current_chunk:
            return False
            
        has_important_numbers = self._has_important_numbers(sent.text)
        return (current_length + len(sent.text) > self.max_length and 
                not has_important_numbers)

    def _has_important_numbers(self, text):
        """重要な数値情報を含むかチェック"""
        return bool(re.search(r'[0-9]+億円|[0-9]+万円|[0-9]+ドル', text))

    def _contains_economic_terms(self, text, keyword_terms):
        """経済用語を含むかチェック"""
        return bool(any(term in text for term in keyword_terms))

    def has_semantic_terms(self, text, pattern_key):
        """
        指定されたパターンに基づいて意味的な用語を判定
        
        Args:
            text (str): 分析対象テキスト
            pattern_key (str): semantic_patternsのキー
            
        Returns:
            bool: パターンに該当する用語が存在するかどうか
        """
        if pattern_key not in self.semantic_patterns:
            return False
            
        pattern = self.semantic_patterns[pattern_key]
        doc = self.nlp(text)
        
        for token in doc:
            # 対象文字を含まない場合はスキップ
            if pattern['target_char'] not in token.text:
                continue
                
            # 除外する品詞かチェック
            if token.pos_ in pattern['exclusions']:
                continue
                
            # パターンマッチング
            for rule in pattern['patterns']:
                if 'exact' in rule and token.text == rule['exact']:
                    return True
                elif 'pos' in rule and 'contains' in rule:
                    if token.pos_ == rule['pos'] and rule['contains'] in token.text:
                        return True
        
        return False

    def analyze_all_semantic_terms(self, text):
        """全ての意味的パターンを分析"""
        results = {}
        for pattern_key in self.semantic_patterns.keys():
            results[pattern_key] = self.has_semantic_terms(text, pattern_key)
        return results

    def _create_chunk(self, chunk_texts, metadata, keyword_terms):
        """チャンクオブジェクトを作成"""
        chunk_text = ''.join(chunk_texts)
        
        # 全ての意味的パターンを分析
        semantic_results = self.analyze_all_semantic_terms(chunk_text)
        
        return {
            'text': chunk_text,
            'metadata': metadata,
            'contains_economic_terms': self._contains_economic_terms(chunk_text, keyword_terms),
            'semantic_analysis': semantic_results
        }

# このクラスは、最終的に以下のような構造を作成する目的
#analyzed_documents = [
#    Document(
#        page_content="2024年1月期の業績は、売上高が前年同期比10%増の100億円となった。",
#        metadata={
#            "article_date": "2024-01-15",
#            "edition_no": "15",
#            "article_edition": "morning",
#            "article_title": "〇〇会社増収",
#            "article_subtitle": "来年さらなる飛躍へ",
#            "semantic_flags": {
#                "contains_economic_terms": True,  # 経済用語（"売上高", "億円"）を含むため
#                "semantic_analysis": {
#                    "new_terms": False,     # "新"を含む重要な表現なし
#                    "first_terms": False,   # "初"を含む重要な表現なし
#                    "most_terms": False,    # "最"を含む重要な表現なし
#                    "hatsu_terms": False,   # "発"を含む重要な表現なし
#                    "ten_terms": False,     # "転"を含む重要な表現なし
#                    "datsu_terms": False,   # "脱"を含む重要な表現なし
#                    "kai_terms": False      # "改"を含む重要な表現なし
#                }
#            }
#        }
#    ),
#    
#    Document(
#        page_content="当社は新製品の開発を発表し、業界初となる革新的な技術を導入した。",
#        metadata={
#            "article_date": "2024-01-15",
#            "edition_no": "16",
#            "article_edition": "evening",
#            "article_title": "〇〇社 新製品発表",
#            "article_subtitle": "売上増期待",
#            
#            "semantic_flags": {
#                "contains_economic_terms": False,  # 設定された経済用語を含まない
#                "semantic_analysis": {
#                    "new_terms": True,      # "新製品"を含む
#                    "first_terms": True,    # "業界初"を含む
#                    "most_terms": False,
#                    "hatsu_terms": True,    # "発表"を含む
#                    "ten_terms": False,
#                    "datsu_terms": False,
#                    "kai_terms": False
#                }
#            }
#        }
#    )
#]

