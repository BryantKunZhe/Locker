 # -*- coding:utf-8 -*- 

import argparse
import os
import zipfile

import crypto

parser = argparse.ArgumentParser(description = "Protect your privacy with Locker!")
group = parser.add_mutually_exclusive_group()
group.add_argument("-e", "--encrypt", action = "store_true", 
	help = "If you want to encrypt your file or folder, please turn on this flag")
group.add_argument("-d", "--decrypt", action = "store_true", 
	help = "If you want to decrypt your encrypted file or folder, please turn on this flag")
parser.add_argument("filepath", help = "The file or folder you want to encrypt or decrypt(\
	e.g. locker.mp4, /usr/video, locker.mp4.en")
parser.add_argument("password", help = "Your encryption or decryption key")
parser.add_argument("-o", "--output", help = "The output folder(e.g. /usr/tmp), default[temporary folder]")
args = parser.parse_args()

if not(args.decrypt or args.encrypt):
	print("Please specify the encrypt or decrypt flag!")
else:
	filepath = args.filepath
	password = args.password
	output = args.output

	# To ensure the length of password within 16, 24 or 32
	if len(password) < 16:
		password = password + (' ' * (16 - len(password)))
	if len(password) > 16 and len(password) < 24:
		password = password + (' ' * (24 - len(password)))
	if len(password) > 24 and len(password) < 32:
		password = password + (' ' * (32 - len(password)))
	if 32 < len(password):
		password = password = password[0:32]

	'''
	Return the last index the substring sub is found in the string s.
	Return -1 on Failure.
	'''
	def reverse_find(s, sub):
		index = -1
		while True:
			temp_index = s.find(sub, index + 1)
			if temp_index == -1:
				break
			else:
				index = temp_index
		return index

	# Encrypt file/folder
	if args.encrypt :
		if os.path.isdir(filepath):
			# Get the folder
			slash_position = reverse_find(filepath, '/')
			folder = filepath[slash_position + 1:]
			# archive the folder
			zip_filename = folder + ".zip"
			print("archive the folder " + zip_filename + "...")
			zip = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
			for root, dirs, files in os.walk(filepath) :
				for file in files :
					abspath = os.path.join(root, file)
					relpath = os.path.relpath(os.path.join(root, file), os.path.join(filepath, '..'))
					try: 
						zip.write(relpath)
					except:
						zip.write(abspath, arcname = relpath)
			zip.close()

			# Encrypt the archive
			c = crypto.crypto()
			if output:
				if os.path.isdir(output):
					print("encrypting...")
					c.encrypt_file(password, zip_filename, output_path = output)
					os.remove(zip_filename)
				else:
					print("-o --output should be a folder!")
			else:
				print("encrypting...")
				c.encrypt_file(password, zip_filename)
				os.remove(zip_filename)

		else:
			# Get the filename
			slash_position = reverse_find(filepath, '/')
			filename = filepath[slash_position + 1:]

			# Encrypt the file
			if filepath[0] == '.' and filepath[1] != '.':
				path = filepath[1:slash_position]
			else:
				path = filepath[0:slash_position + 1]
			c = crypto.crypto(cwd = path)
			if output:
				if os.path.isdir(output):
					print("encrypting...")
					c.encrypt_file(password, filename, output_path = output)
				else:
					print("-o --output should be a folder!")
			else:
				print("encrypting...")
				c.encrypt_file(password, filename)

	if args.decrypt:
		slash_position = reverse_find(filepath, '/')
		encrypt_filename = filepath[slash_position + 1:]
		if filepath[0] == '.' and filepath[1] != '.':
			path = filepath[1:slash_position]
		else:
			path = filepath[0:slash_position + 1]
		c= crypto.crypto(cwd = path)
		if output:
			if os.path.isdir(output):
				print("decrypting...")
				c.decrypt_file(password, encrypt_filename, output)
			else:
				print("-o --output should be a folder")
		else:
			print("decrypting...")
			c.decrypt_file(password, encrypt_filename)