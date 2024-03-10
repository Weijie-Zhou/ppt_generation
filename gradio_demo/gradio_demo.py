# -*- coding: utf-8 -*-
import json
import gradio as gr
from ppt_generate import PPTGenerate
from split_ppt_detail import split_ppt_detail


def get_ppt_outline(topic, text, file_path, temperature):
    # 获取ppt大纲返回
    if file_path:
        res = model.gen_ppt_outline(topic, text, file_path.name, temperature)
    else:
        res = model.gen_ppt_outline(topic, text, '', temperature)
    data = ''
    for i in res:
        data += i
    return data


def get_ppt_detail(topic, text, file_path, ppt_outline, temperature):
    # 获取ppt详情返回
    if file_path:
        res = model.gen_ppt_detail(topic, text, file_path.name, ppt_outline, temperature)
    else:
        res = model.gen_ppt_detail(topic, text, '', ppt_outline, temperature)
    data = []
    for i in res:
        data.append(i)
    # 将生成的ppt详情抽取为json格式，便于gradio渲染
    data = split_ppt_detail(data)
    with open('{}.json'.format(topic), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


if __name__ == '__main__':
    model = PPTGenerate()
    with gr.Blocks() as demo:
        gr.Label('PPT Generation with Chatglm3-6b')
        temperature = gr.Slider(label="Temperature", value=0.7,  maximum=1, minimum=0)
        topic = gr.Textbox(label='请输入PPT主题')
        examples = ['低碳环保实践与策略', '中国传统文化艺术之美', '黄河流域水土防治措施', '云计算领域年终评估：扩展与安全']
        gr.Examples(examples, topic, label='PPT主题示例')
        content = gr.Textbox(label='请输入参考材料')
        file_path = gr.File(label='可以上传txt或者docx格式的参考文档', file_count='single', file_types=['txt', 'docx'], type='file')
        ppt_outline_output = gr.Markdown(label='PPT大纲')
        ppt_detail_output = gr.Json(label='PPT详情')
        btn_gen_ppt_outline = gr.Button("生成PPT大纲")
        btn_gen_ppt_outline.click(get_ppt_outline, [topic, content, file_path, temperature], ppt_outline_output, show_progress=True)
        btn_gen_ppt_detail = gr.Button("生成PPT详情")
        btn_gen_ppt_detail.click(get_ppt_detail, [topic, content, file_path, ppt_outline_output, temperature], ppt_detail_output)
        clear = gr.ClearButton(components=[topic, content, file_path, ppt_outline_output, ppt_detail_output], value="清除内容")
    demo.queue()
    demo.launch(server_name='0.0.0.0', server_port=6006)