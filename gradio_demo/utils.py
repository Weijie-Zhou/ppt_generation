import json

import markdown_to_json
import sentencepiece as spm


class TokenizerLengthCheck:
    '''token长度检查及截断'''
    def __init__(self):
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load("/root/autodl-tmp/ZhipuAI/chatglm3-6b/tokenizer.model")

    def input_length_check(self, text, len_req=8096):
        # 判断prompt+文本后长度是否超过要求长度
        text_tokens = self.sp.EncodeAsIds(text)
        if len(text_tokens) < len_req:
            return True
        else:
            return False
    
    def input_trunc(self, prompt, text, len_req=8096):
        # 输入文本截断
        prompt_tokens = self.sp.EncodeAsIds(prompt)
        text_tokens = self.sp.EncodeAsIds(text)
        total_len = len(prompt_tokens) + len(text_tokens)
        if total_len < len_req:
            return text
        else:
            res_len = len_req - len(prompt_tokens)
            half_res_len = int((len(text_tokens)-res_len) / 2)
            text_tokens = text_tokens[half_res_len: -half_res_len]
            return self.sp.Decode(text_tokens)
        
        
def split_sub_outline(data, topic):
    '''基于markdown_to_json，将markdown格式的ppt大纲切分为json格式'''
    data_temp = []
    for i in data.split('\n'):
        # 去除问题文本
        if '提纲' in i:
            continue
        if 'markdown' in i:
            continue
        if '```' in i:
            continue
        data_temp.append(i)
    data = '\n'.join(data_temp)
    markdown_json = json.loads(markdown_to_json.jsonify(data))
    res = []
    title_lst = [i for i in markdown_json]
    if len(title_lst) == 1:
        title = title_lst[0]
        markdown_json = markdown_json[title]
    elif title_lst[0] == topic:
        title = title_lst[0]
        markdown_json = markdown_json[title]
    else:
        title = topic
    res.append({'name': '主题', 'content': title, 'page': 1})
    catelogs = [i for i in markdown_json]
    res.append({'name': '目录', 'content': catelogs, 'page': 2})
    page = 2
    for catelog in catelogs:
        page += 1
        res.append({'name': '章节', 'content': catelog, 'page': page})
        temp_catelogs = markdown_json[catelog]
        if type(temp_catelogs) == list:
            if len(set([type(i) for i in temp_catelogs])) > 1:
                for idx in range(len(temp_catelogs)//2):
                    page += 1
                    res.append({'name': '内页', 'content': '\n'.join(temp_catelogs[idx*2+1]), 'sub_title': temp_catelogs[idx*2], 'page': page, 'num': len(temp_catelogs[idx+1])})
            else:
                for i in temp_catelogs:
                    page += 1
                    if type(i) == list:
                        i = ''.join(i)
                    res.append({'name': '内页', 'content': i, 'page': page, 'num': 1, 'sub_title': catelog})
        elif type(temp_catelogs) == dict:
            for k, v in temp_catelogs.items():
                page += 1
                if len(set([type(x) for x in v])) > 1:
                    v = v[-1]
                try:
                    if type(v) == str:
                        res.append({'name': '内页', 'content': v, 'sub_title': k, 'page': page, 'num': len(v)})
                    else:
                        res.append({'name': '内页', 'content': '\n'.join(v), 'sub_title': k, 'page': page, 'num': len(v)})
                except:
                    res.append({'name': '内页', 'content': str(v).replace('[', '').replace(']', ''), 'sub_title': k, 'page': page, 'num': len(v)})
    return res