from BlockChain import BlockChain
from Block import Block
import os
import random
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class User:
    def __init__(self):
        # 生成 RSA 私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,  # 可以选择 2048 或 4096 位的密钥长度
        )

        # 从私钥生成公钥
        public_key = private_key.public_key()

        # 将私钥序列化为 PEM 格式（以便存储或导出）
        self.private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()  # 可以选择加密密钥
        )

        # 将公钥序列化为 PEM 格式
        self.public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def create_working_block_chain(self, block_chain_file_path = '../workspace/block_chain/block_chain.json'):
        '''
        重新创建一个用户使用的区块链
        '''
        self.block_chain_file_path = block_chain_file_path
        self.block_chain = BlockChain()
    
    def set_working_block_chain(self, block_chain_file_path:str):
        '''
        设置用户使用的区块链
        '''
        self.block_chain_file_path = block_chain_file_path
        self.block_chain = BlockChain.load_from_file(block_chain_file_path)

    def update_working_block_chain(self):
        '''
        更新用户使用的区块链。避免自己持有的区块链非最新版
        '''
        self.block_chain = BlockChain.load_from_file(self.block_chain_file_path)

    def save_working_block_chain(self, block_chain_file_path:str = '../workspace/block_chain/block_chain.json'):
        '''
        保存（发布）最新的区块链
        '''
        self.block_chain.save_to_file(block_chain_file_path)

    def get_latest_block(self)-> Block:
        '''
        获取当前区块链最新的区块
        '''
        if hasattr(self, 'block_chain'):
            return self.block_chain.get_latest_block()
        else :
            raise Exception('获取区块之前未指定区块链')

    def upload_files(self, file_paths:dict[str]):
        '''
        上传（多个）文件
        '''
        if hasattr(self, 'block_chain') and hasattr(self, 'public_pem'):
            # 首先更新区块链
            self.update_working_block_chain()
            public_key_str = self.public_pem.decode('utf-8')

            # 按行分割字符串
            lines = public_key_str.strip().split('\n')
            # 取出中间部分（从第二行到倒数第二行），也就是实际的公钥部分
            public_key_content = ''.join(lines[1:-1])
            self.block_chain.upload_files(file_paths, public_key_content)

            # 自动保存区块链
            self.save_working_block_chain(self.block_chain_file_path)
        else :
            raise Exception('当前用户没有秘钥，或区块链未初始化')

    def download_file(self, file_enc_hash:str):
        '''
        根据密文的哈希值，下载文件
        '''
        if not hasattr(self, 'block_chain'):
            raise Exception('获取区块之前未指定区块链')
        # 首先更新区块链
        self.update_working_block_chain()
        # 遍历区块链
        for block in self.block_chain.chain:
            for file in block.data.files:
                if file['File'] == file_enc_hash:
                    # 判断当前用户对文件的所有权。实际上应当由其他节点判断
                    public_key_str = self.public_pem.decode('utf-8')
                    lines = public_key_str.strip().split('\n')
                    public_key_content = ''.join(lines[1:-1])
                    if file['User'] == public_key_content:
                        # 通过所有权验证
                        os.system("echo TODO:将文件从存储区下载下来")
                        return
                    else:
                        pass

    def show_files_on_chain(self):
        '''
        显示在区块链上所有的文件及所有者
        '''
        for block in self.block_chain.chain:
            for file in block.data.files:
                print('File:' + '\n' + '\t' + file['File'])
                print('Owner:' + '\n' + '\t' + file['User'])
 


if __name__ == '__main__':
    user = User()

    user.create_working_block_chain()
    # 查看当前创建的区块链
    user.save_working_block_chain()
    # 上传自己的文件
    user.upload_files(['../workspace/data/file_example',])
    # 下载自己的文件

    
    # 上传多个自己的文件测试
    for i in range(0,85):
        n = random.randint(1,10)
        file_list = ['../workspace/data/file_example',] * n
        user.upload_files(file_list)