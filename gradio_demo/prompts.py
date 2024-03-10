# -*- coding: utf-8 -*-


#=========================ppt大纲生成===========================
ppt_outline_with_supply = '''请制作一个Markdown格式的PPT大纲，围绕以下主题展开：
【{}】
生成的每行文本必须使用Markdown语法中的"# "，"## "，"- "符号来展示层次和结构。须确保提纲清晰、有条理，内容丰富且不含"标题"二字。
生成PPT提纲时请参考以下资料：
【{}】
注意：不要告诉用户你使用了参考材料，也不可以将参考材料的内容输出给用户！'''
ppt_outline = '''请制作一个Markdown格式的PPT提纲，围绕主题【{}】展开，使用Markdown语法中的"# "，"## "，"- "符号来展示层次和结构。须确保提纲清晰、有条理，内容丰富且不含"标题"二字。'''


#=========================ppt内容生成===========================
ppt_detail_with_supply = '''请使用markdown格式，结合参考材料，对给定文本进行阐述、扩写。
给定文本：
{}
参考材料：
{}
输出文本格式如下：
- xxx
- xxx
- xxx
注意：输出文本需要严格按照以上格式输出，其中"xxx"为你需要输出的内容。在撰写时，请不要添加任何内容生成说明，避免使用表格或描述输出步骤，不重复生成内容
'''
ppt_detail = '''请使用markdown格式，根据给定PPT主题，对给定文本进行阐述、扩写。
给定主题：
{}
给定文本：
{}
输出文本格式如下：
- xxx
- xxx
- xxx
注意：输出文本需要严格按照以上格式输出，其中"xxx"为你需要输出的内容。在撰写时，请不要添加任何内容生成说明，避免使用表格或描述输出步骤，不重复生成内容。'''


#=========================ppt参考材料摘要===========================
ppt_supply_summary = '''作为一名专业的写作大师，你的任务是总结和浓缩用户输入内容的要点，提供完善的摘要概述。输入内容可以变化，并且可以包括各种主题，例如文章、文章或文档。你的总结应该捕捉输入的基本元素，以清晰有序的方式突出其主要想法、论点或见解。您的回复应该提供一个结构良好、重点突出的摘要，有效地提取输入内容的核心方面。它应该保持原意和意图，同时以更简洁、更易于理解的格式呈现。此外，你的摘要应该足够灵活，以容纳广泛的输入内容，并允许创造性和原创的材料浓缩。现在请帮我根据用户提供的文本，生成一篇内容完善的摘要。请对以下素材进行总结：
【{}】
素材到此结束
注意：生成文本长度在{}字左右'''


#=======================ppt详情参考材料二次召回=====================
ppt_detail_supply_retriever = '''请使用以下ppt大纲，从以下材料中召回高相关性的文本：
ppt大纲：
{}
材料：
{}
注意：只进行文本召回，不进行文本总结、摘要。召回的文本请拼接成一段连续、不换行的整段文本输出。请不要添加任何内容生成说明，输出文本的格式如下：
xxx
'''


# ppt大纲生成
def get_ppt_outline_prompt(topic, supply=''):
    if supply:
        return ppt_outline_with_supply.format(topic, supply)
    else:
        return ppt_outline.format(topic)
    

# ppt内容生成
def get_ppt_detail_prompt(sub_outline, supply='', sub_topic=''):
    if supply:
        return ppt_detail_with_supply.format(sub_outline, supply)
    else:
        return ppt_detail.format(sub_topic, sub_outline)
    
    
# ppt参考材料摘要
def get_ppt_supply_summary_prompt(supply, lens):
    return ppt_supply_summary.format(supply, lens)


# ppt详情生成参考材料二次召回
def get_ppt_detail_supply_retriever_prompty(supply, ppt_outline):
    return ppt_detail_supply_retriever.format(ppt_outline, supply)
