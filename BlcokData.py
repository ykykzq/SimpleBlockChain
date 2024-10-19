import hashlib
class BlockData:
    def __init__(self):
        '''
        :param files: 存储当前区块记录了哪些文件
        '''
        self.files = []
    
    def add_file(self, file_path, author_hash):
        '''
        计算哈希值
        :param file_path: 要上传的文件的路径
        :param author_hash: 文件上传者的哈希值，实际上是公钥
        '''
        file_hash = self.calculate_file_hash(file_path)
        self.files.append((file_hash, author_hash))

    def calculate_file_hash(file_path):
        '''
        计算文件的哈希值
        :param file_path: 要计算哈希值的文件路径
        '''
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()  