


class LDBox:
    
    obbm = None
    obbo = None

    def __init__(self, cloud):
        self._cloud = cloud


    def run(self):
        self.obbmin = self._cloud.get_minimal_oriented_bounding_box()
        self.obbmax = self._cloud.get_oriented_bounding_box()

        return { 'obbmin': self.obbmin, 'obbmax': self.obbmax }