from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
import sys
sys.path.append('src/python')
from rag.processing.RagExecutor import RagExecutor

class RAGPrompt:
    def __init__(self, retriever_instance):
        # Retrieverのインスタンスをクラスに保存
        self.retriever = retriever_instance
        
        # LLMの初期化
        self.llm = OpenAI(temperature=0)
        
        # QAチェーンの作成
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm, 
            chain_type="stuff", 
            retriever=self.retriever
        )

    def interact_with_user(self):
        while True:
            query = input("質問を入力してください（終了するには'exit'と入力）: ")
            if query.lower() == 'exit':
                break
            result = self.qa.run(query)
            print(result)

# Retrieverクラスは別のファイルやモジュールで定義されていると仮定
# 例:
# class Retriever:
#     def retrieve(self, query):
#         # ここでクエリに対する情報の検索を行う
#         return some_results

# 使用例
if __name__ == "__main__":
    # Retrieverのインスタンスを作成（この部分は実際には別のスクリプトかモジュールで管理）
    retriever = RagExecutor.load_saved_rag()
    
    # RAGSystemのインスタンスを作成
    rag_system = RAGPrompt(retriever)
    
    # ユーザーとのインタラクションを開始
    rag_system.interact_with_user()