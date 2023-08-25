
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import platform
from measures import LDBox

# custom GUI
class CGui:
    MENU_OPEN = 1
    MENU_BOX = 2
    MENU_QUIT = 3
    MENU_ABOUT = 21

    def __init__(self, width, height):
        isMacOS = (platform.system() == "Darwin")
        self._cloud = None
        self._obb = None
        self._obbr = None

        resource_path = gui.Application.instance.resource_path
        self.window = gui.Application.instance.create_window("Osteo LabDig", width, height)
        w = self.window  # to make the code more concise

        # 3D widget
        self._scene = gui.SceneWidget()
        self._scene.scene = rendering.Open3DScene(w.renderer)

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
            self._data_menu.add_item("Box measure", CGui.MENU_BOX)

            self._help_menu = gui.Menu()
            self._help_menu.add_item("About", CGui.MENU_ABOUT)
            self._menu = gui.Menu()

            if isMacOS:
                # macOS will name the first menu item for the running application
                # (in our case, probably "Python"), regardless of what we call
                # it. This is the application menu, and it is where the
                # About..., Preferences..., and Quit menu items typically go.
                self._menu.add_menu("File", self._file_menu)
                self._menu.add_menu("Data", self._data_menu)
                # Don't include help menu unless it has something more than
                # About...
            else:
                self._menu.add_menu("File", self._file_menu)
                self._menu.add_menu("Data", self._data_menu)
                self._menu.add_menu("Help", self._help_menu)
            gui.Application.instance.menubar = self._menu

        # The menubar is global, but we need to connect the menu items to the
        # window, so that the window can call the appropriate function when the
        # menu item is activated.
        w.set_on_menu_item_activated(CGui.MENU_OPEN, self._on_menu_open)
        w.set_on_menu_item_activated(CGui.MENU_BOX, self._on_menu_box)
        w.set_on_menu_item_activated(CGui.MENU_QUIT, self._on_menu_quit)
        w.set_on_menu_item_activated(CGui.MENU_ABOUT, self._on_menu_about)
        self._enable_cloud_menus(False)
        # ----

        w.add_child(self._scene)


    def _enable_cloud_menus(self, enabled: bool):
        self._data_menu.set_enabled(CGui.MENU_BOX, enabled)


    def _on_load_dialog_done(self, filename):
        self.window.close_dialog()
        self.load(filename)


    def load(self, path):
        self._scene.scene.clear_geometry()
        self._cloud = None
        self._obb = None
        self._obbr = None

#        geometry = None
#        geometry_type = o3d.io.read_file_geometry_type(path)
#
#        mesh = None
#        if geometry_type & o3d.io.CONTAINS_TRIANGLES:
#            mesh = o3d.io.read_triangle_model(path)
#        if mesh is None:
#            print("[Info]", path, "appears to be a point cloud")
#            cloud = None
#            try:
#                cloud = o3d.io.read_point_cloud(path)
#            except Exception:
#                pass
#            if cloud is not None:
#                print("[Info] Successfully read", path)
#                if not cloud.has_normals():
#                    cloud.estimate_normals()
#                cloud.normalize_normals()
#                geometry = cloud
#            else:
#                print("[WARNING] Failed to read points", path)
#
#        if geometry is not None or mesh is not None:
#            try:
#                if mesh is not None:
#                    # Triangle model
#                    self._scene.scene.add_model("__model__", mesh)
#                else:
#                    # Point cloud
#                    self._scene.scene.add_geometry("__model__", geometry,
#                                                   self.settings.material)
#                bounds = self._scene.scene.bounding_box
#                self._scene.setup_camera(60, bounds, bounds.get_center())
#            except Exception as e:
#                print(e)

        self._cloud = None
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

                material = rendering.MaterialRecord()
                material.base_color =  [0.9, 0.9, 0.9, 1.0]
                material.shader = "defaultLit"

                #self._cloud = self._cloud.voxel_down_sample(voxel_size=1)
                self._scene.scene.add_geometry("__model___", self._cloud, material)
                bounds = self._scene.scene.bounding_box
                self._scene.setup_camera(60, bounds, bounds.get_center())
                self._enable_cloud_menus(True)
            except Exception as e:
                print(e)


    def _on_file_dialog_cancel(self):
        self.window.close_dialog()


    def _on_menu_open(self):
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load",self.window.theme)
#        dlg.add_filter(
#            ".ply .stl .fbx .obj .off .gltf .glb",
#            "Triangle mesh files (.ply, .stl, .fbx, .obj, .off, "
#            ".gltf, .glb)")
#        dlg.add_filter(
#            ".xyz .xyzn .xyzrgb .ply .pcd .pts",
#            "Point cloud files (.xyz, .xyzn, .xyzrgb, .ply, "
#            ".pcd, .pts)")
#        dlg.add_filter(".ply", "Polygon files (.ply)")
#        dlg.add_filter(".stl", "Stereolithography files (.stl)")
#        dlg.add_filter(".fbx", "Autodesk Filmbox files (.fbx)")
#        dlg.add_filter(".obj", "Wavefront OBJ files (.obj)")
#        dlg.add_filter(".off", "Object file format (.off)")
#        dlg.add_filter(".gltf", "OpenGL transfer files (.gltf)")
#        dlg.add_filter(".glb", "OpenGL binary transfer files (.glb)")
#        dlg.add_filter(".xyz", "ASCII point cloud files (.xyz)")
#        dlg.add_filter(".xyzn", "ASCII point cloud with normals (.xyzn)")
#        dlg.add_filter(".xyzrgb", "ASCII point cloud files with colors (.xyzrgb)")
#        dlg.add_filter(".pcd", "Point Cloud Data files (.pcd)")
#        dlg.add_filter(".pts", "3D Points files (.pts)")
#        dlg.add_filter("", "All files")
        dlg.add_filter(".ld", "3D xyzn file (.ld)")

        # A file dialog MUST define on_cancel and on_done functions
        dlg.set_on_cancel(self._on_file_dialog_cancel)
        dlg.set_on_done(self._on_load_dialog_done)
        self.window.show_dialog(dlg)


    def _on_menu_quit(self):
        gui.Application.instance.quit()


    def box_measure(self):
        if self._cloud is not None:
            box = LDBox(self._cloud)
            boxes = box.run()
            self._obb = boxes["obb"]
            self._obbr = boxes["obbr"]
            # aabb = self._cloud.get_axis_aligned_bounding_box()
            #obb = self._cloud.get_oriented_bounding_box()
            material = rendering.MaterialRecord()
            material.base_color =  [1, 1, 0, 1.0]
            material.shader = "defaultLit"
            self._scene.scene.add_geometry("__obbr___", self._obbr, material)
            material.base_color =  [0, 0, 1, 1.0]
            material.shader = "defaultLit"
            self._scene.scene.add_geometry("__obb___", self._obb, material)


    def _on_menu_box(self):
        self.box_measure()


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
