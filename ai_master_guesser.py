import streamlit as st
import google.generativeai as genai

# --- 1. 安全配置 API ---
# 建议在 Streamlit Cloud 的 Secrets 中设置 "GEMINI_API_KEY"
# 本地测试时，你可以暂时把 API_KEY 替换成你的字符串
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "这里填入你的API_KEY" # 仅限本地测试使用！

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. 初始化系统与会话 ---
st.set_page_config(page_title="AI 读心神算子", page_icon="🕵️", layout="centered")

if "chat_session" not in st.session_state:
    # 核心：设定 AI 的“人格”与规则
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.game_over = False
    st.session_state.question_count = 0
    
    # 初始指令：确立游戏边界
    init_instr = (
        "现在我们要玩一个猜人物游戏。我心里想一个著名人物（现实、虚拟、古今中外皆可）。"
        "你作为猜题者，每次只能问一个‘是/否’的问题。我会回答：‘是’、‘不是’或‘不确定’。"
        "请通过你的逻辑推理，用最少的问题锁定目标。如果你觉得有 90% 的把握了，请直接给出猜测。"
        "现在，请开始你的第一问。"
    )
    response = st.session_state.chat_session.send_message(init_instr)
    st.session_state.current_question = response.text

# --- 3. UI 界面设计 ---
st.title("🕵️ AI 读心神算子：终极挑战")
st.write("---")

# 左侧进度条与状态
with st.sidebar:
    st.header("📊 实时战况")
    st.metric("提问次数", st.session_state.question_count)
    if st.button("🔄 重新开始游戏", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.info("提示：AI 会根据你的回答动态调整策略，请如实作答。")

# 中央游戏区域
if not st.session_state.game_over:
    st.info(f"**AI 正在思考中... 第 {st.session_state.question_count + 1} 问：**")
    st.markdown(f"### {st.session_state.current_question}")
    
    # 交互按钮
    col1, col2, col3 = st.columns(3)
    
    def process_answer(user_ans):
        st.session_state.question_count += 1
        with st.spinner("正在分析线索..."):
            res = st.session_state.chat_session.send_message(user_ans)
            st.session_state.current_question = res.text
            # 简单的逻辑判断：如果 AI 给出的答案里不带问号，可能是在公布答案
            if "?" not in res.text:
                st.session_state.game_over = True
        st.rerun()

    with col1:
        if st.button("✅ 是的", use_container_width=True, type="primary"):
            process_answer("是的")
    with col2:
        if st.button("❌ 不是", use_container_width=True):
            process_answer("不是")
    with col3:
        if st.button("❔ 不确定", use_container_width=True):
            process_answer("不确定")

# 结算界面
else:
    st.balloons()
    st.success("## 🎯 AI 给出了最终答案！")
    st.markdown(f"### {st.session_state.current_question}")
    
    if st.button("猜对了！太神了", use_container_width=True):
        st.snow()
    if st.button("没猜对，AI 还需要学习", use_container_width=True):
        st.warning("看来我的数据库里还缺了一些维度。")