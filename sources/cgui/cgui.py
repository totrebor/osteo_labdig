
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import platform
import numpy as np
import copy
from measures import LDBox

# custom GUI
class CGui:
    MENU_OPEN = 1
    MENU_BOX = 2
    MENU_QUIT = 3
    MENU_RESET = 4
    MENU_VOXEL01 = 5
    MENU_VOXEL1 = 6
    MENU_ABOUT = 21

    def __init__(self, width, height):
        isMacOS = (platform.system() == "Darwin")
        self._cloud = None
        self._model = None
        self._obbmin = None
        self._obbmax = None
        #self.settings = Settings()
        resource_path = gui.Application.instance.resource_path
        self.window = gui.Application.instance.create_window("Osteo LabDig", width, height)
        w = self.window  # to make the code more concise

        # 3D widget
        self._scene = gui.SceneWidget()
        self._scene.scene = rendering.Open3DScene(w.renderer)
        self._material = rendering.MaterialRecord()
        self._material.base_color =  [0.9, 0.9, 0.9, 1.0]
        self._material.shader = "defaultLit"

        em = w.theme.font_size
        separation_height = int(round(0.5 * em))

        ## ---- Panel ----
        self._panel = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        view_ctrls = gui.CollapsableVert("Measures", 0.25 * em, gui.Margins(em, 0, 0, 0))
        
        self._min_box_0 = gui.Label("")
        self._min_box_1 = gui.Label("")
        self._min_box_2 = gui.Label("")
        view_ctrls.add_child(gui.Label("Min box"))
        view_ctrls.add_child(self._min_box_0)
        view_ctrls.add_child(self._min_box_1)
        view_ctrls.add_child(self._min_box_2)

        self._max_box_0 = gui.Label("")
        self._max_box_1 = gui.Label("")
        self._max_box_2 = gui.Label("")
        view_ctrls.add_child(gui.Label("Max box"))
        view_ctrls.add_child(self._max_box_0)
        view_ctrls.add_child(self._max_box_1)
        view_ctrls.add_child(self._max_box_2)
        
        self._panel.add_child(view_ctrls)

        # ---- Menu ----
        # The menu is global (because the macOS menu is global), so only create
        # it once, no matter how many windows are created
        if gui.Application.instance.menubar is None:
            if isMacOS:
                app_menu = gui.Menu()
                app_menu.add_item("About", CGui.MENU_ABOUT)
                app_menu.add_separator()
                app_menu.add_item("Quit", CGui.MENU_QUIT)

            self._file_menu = gui.Menu()
            self._file_menu.add_item("Open...", CGui.MENU_OPEN)

            if not isMacOS:
                self._file_menu.add_separator()
                self._file_menu.add_item("Quit", CGui.MENU_QUIT)

            self._data_menu = gui.Menu()
            self._data_menu.add_item("Reset", CGui.MENU_RESET)
            self._data_menu.add_item("Voxel 0.1", CGui.MENU_VOXEL01)
            self._data_menu.add_item("Voxel 1", CGui.MENU_VOXEL1)

            self._measures_menu = gui.Menu()
            self._measures_menu.add_item("Box measure", CGui.MENU_BOX)

            self._help_menu = gui.Menu()
            self._help_menu.add_item("About", CGui.MENU_ABOUT)
            self._menu = gui.Menu()

            self._menu.add_menu("File", self._file_menu)
            self._menu.add_menu("Data", self._data_menu)
            self._menu.add_menu("Measures", self._measures_menu)

            if isMacOS:
                # macOS will name the first menu item for the running application
                # (in our case, probably "Python"), regardless of what we call
                # it. This is the application menu, and it is where the
                # About..., Preferences..., and Quit menu items typically go.
                # Don't include help menu unless it has something more than
                # About...
                pass
            else:
                self._menu.add_menu("Help", self._help_menu)
            gui.Application.instance.menubar = self._menu

        # The menubar is global, but we need to connect the menu items to the
        # window, so that the window can call the appropriate function when the
        # menu item is activated.
        w.set_on_menu_item_activated(CGui.MENU_OPEN, self._on_menu_open)
        w.set_on_menu_item_activated(CGui.MENU_BOX, self._on_menu_box)
        w.set_on_menu_item_activated(CGui.MENU_RESET, self._on_menu_reset)
        w.set_on_menu_item_activated(CGui.MENU_VOXEL01, self._on_menu_voxel01)
        w.set_on_menu_item_activated(CGui.MENU_VOXEL1, self._on_menu_voxel1)
        w.set_on_menu_item_activated(CGui.MENU_QUIT, self._on_menu_quit)
        w.set_on_menu_item_activated(CGui.MENU_ABOUT, self._on_menu_about)
        self._enable_measures_menus(False)
        self._enable_data_menus(False)
        # ----

        w.set_on_layout(self._on_layout)
        w.add_child(self._scene)
        w.add_child(self._panel)


    def _on_layout(self, layout_context):
        # The on_layout callback should set the frame (position + size) of every
        # child correctly. After the callback is done the window will layout
        # the grandchildren.
        r = self.window.content_rect
        self._scene.frame = r
        width = 17 * layout_context.theme.font_size
        height = min(
            r.height,
            self._panel.calc_preferred_size(layout_context, gui.Widget.Constraints()).height
        )
        self._panel.frame = gui.Rect(r.get_right() - width, r.y, width, height)


    def _enable_measures_menus(self, enabled: bool):
        self._measures_menu.set_enabled(CGui.MENU_BOX, enabled)


    def _enable_data_menus(self, enabled: bool):
        self._data_menu.set_enabled(CGui.MENU_RESET, enabled)
        self._data_menu.set_enabled(CGui.MENU_VOXEL01, enabled)
        self._data_menu.set_enabled(CGui.MENU_VOXEL1, enabled)


    def _on_load_dialog_done(self, filename):
        self.window.close_dialog()
        self.load(filename)


    def load(self, path):
        self._scene.scene.clear_geometry()
        self._cloud = None
        self._model = None
        self._obbmin = None
        self._obbmax = None

        try:
            self._cloud = o3d.io.read_point_cloud(path, "xyzn")
        except Exception:
            pass

        if self._cloud is not None:
            print("[Info] Successfully read", path)
            if not self._cloud.has_normals():
                self._cloud.estimate_normals()
            self._cloud.normalize_normals()
        else:
            print("[WARNING] Failed to read points", path)
        
        if self._cloud is not None:
            try:
                UNLIT = "defaultUnlit"
                LIT = "defaultLit"
                NORMALS = "normals"
                DEPTH = "depth"
                materials = {
                    LIT: rendering.MaterialRecord(),
                    UNLIT: rendering.MaterialRecord(),
                    NORMALS: rendering.MaterialRecord(),
                    DEPTH: rendering.MaterialRecord()
                }
                materials[LIT].base_color = [0.9, 0.9, 0.9, 1.0]
                materials[LIT].shader = LIT
                materials[UNLIT].base_color = [0.9, 0.9, 0.9, 1.0]
                materials[UNLIT].shader = UNLIT
                materials[NORMALS].shader = NORMALS
                materials[DEPTH].shader = DEPTH

                #self._cloud = self._cloud.voxel_down_sample(voxel_size=0.1)
                #print(self._cloud.get_center())
                #origin = np.array([0, 0, 0], dtype=np.float64)
                #self._cloud = self._cloud.translate(origin, True)
                self._cloud = self._cloud.translate((0, 0, 0), relative=False)
                self._cloud = self._cloud.remove_duplicated_points()
                #print(self._cloud.get_center())
                self._model = copy.deepcopy(self._cloud)
                self._scene.scene.add_geometry("__model___", self._model, self._material)
                bounds = self._scene.scene.bounding_box
                self._scene.setup_camera(60, bounds, bounds.get_center())
                self._enable_measures_menus(True)
                self._enable_data_menus(True)
            except Exception as e:
                print(e)


    def _on_file_dialog_cancel(self):
        self.window.close_dialog()


    def _on_menu_open(self):
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load",self.window.theme)
        dlg.add_filter(".ld", "3D xyzn file (.ld)")

        # A file dialog MUST define on_cancel and on_done functions
        dlg.set_on_cancel(self._on_file_dialog_cancel)
        dlg.set_on_done(self._on_load_dialog_done)
        self.window.show_dialog(dlg)


    def _on_menu_quit(self):
        gui.Application.instance.quit()


    def _on_menu_reset(self):
        if self._cloud is not None:
            self._scene.scene.clear_geometry()
            self._model = copy.deepcopy(self._cloud)
            self._scene.scene.add_geometry("__model___", self._model, self._material)


    def _on_menu_voxel01(self):
        if self._cloud is not None:
            self._scene.scene.clear_geometry()
            self._model = copy.deepcopy(self._cloud)
            self._model = self._model.voxel_down_sample(voxel_size=0.1)
            self._scene.scene.add_geometry("__model___", self._model, self._material)


    def _on_menu_voxel1(self):
        if self._cloud is not None:
            self._scene.scene.clear_geometry()
            self._model = copy.deepcopy(self._cloud)
            self._model = self._model.voxel_down_sample(voxel_size=1)
            self._scene.scene.add_geometry("__model___", self._model, self._material)


    def box_measure(self):
        if self._model is not None:
            box = LDBox(self._model)
            boxes = box.run()
            self._obbmin = boxes["obbmin"]
            self._obbmax = boxes["obbmax"]
            material = rendering.MaterialRecord()
            material.base_color =  [1, 1, 0, 1.0]
            material.shader = "defaultLit"
            self._scene.scene.add_geometry("__obbmin___", self._obbmin, material)
            material.base_color =  [0, 0, 1, 1.0]
            material.shader = "defaultLit"
            self._scene.scene.add_geometry("__obbmax___", self._obbmax, material)
            print(self._obbmin)
            print(self._obbmax)
            extent = self._obbmin.extent
            self._min_box_0.text = str(extent[0])
            self._min_box_1.text = str(extent[1])
            self._min_box_2.text = str(extent[2])
            extent = self._obbmax.extent
            self._max_box_0.text = str(extent[0])
            self._max_box_1.text = str(extent[1])
            self._max_box_2.text = str(extent[2])


    def _on_menu_box(self):
        self.box_measure()


    def _on_about_ok(self):
        self.window.close_dialog()


    def _on_menu_about(self):
        # Show a simple dialog. Although the Dialog is actually a widget, you can
        # treat it similar to a Window for layout and put all the widgets in a
        # layout which you make the only child of the Dialog.
        em = self.window.theme.font_size
        dlg = gui.Dialog("About")

        # Add the text
        dlg_layout = gui.Vert(em, gui.Margins(em, em, em, em))
        dlg_layout.add_child(gui.Label("Osteo LabDig"))

        # Add the Ok button. We need to define a callback function to handle
        # the click.
        ok = gui.Button("OK")
        ok.set_on_clicked(self._on_about_ok)

        # We want the Ok button to be an the right side, so we need to add
        # a stretch item to the layout, otherwise the button will be the size
        # of the entire row. A stretch item takes up as much space as it can,
        # which forces the button to be its minimum size.
        h = gui.Horiz()
        h.add_stretch()
        h.add_child(ok)
        h.add_stretch()
        dlg_layout.add_child(h)

        dlg.add_child(dlg_layout)
        self.window.show_dialog(dlg)
