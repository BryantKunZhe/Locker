import os
import random
import struct
from Crypto.Cipher import AES
from Crypto import Random

class crypto:
	def __init__(self, cwd = os.getcwd(), chunksize = 512*1024*1024):
		self.cwd = cwd
		self.chunksize = chunksize

	def encrypt_file(self, key, in_filename, output_path = '.'):
		out_filename = in_filename + ".en"
		iv = Random.new().read(AES.block_size)
		encryptor = AES.new(key, AES.MODE_CBC, iv)
		in_filename = os.path.join(self.cwd, in_filename)
		out_filename = os.path.join(output_path, out_filename)
		with open(in_filename, 'rb') as in_file:
			with open(out_filename, 'wb') as out_file:
				filesize = os.path.getsize(in_filename)
				magic_number = b'19970629'
				out_file.write(magic_number)
				if filesize < self.chunksize :
					con = in_file.read()
					if len(con) % 16 != 0:
						con = con + ' '.encode() * (16 - len(con) % 16)
						out_file.write(iv)
						out_file.write(encryptor.encrypt(con))
					else:
						out_file.write(iv)
						out_file.write(encryptor.encrypt(con))
				else :
					out_file.write(struct.pack('<Q', filesize))
					out_file.write(iv)

					while True:
						chunk = in_file.read(self.chunksize)
						if len(chunk) == 0:
							break
						elif len(chunk) % 16 != 0:
							chunk += ' '.encode() * (16 - len(chunk) % 16)
						out_file.write(encryptor.encrypt(chunk))

	def decrypt_file(self, key, in_filename, output_path = '.'):
		out_filename = in_filename[0: -3]
		in_filename = os.path.join(self.cwd, in_filename)
		out_filename = os.path.join(output_path, out_filename)
		with open(in_filename, 'rb') as in_file:
			with open(out_filename, 'wb') as out_file:
				magic_number = b'19970629'
				if in_file.read(8) == magic_number:
					filesize = os.path.getsize(in_filename)
					if filesize < self.chunksize:
						iv = in_file.read(16)
						con = in_file.read()
						decryptor = AES.new(key, AES.MODE_CBC, iv)
						out_file.write(decryptor.decrypt(con))
					else:
						original_size = struct.unpack('<Q', in_file.read(struct.calcsize('Q')))[0]
						iv = in_file.read(16)
						decryptor = AES.new(key, AES.MODE_CBC, iv)

						while True:
							chunk = in_file.read(self.chunksize)
							if len(chunk) == 0:
								break
							out_file.write(decryptor.decrypt(chunk))
						out_file.truncate(original_size)
				else:
					print("The file is damaged!")