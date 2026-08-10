from andover_automation.SupportFiles.Interface import App
from PIL import Image, ImageTk
import os
from pathlib import Path

def main():
    app = App()
    app.wm_protocol(func=app.destroy)

    # Added Andover Image as Icon
    # Get the package directory to locate images
    package_dir = Path(__file__).parent
    image_path = package_dir / "SupportFiles" / "images" / "Andover-Cambridge-Mutual.png"
    
    advr_image1 = ImageTk.PhotoImage(Image.open(image_path).resize((64, 64)))
    app.after(100, lambda: app.iconphoto(False, advr_image1))
    app.mainloop()

if __name__ == '__main__':
    main()
