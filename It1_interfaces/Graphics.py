class Graphics:
    def __init__(self, sprites_folder: pathlib.Path, board: Board, loop: bool = True, fps: float = 6.0): pass
    def _load_sprites(self): pass
    def copy(self): pass
    def reset(self, cmd: Command): pass
    def update(self, now_ms: int): pass
    def get_img(self) -> Img: pass
