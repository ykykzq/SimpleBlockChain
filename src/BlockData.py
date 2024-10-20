import hashlib
import json
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class BlockData:
    def __init__(self):
        '''
        :param files: 存储当前区块记录了哪些文件
        '''
        self.files = []
    
    def add_file(self, file_path: str, author_hash_str: str):
        '''
        添加文件，实际上生成一个（用户公钥，加密后文件的哈希）键值对
        :param file_path: 要上传的文件的路径
        :param author_hash: 文件上传者的哈希值，实际上是公钥
        '''
        # 计算文件的哈希值
        file_hash_str = self.calculate_file_hash(file_path)
        # 使用文件哈希值作为密钥，对文件进行加密
        self.encrypt_file(file_path, file_hash_str)
        # 计算密文的哈希值
        enc_file_hash_str = self.calculate_file_hash(file_path + '.enc')
        # 将用户信息＆密文哈希值写入数据
        self.files.append((author_hash_str, enc_file_hash_str))

    def calculate_file_hash(self, file_path: str):
        '''
        计算文件的哈希值
        :param file_path: 要计算哈希值的文件路径
        '''
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest() 
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """根据密码和盐值生成密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt_file(self, file_path: str, password: str):
        """加密文件"""
        salt = os.urandom(16)  # 生成随机盐
        key = self.derive_key(password, salt)

        # 生成随机的初始化向量（IV）
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        with open(file_path, 'rb') as f:
            plaintext = f.read()

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # 将盐、IV 和密文写入输出文件
        with open(file_path + '.enc', 'wb') as f:
            f.write(salt + iv + ciphertext)

    def decrypt_file(self, encrypted_file_path: str, password: str):
        """解密文件"""
        with open(encrypted_file_path, 'rb') as f:
            # 读取盐、IV 和密文
            salt = f.read(16)
            iv = f.read(16)
            ciphertext = f.read()

        key = self.derive_key(password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # 写入解密后的文件
        with open(encrypted_file_path[:-4]+'.dec', 'wb') as f:  # 去掉 .enc 后缀
            f.write(plaintext)
            
    def to_dict(self):
        """将 BlockData 实例转换为字典"""
        return {
            'files': self.files,
        }

if __name__ == '__main__':
    '''
    测试功能
    '''

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

    # 向data中添加用户信息与文件信息
    data = BlockData()
    data.add_file('../data/file_example', public_key_content)

    # 尝试解密文件，使用文件哈希作为密钥
    data.decrypt_file('../data/file_example.enc',# 计算文件的哈希值
        data.calculate_file_hash('../data/file_example'))

    print(json.dumps(data.to_dict(), ensure_ascii=False))