class GameBuilder:
    def __init__(self, root_folder: pathlib.Path, 
                 board_width: int, board_height: int,
                 cell_width_pix: int, cell_height_pix: int, 
                 board_image_file: str):
        pass

    def _read_board_layout(self, board_file: pathlib.Path) -> List[Tuple[str, Tuple[int, int]]]:
        pass

    def build_game(self, board_file: str) -> Game:
        pass
