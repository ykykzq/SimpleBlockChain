import hashlib
import random
import time
import json
import os
import pickle
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Block import Block
from BlockData import BlockData

class BlockChain:
    def __init__(self):
        # 创造创世区块
        self.chain = [self._create_genesis_block()]
        # 设置挖矿难度
        self.difficulty = 0
        # 设置当前Block Chain的ID
        current_time = time.time()
        random.seed(current_time)
        random_number = random.randint(0,2147483647)
        self.id = hashlib.sha256(str(random_number).encode()).hexdigest()

    @staticmethod
    def _create_genesis_block() -> Block:
        '''
        生成创世区块
        :return: 创世区块
        '''
        timestamp = time.time()
        block = Block(timestamp, BlockData(), '')
        return block

    def get_latest_block(self) -> Block:
        '''
        获取最新的区块
        :return: 最新的区块
        '''
        return self.chain[-1]

    def verify_blockchain(self) -> bool:
        '''
        检验区块链数据是否完整
        :return: 检验结果
        '''
        for i in range(1,len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            # 当前区块的哈希不应被改变
            if current_block.hash != current_block.calculate_hash():
                return False
            # 当前区块记录的前一个区块的哈希，与前一个区块的哈希值匹配
            if current_block.previous_hash != previous_block.calculate_hash():
                return False
            
        return True
    
    def upload_files(self, file_path_list:dict[str], author_hash_str: str):
        '''
        用户调用以上传自己的文件
        :param file_path_list:要上传的文件列表
        :param author_hash_str:上传者的哈希值，标记身份
        '''
        blockdata = BlockData()
        for file_path in file_path_list:
            blockdata.add_file(file_path, author_hash_str)

        block = Block(time.time(),blockdata, self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        # 将当前块链接到链的最后
        self.chain.append(block)
        # 将加密后的文件上传
        for file_path in file_path_list:
            BlockData.encrypt_file(file_path, 
                                   BlockData.calculate_file_hash(file_path))
            file_name = file_path.split('/')[-1]
            os.system('mv '+ file_path + '.enc' + ' '+'../workspace/upload_data/' + file_name +'.enc')

    def to_dict(self):
        return {
            'ID': self.id,
            'Chain': [block.to_dict() for block in self.chain],
            'Difficulty': self.difficulty,
        }

    @classmethod
    def from_dict(cls, data):
        blockchain = cls()
        blockchain.chain = [Block.from_dict(block_data) for block_data in data['Chain']]
        blockchain.difficulty = data['Difficulty']
        blockchain.id = data['ID']
        return blockchain
    
    @staticmethod
    def load_from_file(file_path:str):
        '''
        从文件加载一个区块链
        '''
        # with open(file_path,'r',encoding='utf-8') as f:
        #     x = pickle.load(f)
        #     return x

        # 另一种实现
        with open(file_path,'r',encoding='utf-8') as f:
            data = json.load(f)
            blockchain = BlockChain.from_dict(data)
            return blockchain
        return None

    def save_to_file(self, file_path:str)->bool:
        '''
        将当前区块链保存到文件中
        '''
        # # 写入到指定路径
        # with open(file_path,'w', encoding='utf-8') as f:
        #     pickle.dump(self,f)
        #     return True
        # return False
    
        # 另一种实现
        with open(file_path,'w',encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)
            return True
        return False
    

if __name__ == '__main__':
    '''
    测试Block Chain的代码
    '''

    # 测试从文件保存与加载功能

    bc = BlockChain()
    bc.save_to_file('../workspace/block_chain/block_chain.json')

    new_bc = BlockChain.load_from_file('../workspace/block_chain/block_chain.json')

    # 测试文件上传功能
    # 生成 RSA 私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,  # 可以选择 2048 或 4096 位的密钥长度
    )

    # 从私钥生成公钥
    public_key = private_key.public_key()

    # 将私钥序列化为 PEM 格式（以便存储或导出）
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()  # 可以选择加密密钥
    )

    # 将公钥序列化为 PEM 格式
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    private_key_str = private_pem.decode('utf-8')
    public_key_str = public_pem.decode('utf-8')

    # 按行分割字符串
    lines = public_key_str.strip().split('\n')
    # 取出中间部分（从第二行到倒数第二行），也就是实际的公钥部分
    public_key_content = ''.join(lines[1:-1])

    new_bc.upload_files(['../workspace/data/file_example',],public_key_content)
    new_bc.save_to_file('../workspace/block_chain/new_block_chain.json')
    
    print('检验区块链的合法性:')
    print(new_bc.verify_blockchain())
