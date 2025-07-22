class Img:
    def __init__(self):
        pass

    def read(self, path: pathlib.Path, target_size: Optional[Tuple[int, int]] = None):
        pass

    def clone(self):
        pass

    def draw_on(self, other_img: 'Img', x: int, y: int, alpha: float = 1.0):
        pass

    def resize(self, new_width: int, new_height: int):
        pass
