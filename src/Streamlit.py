import streamlit as st
import graphviz
from User import User


# TODO:打印出当前区块链
def show_block_chain(user:User):
    '''
    打印当前用户正在使用的区块链
    '''
    # Create a graphlib graph object
    graph = graphviz.Digraph()
    previous_hash = ''
    for block in user.block_chain.chain:
        graph.edge(previous_hash, block.hash[0:6])
        previous_hash = block.hash[0:6]
    # 打印区块链
    st.graphviz_chart(graph)



# 用于存储用户输入的文件路径
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
    st.session_state.file_path = ''  # Initialize the input field
    st.session_state.file_input_visible = False  # Initially hide the input field
    st.session_state.blockchain_buttons_visible = True  # Initially show blockchain buttons
    st.session_state.user_created = False  # Track if user is created
    st.session_state.user = None  # Store user instance

# 创建用户
if not st.session_state.user_created:
    if st.button('创建用户'):
        st.session_state.user = User()  # 创建用户实例并存储在 session_state
        st.session_state.user_created = True  # 用户创建状态
        st.success('用户创建成功！')  # 显示成功信息
        st.session_state.blockchain_buttons_visible = True  # 允许显示区块链按钮

# 在用户创建后隐藏“创建用户”按钮
if st.session_state.user_created:
    st.info('您已创建用户，可以选择创建新的区块链或从文件加载区块链。')

# 设置用户的工作区块链
if st.session_state.user_created:
    # 创建新的区块链
    if st.session_state.blockchain_buttons_visible:
        if st.button('创建新的区块链'):
            st.session_state.user.create_working_block_chain()  # 使用 session_state 中的 user
            st.session_state.blockchain_buttons_visible = False  # 隐藏区块链按钮
            st.success('新的区块链已创建！')  # 显示成功信息
            
        # 从文件加载区块链
        block_chain_path = st.text_input('输入区块链路径')
        if st.button('从文件加载区块链'):
            st.session_state.user.set_working_block_chain(block_chain_path)  # 使用 session_state 中的 user
            st.session_state.blockchain_buttons_visible = False  # 隐藏区块链按钮
            st.success('区块链已从文件加载！')  # 显示成功信息

# 上传文件按钮
if not st.session_state.blockchain_buttons_visible:
    if st.button('上传文件'):
        st.session_state.file_input_visible = True  # Show input field after clicking this button
        st.session_state.file_upload_visible = True  # Allow file upload

# 如果输入框可见，则显示它
if st.session_state.file_input_visible:
    file_path = st.text_input('输入要上传的文件的路径', value=st.session_state.file_path)

    # 添加按钮
    if st.button('添加'):
        if file_path:  # 检查输入是否为空
            st.session_state.uploaded_files.append(file_path)
            st.success(f'文件已添加: {file_path}')
            # 清空输入框
            st.session_state.file_path = ''
        else:
            st.error('请提供有效的文件路径')

    # 确认上传按钮，只有在文件输入框可见时才显示
    if st.button('确认上传'):
        if st.session_state.uploaded_files:  # 检查是否有文件添加
            st.success('上传的文件列表:')
            for file in st.session_state.uploaded_files:
                st.write(file)
            # 这里可以添加您希望执行的上传动作
            st.session_state.user.upload_files(st.session_state.uploaded_files)
            st.session_state.uploaded_files = []  # 可选: 重置文件列表
            st.session_state.file_input_visible = False  # 隐藏输入框
        else:
            st.error('请至少添加一个文件路径')

if 'user' in st.session_state:
    if hasattr(st.session_state.user, 'block_chain'):
        if st.button('展示区块链'):
            show_block_chain(st.session_state.user)