import hashlib
import random
import time
import json
import pickle
from Block import Block
from BlockData import BlockData

class BlockChain:
    def __init__(self):
        # 创造创世区块
        self.chain = [self._create_genesis_block()]
        # 设置挖矿难度
        self.difficulty = 5
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

        

    def save_to_file(self,file_path:str)->bool:
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

    bc.save_to_file('../data/block_chain.json')

    new_bc = BlockChain.load_from_file('../data/block_chain.json')