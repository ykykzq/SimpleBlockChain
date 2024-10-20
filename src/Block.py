import hashlib
import json
import time
import BlockData

class Block:
    def __init__(self, timestamp, data, previous_hash=''):
        """
        区块的初始化
        :param timestamp: 创建时的时间戳
        :param data: 区块数据
        :param previous_hash: 上一个区块的hash
        :param hash: 区块的hash
        """

        if not isinstance(data, BlockData.BlockData):
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
        block_str = self.previous_hash + str(self.timestamp) + json.dumps(self.data, ensure_ascii=False)
        sha_256 = hashlib.sha256()
        sha_256.update(block_str.encode('utf-8'))

        hash = sha_256.hexdigest()
        return hash

    def mine_block(self, diffculty):
        '''
        :param diffculty: 整型，代表挖矿难度
        '''
        time_start = time.clock()

        # 计算哈希
        while self.hash[0:diffculty] != ''.join(['0']*diffculty):
            self.nonce = self.nonce + 1
            self.hash = self.calculate_hash()

        print("挖到区块{0},耗时{1}秒".format(self.hash, time.clock()-time_start))