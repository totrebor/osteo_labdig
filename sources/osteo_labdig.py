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
#    pcd1 = o3d.io.read_point_cloud("test_data/5/5_Project1_scan_1.asc", "xyzn")
#    print(pcd1)
#    o3d.visualization.draw_geometries([pcd1])
#    # We need to initialize the application, which finds the necessary shaders
#    # for rendering and prepares the cross-platform window abstraction.
#    gui.Application.instance.initialize()
#    gui.Application.instance.create_window("OSTEO_LABDIG", 900, 900)
#    if gui.Application.instance.menubar is None:
#        if isMacOS:
#            app_menu = gui.Menu()
#            app_menu.add_item("About", MENU_ABOUT)
#            app_menu.add_separator()
#            app_menu.add_item("Quit", MENU_QUIT)
#        file_menu = gui.Menu()
#        file_menu.add_item("Open...", MENU_OPEN)
#        file_menu.add_item("Export Current Image...", MENU_EXPORT)
#        if not isMacOS:
#            file_menu.add_separator()
#            file_menu.add_item("Quit", MENU_QUIT)
#        settings_menu = gui.Menu()
#        settings_menu.add_item("Lighting & Materials", MENU_SHOW_SETTINGS)
#        settings_menu.set_checked(MENU_SHOW_SETTINGS, True)
#        help_menu = gui.Menu()
#        help_menu.add_item("About", MENU_ABOUT)
#
#        menu = gui.Menu()
#        if isMacOS:
#            # macOS will name the first menu item for the running application
#            # (in our case, probably "Python"), regardless of what we call
#            # it. This is the application menu, and it is where the
#            # About..., Preferences..., and Quit menu items typically go.
#            menu.add_menu("Example", app_menu)
#            menu.add_menu("File", file_menu)
#            menu.add_menu("Settings", settings_menu)
#            # Don't include help menu unless it has something more than
#            # About...
#        else:
#            menu.add_menu("File", file_menu)
#            menu.add_menu("Settings", settings_menu)
#            menu.add_menu("Help", help_menu)
#        gui.Application.instance.menubar = menu
#
#    # Run the event loop. This will not return until the last window is closed.
#    gui.Application.instance.run()
    gui.Application.instance.initialize()
    w = CGui(1024, 768)
    gui.Application.instance.run()


if __name__ == "__main__":
    main()
