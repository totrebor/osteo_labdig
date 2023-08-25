


class LDBox:
    

    def __init__(self, cloud):
        self._cloud = cloud


    def run(self):
        obb = self._cloud.get_oriented_bounding_box()
        obbr = self._cloud.get_oriented_bounding_box(robust=True)
        return { 'obb': obb, 'obbr': obbr }