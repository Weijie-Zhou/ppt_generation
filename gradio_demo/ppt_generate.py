# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from document2vec import Document2Vec
from prompts import get_ppt_outline_prompt, get_ppt_detail_prompt, get_ppt_supply_summary_prompt, get_ppt_detail_supply_retriever_prompty
from utils import TokenizerLengthCheck, split_sub_outline


class PPTGenerate:
    def __init__(self, base_url="http://127.0.0.1:8000/v1/", max_token_length=8096):
        self.tokenizer_length_check = TokenizerLengthCheck()
        self.max_token_length = max_token_length
        self.client = OpenAI(api_key="EMPTY", base_url=base_url)
        self.document2vec = Document2Vec()
        
    def simple_chat(self, prompt, use_stream=True, temperature=0.3, presence_penalty=1.1, top_p=0.8):
        # 调用openai接口请求chatglm3-6b
        messages = [
        {
            "role": "system",
            "content": "A chat between a curious user and an artificial intelligence assistant. " \
                    "The assistant gives helpful, detailed, and polite answers to the user's questions. " \
        },
        {
            "role": "user",
            "content": prompt
        }
        ]
        response = self.client.chat.completions.create(
                        model="chatglm3-6b",
                        messages=messages,
                        stream=use_stream,
                        max_tokens=self.max_token_length,
                        temperature=temperature,
                        presence_penalty=presence_penalty,
                        top_p=top_p)
        if response:
            if use_stream:
                # 流式输出
                for chunk in response:
                    chunk = chunk.choices[0].delta.content
                    # print(chunk, end='', flush=True)
                    yield chunk
            else:
                content = response.choices[0].message.content
                # print('content', content)
                yield content
        else:
            print("Error:", response.status_code)
            
    def document_summary(self, document, lens=8000, max_workers=3):
        # 多进程文档摘要
        document_lst = self.document2vec.document_splitter(document, chunk_size=lens, chunk_overlap=200)
        summary_lens = (lens // (len(document_lst) * 100)) * 100 
        thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        future_lst = []
        for i in document_lst:
            # 多进程摘要，加速
            future = thread_pool.submit(self.summary, i, summary_lens)
            future_lst.append(future)
        text_lst = [future.result() for future in future_lst if future.result()] if future_lst else []
        return "\n".join(text_lst)
    
    def summary(self, document, lens):
        # 拼接prompt，进行文档摘要
        prompt = get_ppt_supply_summary_prompt(document, lens)
        res = ''
        for chunk in self.simple_chat(prompt, temperature=0.1):
            res += chunk
        return res
        
    def gen_ppt_outline_prompt(self, topic, content, file_path):
        # 拼接ppt大纲生成prompt
        if content or file_path:
            if file_path:
                document = content + self.document2vec.load_document(file_path)
            else:
                document = content
        else:
            document = ''
        query = get_ppt_outline_prompt(topic, document)
        # 判断prompt进行tokenizer后的长度是否超过max_token_length
        input_length_check_tag = self.tokenizer_length_check.input_length_check(query, len_req=self.max_token_length)
        if not input_length_check_tag:
            # 对于超出max_token_length的prompt，需要对传入的参考文档进行摘要
            document = self.document_summary(document)
            query = get_ppt_outline_prompt(topic, document)
        return query        
    
    def gen_ppt_outline(self, topic, content='', file_path='', temperature=0.7):
        # 调用大模型生成ppt大纲
        query = self.gen_ppt_outline_prompt(topic, content, file_path)
        for response in self.simple_chat(query, temperature=temperature):
            yield response
    
    def llm_retriever(self, document, sub_outline):
        # 大模型二次召回
        prompt = get_ppt_detail_supply_retriever_prompty(document, sub_outline)
        res = ''
        for chunk in self.simple_chat(prompt, temperature=0.1):
            res += chunk
        return res
    
    def gen_ppt_detail_prompt(self, sub_topic, sub_outline, db):
        # 拼接ppt详情生成prompt
        document_retriever = ''
        if db:
            # 对参考文档使用db向量库进行第一次召回
            document_retriever = self.document2vec.retriever(db, sub_outline)
            # 对参考文档使用大模型进行第二次召回
            if document_retriever:
                document_retriever = self.llm_retriever(document_retriever, sub_outline)
        return get_ppt_detail_prompt(sub_outline, document_retriever, sub_topic) 
            
    def gen_ppt_detail(self, topic, content='', file_path='', ppt_outline='', temperature=0.7):
        # 将ppt大纲抽取为json格式的一页页ppt
        outline_json = split_sub_outline(ppt_outline, topic)
        print('outline_json', outline_json)
        db = ''
        if content or file_path:
            # 对用户传入的参考文档进行切分，并向量化，便于后续召回
            db = self.document2vec.prepare_db(content, file_path)
        chapter = ''
        for dic in outline_json:
            if '内页' not in dic['name']:
                # 对主标题、目录、章节页进行处理(这三类不需要调用大模型进行内容生成)
                if type(dic['content']) == list:
                    dic['content'] = '\n'.join(dic['content'])
                response_json = {}
                response_json['answer'] = dic['content']
                response_json["placeholder_name"] = dic['name'] + '_' + str(dic['page'])
                if '章节' == dic['name']:
                    chapter = dic['content']
            else:
                # 对内页进行详情生成
                query = self.gen_ppt_detail_prompt(dic['sub_title'], dic['content'], db)
                if chapter == dic['sub_title']:
                    placeholder_name = dic['name'] + '_' + dic['content'] + '_' + str(dic['page'])
                else:
                    placeholder_name = dic['name'] + '_' + dic['sub_title'] + '_' + str(dic['page'])
                response_json = {}
                response_json['answer'] = ''
                for chunk in self.simple_chat(query, temperature=temperature):
                    response_json['answer'] += chunk
                response_json["placeholder_name"] = placeholder_name
            yield response_json
            