# 创建虚拟环境
conda create -n ppt_generate python=3.8
conda activate ppt_generate
# 升级pip
python -m pip install --upgrade pip
# 更换 pypi 源加速库的安装
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install torch>=2.0.0
pip install fastapi==0.104.1
pip install uvicorn==0.24.0.post1
pip install requests==2.25.1
pip install modelscope==1.9.5
pip install transformers==4.37.2
pip install streamlit==1.24.0
pip install sentencepiece==0.1.99
pip install accelerate==0.24.1
pip install tiktoken==0.6.0
pip install loguru==0.7.2
pip install sentence_transformers==2.5.1
pip install sse_starlette==2.0.0
pip install openai==1.13.3
pip install peft==0.4.0
pip install datasets==2.10.1
pip install pycorrector==1.0.3
pip install gunicorn==21.2.0
pip install langchain==0.1.5
pip install flask==3.0.2
pip install portalocker==2.8.2
pip install faiss-gpu==1.8.0
pip install markdown_to_json
pip install rank_bm25