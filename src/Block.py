from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json
import json
import time
from BlockData import BlockData

class Block:
    def __init__(self, timestamp:float, data:BlockData, previous_hash=''):
        """
        区块的初始化
        :param timestamp: 创建时的时间戳
        :param data: 区块数据
        :param previous_hash: 上一个区块的hash
        :param hash: 区块的hash
        """

        if not isinstance(data, BlockData):
            print("区块中数据字段类型错误！")
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        '''
        计算该区块的哈希值
        :return : 哈希值，字符串表示
        '''
        block_str = self.previous_hash + str(self.timestamp) + json.dumps(self.data.to_dict(), ensure_ascii=False)
        
        # Create a SHA-256 hash object
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        
        # Update the hash object with the block string encoded as UTF-8
        digest.update(block_str.encode('utf-8'))
        
        # Finalize the hash and return the hexadecimal representation
        block_hash = digest.finalize().hex()  # Convert to hexadecimal string
        return block_hash

    def mine_block(self, diffculty:int):
        '''
        :param diffculty: 整型，代表挖矿难度
        '''
        time_start = time.time()

        # 计算哈希
        while self.hash[0:diffculty] != ''.join(['0']*diffculty):
            self.nonce = self.nonce + 1
            self.hash = self.calculate_hash()

        print("挖到区块:\n \t{0}\n耗时为:\n \t{1}".format(self.hash, time.time()-time_start))

    def to_dict(self):
        '''
        转化为字典
        '''
        return {
            'Time Stamp': self.timestamp,
            'Block Data': self.data.to_dict(),
            'Previous Hash': self.previous_hash,
            'Block Hash': self.hash,
            'Nonce':self.nonce,
        }
    
    @classmethod
    def from_dict(cls, data):
        block = cls(time.time(), BlockData())
        block.timestamp = data['Time Stamp']
        block.data = BlockData.from_dict(data['Block Data'])
        block.previous_hash = data['Previous Hash']
        block.hash = data['Block Hash']
        block.nonce = data['Nonce']

        return block