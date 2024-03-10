from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.document_loaders import TextLoader, Docx2txtLoader
from langchain.vectorstores import FAISS
from gradio_demo.chinese_recursive_text_splitter import ChineseRecursiveTextSplitter



class Document2Vec:
    def __init__(self):
        # 加载bge模型
        self.embedding_model = HuggingFaceBgeEmbeddings(
            model_name="/root/autodl-tmp/AI-ModelScope/bge-large-zh-v1.5",
            model_kwargs={"device": "cuda:0"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
    def load_document(self, file_path):
        # 加载文档文件
        if '.txt' in file_path:
            loader = TextLoader(file_path)
        elif '.docx' in file_path:
            loader = Docx2txtLoader(file_path)
        else:
            raise Exception('请上传txt/docx类型的文档')
        document_lst = loader.load()
        document = ''.join([document.page_content for document in document_lst])
        return document

    def document_splitter(self, document, separators=['。', '！', '？', '\n'], chunk_size=50, chunk_overlap=0):
        # 文本切分
        text_splitter = ChineseRecursiveTextSplitter(
            separators=separators,
            keep_separator=True,
            is_separator_regex=True,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_text(document)
        return chunks
    
    def prepare_db(self, content, file_path, lens=100):
        # 初始化向量库
        if file_path:
            document = content + self.load_document(file_path)
        else:
            document = content
        document_lst = self.document_splitter(document, chunk_size=lens)
        db = FAISS.from_texts(document_lst, self.embedding_model)
        return db
    
    def retriever(self, db, query, k=3, threshold=1):
        # 文档召回
        res = db.similarity_search_with_score(query, k=k)
        document = ''
        for i in res:
            if i[1] < threshold:
                document += i[0].page_content
        return document
