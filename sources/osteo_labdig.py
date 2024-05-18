import open3d as o3d
import open3d.visualization.gui as gui
import platform
from cgui.cgui import CGui


isMacOS = (platform.system() == "Darwin")

MENU_OPEN = 1
MENU_EXPORT = 2
MENU_QUIT = 3
MENU_SHOW_SETTINGS = 11
MENU_ABOUT = 21

def main():
    gui.Application.instance.initialize()
    w = CGui(1024, 768)
    gui.Application.instance.run()


if __name__ == "__main__":
    main()
