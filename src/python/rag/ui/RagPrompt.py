from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
import sys
import os
sys.path.append('src/python')
from rag.processing.RagExecutor import RagExecutor

class RAGPrompt:
    def __init__(self, retriever_instance):
        self.retriever = retriever_instance.get_retriever()
        
        
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo-16k",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # QAチェーンの作成
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            verbose=True
        )

    def print_retriever_info(self):
        """Retrieverの情報を表示"""
        return
        # print("\n=== Retriever情報 ===")
        # print(f"Retriever type: {type(self.retriever)}")
        # print(f"Search kwargs: {self.retriever.search_kwargs}")

        # # ChromaDBの情報を取得
        # if hasattr(self.retriever, '_collection'):
        #     print(f"Collection name: {self.retriever._collection.name}")
        #     print(f"Total documents: {self.retriever._collection.count()}")

    def print_retrieved_documents(self, docs):
        return
        # """検索されたドキュメントの情報を表示"""
        # print("\n=== 検索されたドキュメント ===")
        # for i, doc in enumerate(docs, 1):
        #     print(f"\nドキュメント {i}:")
        #     print(f"内容: {doc.page_content[:200]}...")  # 最初の200文字のみ表示
        #     print(f"メタデータ: {doc.metadata}")
        #     try:
        #         print(f"類似度スコア: {doc.similarity}")  # もし利用可能な場合
        #     except:
        #         pass        

    def interact_with_user(self):
        self.print_retriever_info()

        while True:
            query = input("質問を入力してください（終了するには'exit'と入力）: ")
            if query.lower() == 'exit':
                break
            #result = self.qa.run(query)
            result = self.qa.invoke(query)
            print(result)

            # 関連ドキュメントの表示
            if 'source_documents' in result:
                self.print_retrieved_documents(result['source_documents'])            

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