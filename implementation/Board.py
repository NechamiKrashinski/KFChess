from dataclasses import dataclass

from implementation.img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    W_cells: int
    H_cells: int
    img: Img

    # convenience, not required by dataclass
    def clone(self) -> "Board":
        new_img = Img()
        new_img.img = self.img.img.copy()  # העתקה עמוקה של המטריצה של התמונה
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=new_img
    )