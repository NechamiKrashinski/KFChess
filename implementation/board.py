from dataclasses import dataclass

from .img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    cell_H_m: int
    cell_W_m: int
    W_cells: int
    H_cells: int
    img: Img

    # convenience, not required by dataclass
    def clone(self) -> "Board":
        new_img = Img()
        new_img.img = self.img.clone()  # העתקה עמוקה של המטריצה של התמונה
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m=self.cell_H_m,
            cell_W_m=self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=new_img
    )