from SupportFiles.Interface import App
from PIL import Image, ImageTk

def main():
  app = App()
  app.wm_protocol(func = app.destroy)

  # Added Andover Image as Icon
  advr_image1 = ImageTk.PhotoImage(Image.open("SupportFiles/images/Andover-Cambridge-Mutual.png").resize((64, 64)))  # Resize the image to fit the icon size
  app.after(100, lambda: app.iconphoto(False, advr_image1))  # Ensure the icon is set after the main loop starts
  app.mainloop()

if __name__ == '__main__':
  main()