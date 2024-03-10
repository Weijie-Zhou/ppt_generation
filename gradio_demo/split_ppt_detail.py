import json
import markdown_to_json


def delete_sentence(data):
    # 去除生成文本中不必要的内容
    data_lst = data.split('\n')
    res = []
    for data in data_lst:
        if not data:
            continue
        if '大纲' in data:
            continue
        if '参考材料' in data:
            continue
        if '```' in data:
            continue
        if '到此为止' in data:
            continue
        if 'Markdown' in data:
            continue
        if '---' in data:
            continue
        if '文本内容' in data:
            continue
        if '标记符' in data:
            continue
        if '扩写' in data:
            continue
        if '扩展后的文本' in data:
            continue
        if '幻灯片' in data:
            continue
        if 'PPT' in data:
            continue
        if 'ppt' in data:
            continue
        if '给定' in data and '文本' in data:
            continue
        if '扩展' in data and '版本' in data:
            continue
        if '扩展' in data and '内容' in data:
            continue
        if '子标题' in data:
            continue
        if '标题' in data:
            continue
        if '结论' == data:
            continue
        data = data.replace('**文本**：', '').replace('**文本**', '').replace('子章节', '').replace('*', '').replace('正文', '')
        res.append(data)
    return '\n'.join(res)


def convert_to_dict(input_list):
    # 辅助转换函数
    result_list = []

    for i in range(0, len(input_list), 2):
        main_title = input_list[i]
        sub_list = input_list[i + 1]

        main_dict = {'sub_title_1': main_title, 'sub_content_1': []}
        if type(sub_list) == list and len(sub_list) % 2 == 0 and set([type(j) for j in sub_list]) == set([list, str]):
            for j in range(0, len(sub_list), 2):
                sub_title_2 = sub_list[j]
                sub_content_2 = sub_list[j + 1]

                sub_dict = {'sub_title_2': sub_title_2, 'sub_content_2': sub_content_2}
                main_dict['sub_content_1'].append(sub_dict)
        else:
            main_dict['sub_content_1'] = sub_list

        result_list.append(main_dict)

    return result_list


def list_to_dict(input_list):
    # 辅助转换函数
    result_dict_list = []

    sub_title = ''
    sub_content = []

    for item in input_list:
        if isinstance(item, str) and item.startswith('1.'):
            if sub_title:
                result_dict_list.append({'sub_title_1': sub_title, 'sub_content_1': sub_content})
                sub_content = []
            sub_title = item
        elif isinstance(item, list):
            sub_content.extend(item)

    if sub_title:
        result_dict_list.append({'sub_title_1': sub_title, 'sub_content_1': sub_content})

    return result_dict_list


def split_ppt_detail(data):
    # 对大模型生成的ppt详情内容进行切分，转换为json格式
    res = []
    for char in data:
        dic = {}
        nw_title, dic['content'] = char['placeholder_name'], char['answer']
        if len(nw_title.split('_')) == 2:
            dic['page'] = nw_title.split('_')[-1]
            dic['name'] = nw_title.split('_')[-2]
            dic['content'] = delete_sentence(dic['content'])
            if dic['name'] == '目录':
                dic['content'] = dic['content'].split('\n')
        elif len(nw_title.split('_')) == 3:
            dic['page'] = nw_title.split('_')[-1]
            dic['title'] = nw_title.split('_')[-2]
            dic['name'] = nw_title.split('_')[-3]
            dic['content'] = delete_sentence(dic['content'])
            if dic['name'] == '内页':
                try:
                    dic['content'] = json.loads(markdown_to_json.jsonify(dic['content'].strip()))
                except:
                    dic['content'] = dic['content'].strip().split('\n')
        if dic['name'] == '内页' and len([i for i in dic['content']]) == 1 and [i for i in dic['content']][0] == 'root':
            dic['content'] = dic['content']['root'][0]
        temp_lst = []
        if dic['name'] == '内页' and type(dic['content']) == dict:
            for k, v in dic['content'].items():
                temp_dic = {}
                temp_dic['sub_title'] = k
                if not type(v) == dict:
                    temp_dic['sub_content'] = v
                else:
                    temp_dic['sub_content'] = []
                    for temp_k, temp_v in v.items():
                        temp_temp_dic = {}
                        temp_temp_dic['sub_title_1'] = temp_k
                        temp_temp_dic['sub_content_1'] = temp_v
                        temp_dic['sub_content'].append(temp_temp_dic)
                if len(set([type(i) for i in temp_dic['sub_content']])) == 2 and list in [type(i) for i in temp_dic['sub_content']] and str in [type(i) for i in temp_dic['sub_content']]:
                    temp_dic['sub_content'] = [i if type(i)==str else '\n'.join(i) for i in temp_dic['sub_content']]
                temp_lst.append(temp_dic)
            dic['content'] = temp_lst
        elif dic['name'] == '内页' and type(dic['content']) == list and not temp_lst:
            if len(set([type(i) for i in dic['content']])) > 1:
                if len(dic['content']) % 2 != 0:
                    dic['content'] = dic['content'][1:]
                for idx in range(len(dic['content'])//2):
                    temp_dic = {'sub_title': dic['content'][idx*2], 'sub_content': dic['content'][idx*2+1]}
                    if type(temp_dic['sub_content']) == list and len(temp_dic['sub_content']) % 2 == 0 and set([type(j) for j in temp_dic['sub_content']]) == set([list, str]):
                        try:
                            temp_dic['sub_content'] = convert_to_dict(temp_dic['sub_content'])
                        except:
                            try:
                                temp_dic['sub_content'] = list_to_dict(temp_dic['sub_content'])
                            except:
                                pass
                    if len(set([type(i) for i in temp_dic['sub_content']])) == 2 and list in [type(i) for i in temp_dic['sub_content']] and str in [type(i) for i in temp_dic['sub_content']]:
                        temp_dic['sub_content'] = [i if type(i)==str else '\n'.join(i) for i in temp_dic['sub_content']]
                    temp_lst.append(temp_dic)
                dic['content'] = temp_lst
        if len([type(i) for i in dic['content']]) == 2 and list in [type(i) for i in dic['content']] and str in [type(i) for i in dic['content']]:
            dic['content'] = [i if type(i)==str else '\n'.join(i) for i in dic['content']]
        res.append(dic)
    return res