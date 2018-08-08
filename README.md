# picture-cleaner
A tool I made to sift through pictures I take on my camera. It shows all the jpg images in a specified folder, and if you mark one bad, it'll create a subdirectory named `bad` and move the image along with all its other extension versions into that folder. This is super handy for me since my camera shoots in both RAW and JPEG.

This app only moves files around and will not delete anything, so it is perfectly safe to use. I do not want a bug to delete valuable pictures!

After you specify a directory to open, this app will preload the entire directory's JPEG images into memory which may take a minute or two, the progress is shown in the console. I chose the tradeoff memory consumption for speed, since I have tons of RAM and was too lazy to write the code to lazy-load images in the background.

Keep in mind that the image view in the UI isn't full quality; I couldn't find a way to get `tkinter` to properly show full-res images. You can press `<space>` to open a full-res preview in macOS's Quick Look!

You may have to pass in the `exts` parameter to `PictureCleaner().show()` to get it to move the file extensions you want.

This is built very specifically for my purposes and only tested on a Mid-2015 15-inch Macbook Pro running macOS 10.12.6 and Python 3.6.6 with images shot on a Sony A6000. Feel free to make any modifications to fit your needs or submit a pull request!

## Usage:
`python3 picture_cleaner.py [folder_path]`

The only external library needed is [Pillow](https://pillow.readthedocs.io/en/latest/).

![Screenshot](screenshot.png)

## Features
### Key Bindings
`b`: move all specified versions of the shown image into the bad folder

`k`: keep all versions of the shown image and remove it from the image viewer

`r`: move only the raw version of the image to the bad folder and keep the jpg (useful if I don't plan on editing shown image)

`<space>`: open the image in full-res in macOS Quick Look

`arrow keys`: browse through images

Physical buttons are provided in the UI for each of the above as well.
