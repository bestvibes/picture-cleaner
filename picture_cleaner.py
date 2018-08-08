#!/usr/bin/env python3

import os
import sys
import tkinter
from PIL import Image, ImageTk
import concurrent.futures
from io import BytesIO
from functools import partial
from subprocess import Popen, DEVNULL

class PictureCleaner(object):
	def __init__(self, *args, **kwargs):
		self.root = tkinter.Tk(className="Picture Cleaner")
		self.canvas = tkinter.Canvas(self.root, *args, **kwargs)
		self.canvas.pack(expand="yes", fill="both")

		# Not Resizable
		self.root.resizable(width=0, height=0)

	def show(self, img_folder_path, exts=['JPG', 'ARW']):
		assert os.path.isdir(img_folder_path)

		self.exts = exts
		self.img_folder_path = img_folder_path
		files = os.listdir(self.img_folder_path)
		jpgs = filter(lambda img_filename: ".jpg" == os.path.splitext(img_filename)[1].lower(), files)
		img_path_list = list(map(lambda jpg_filename: os.path.join(self.img_folder_path, jpg_filename), jpgs))

		if (len(img_path_list) == 0):
			print(f"No valid JPG pictures in {self.img_folder_path}!")
			return

		self.img_w = self.canvas.winfo_screenwidth()
		self.img_h = self.canvas.winfo_screenheight() - 150 # to avoid dock

		self.img_index = 0

		self.num_imgs = len(img_path_list)
		self.img_path_list = img_path_list
		self.img_list = []
		self.load_images(img_path_list)

		# useful in the future for undo functionality
		self.num_bad_imgs = 0
		self.bad_img_path_list = []
		self.bad_img_list = []

		self.bad_img_folder_path = os.path.join(img_folder_path, 'bad')
		try:
			os.mkdir(self.bad_img_folder_path)
		except OSError:
			# dir already exists
			pass

		self.set_window_settings()
		self.create_img_view()
		self.create_buttons()

		self.update_image()

		self.root.mainloop()

	def load_images(self, img_path_list):
		print(f"Loading {self.num_imgs} images...")
		self.img_list = []
		num_done = 0
		with concurrent.futures.ThreadPoolExecutor() as executor:
			for img_path, img_data in zip(img_path_list, executor.map(partial(self.get_tk_image, self.img_w, self.img_h), img_path_list)):
				try:
					self.img_list.append(ImageTk.PhotoImage(data=img_data))
				except Exception as exc:
					print('%r generated an exception: %s' % (img_path, exc))
					sys.exit(1)
				else:
					num_done += 1
					print(f"Loaded {num_done}/{self.num_imgs}...", end="\r")

		print("\nLoaded images!")

	def update_image(self):
		if (self.img_index == -1):
			self.img_index = self.num_imgs - 1
		elif (self.img_index >= self.num_imgs):
			self.img_index = 0

		img = self.img_list[self.img_index]
		self.canvas.itemconfig(self.img_view, image=img)

		filename = os.path.basename(self.img_path_list[self.img_index])
		self.root.title(filename)
		return

	def previous_image(self, event=None):
		self.img_index -= 1
		self.update_image()

	def next_image(self, event=None):
		self.img_index += 1
		self.update_image()

	def preview_current_image(self, event=None):
		if sys.platform == 'darwin':
			Popen(["qlmanage", "-p", self.img_path_list[self.img_index]], stdout=DEVNULL, stderr=DEVNULL)
		else:
			print("Preview only supported on OS X for now!")

	def remove_raw(self, event=None):
		self.mark_current_image_bad(exts=['ARW'])

	def mark_current_image_bad(self, event=None, exts=None):
		if not exts:
			exts = self.exts

		bad_img_path = self.img_path_list[self.img_index]

		print(f"moving {exts} to bad for: {bad_img_path}")
		bad_img_path_wo_ext = os.path.splitext(bad_img_path)[0]
		for path_to_move in map(lambda ext: f"{bad_img_path_wo_ext}.{ext}", exts):
			if os.path.exists(path_to_move):
				dst = os.path.join(self.bad_img_folder_path, os.path.basename(path_to_move))
				os.rename(path_to_move, dst)
		
		self.hide_current_image()

	def hide_current_image(self, event=None):
		self.bad_img_list.append(self.img_list.pop(self.img_index))
		self.bad_img_path_list.append(self.img_path_list.pop(self.img_index))
		self.num_imgs -= 1
		self.num_bad_imgs += 1

		self.update_image()

	def set_window_settings(self):
		self.canvas['width'] = self.canvas.winfo_screenwidth()
		self.canvas['height'] = self.canvas.winfo_screenheight()
		return

	def create_buttons(self):
		tkinter.Button(self.canvas, text=">", command=self.next_image, borderwidth=0).place(x=(self.canvas.winfo_screenwidth() / 1.05),y=(self.canvas.winfo_screenheight()/2))
		tkinter.Button(self.canvas, text="<", command=self.previous_image, borderwidth=0).place(x=20,y=(self.canvas.winfo_screenheight()/2))
		tkinter.Button(self.canvas, text="[B]ad", command=self.mark_current_image_bad, borderwidth=0).place(x=self.canvas.winfo_screenwidth() / 2 - 120,y=self.img_h)
		tkinter.Button(self.canvas, text="Remove [R]AW", command=self.remove_raw, borderwidth=0).place(x=self.canvas.winfo_screenwidth() / 2 - 50,y=self.img_h)
		tkinter.Button(self.canvas, text="[K]eep", command=self.hide_current_image, borderwidth=0).place(x=self.canvas.winfo_screenwidth() / 2 + 80,y=self.img_h)
		self.root.bind('<Left>', self.previous_image)
		self.root.bind('<Right>', self.next_image)
		self.root.bind('<space>', self.preview_current_image)
		self.root.bind('b', self.mark_current_image_bad)
		self.root.bind('r', self.remove_raw)
		self.root.bind('k', self.hide_current_image)
		self.canvas['bg']="white"
		return

	def create_img_view(self):
		self.img_view = self.canvas.create_image(self.img_w/2,
													self.img_h/2,
													image=self.img_list[self.img_index],
													anchor='center')

	def get_tk_image(self, w, h, path):
		buffered = BytesIO()
		img = Image.open(path)
		img.thumbnail((w, h), resample=Image.LANCZOS)
		img.save(buffered, format='JPEG', subsampling=0, quality=95, icc_profile=img.info.get('icc_profile'))
		img.close()
		return buffered.getvalue()

def main():
	if len(sys.argv) != 2:
		print(f"usage: {sys.argv[0]} [folder]")
		sys.exit(1)

	folder = os.path.abspath(sys.argv[1])

	PictureCleaner().show(folder)

if __name__ == "__main__":
	main()