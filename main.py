import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

from atoms import *
from main_window import Ui_MainWindow
from substance import *
from database_searcher import *


class Window(QMainWindow, Ui_MainWindow):
    """Класс главного окна программы."""
    def __init__(self):
        """Инициализация окна программы."""
        super().__init__()
        self.setupUi(self)
        self.fill_reaction_btn.clicked.connect(self.fill_reaction)
        self.fill_coefficients_btn.clicked.connect(self.fill_coefficients)
        self.calculate_mass_btn.clicked.connect(self.calculate_mass)

    def fill_reaction(self):
        """Пытается заполнить поля с продуктами реакции."""
        reagent1 = self.primary_input_edit.text()
        reagent2 = self.secondary_input_edit.text()
        try:
            substance1 = get_substance(reagent1)
            substance2 = get_substance(reagent2)
        except IndexError:
            self.coefficients_error_lbl.setText("Не получилось расшифровать формулу вещества")
            return
        if substance1.__class__ == Oxide:
            if substance1.oxide_type() == "кислотный":
                if reagent2 == "H2O":
                    try:
                        acid = get_acid_from_oxide(reagent1)
                        self.primary_output_edit.setText(acid)
                        self.secondary_output_edit.setText("")
                        self.coefficients_error_lbl.setText("")
                    except QueryNotFoundError:
                        self.coefficients_error_lbl.setText("Не получилось автозаполнить реакцию")
                elif substance2.__class__ == Base:
                    try:
                        acid = get_substance(get_acid_from_oxide(reagent1))
                        salt = Salt(substance2.cation, substance2.cation_charge,
                                    acid.anion)
                        self.primary_output_edit.setText(str(salt))
                        self.secondary_output_edit.setText("H2O")
                        self.coefficients_error_lbl.setText("")
                    except QueryNotFoundError:
                        self.coefficients_error_lbl.setText("Не получилось автозаполнить реакцию")
                elif substance2.__class__ == Oxide and substance2.oxide_type() == "основный":
                    try:
                        acid = get_substance(get_acid_from_oxide(reagent1))
                        salt = Salt(substance2.cation, substance2.cation_charge,
                                    acid.anion)
                        self.primary_output_edit.setText(str(salt))
                        self.secondary_output_edit.setText("")
                        self.coefficients_error_lbl.setText("")
                    except QueryNotFoundError:
                        self.coefficients_error_lbl.setText("Не получилось автозаполнить реакцию")
            elif substance1.oxide_type() == "основный":
                if reagent2 == "H2O" and get_element_type(substance1.cation) in (
                        "щелочный металл", "щелочно-земельный металл"):
                    base = Base(substance1.cation, substance1.cation_charge)
                    self.primary_output_edit.setText(str(base))
                    self.secondary_output_edit.setText("")
                    self.coefficients_error_lbl.setText("")
                elif substance2.__class__ == Oxide and substance2.oxide_type() == "кислотный":
                    try:
                        acid = get_substance(get_acid_from_oxide(reagent2))
                        salt = Salt(substance1.cation, substance1.cation_charge,
                                    acid.anion)
                        self.primary_output_edit.setText(str(salt))
                        self.secondary_output_edit.setText("")
                        self.coefficients_error_lbl.setText("")
                    except QueryNotFoundError:
                        self.coefficients_error_lbl.setText("Не получилось автозаполнить реакцию")
                elif substance2.__class__ == Acid:
                    salt = Salt(substance1.cation, substance1.cation_charge, substance2.anion)
                    self.primary_output_edit.setText(str(salt))
                    self.secondary_output_edit.setText("H2O")
                    self.coefficients_error_lbl.setText("")
        elif substance1.__class__ == Acid:
            if substance2.__class__ == str:
                if compare_reactivity(substance2, substance1.cation) > 0:
                    salt = Salt(substance2, get_cation_charge(substance2), substance1.anion)
                    self.primary_output_edit.setText(str(salt))
                    self.secondary_output_edit.setText("H2")
                    self.coefficients_error_lbl.setText("")
                else:
                    self.coefficients_error_lbl.setText(
                        "Металл не может вытеснить водород из кислоты"
                    )
            elif (substance2.__class__ == Oxide and substance2.oxide_type() == "основный") or \
                    (substance2.__class__ == Base):
                salt = Salt(substance2.cation, substance2.cation_charge, substance1.anion)
                self.primary_output_edit.setText(str(salt))
                self.secondary_output_edit.setText("H2O")
                self.coefficients_error_lbl.setText("")

    def fill_coefficients(self):
        """Заполняет коэффициенты реакции."""
        reagent1 = self.primary_input_edit.text()
        reagent2 = self.secondary_input_edit.text()
        substance1 = get_substance(reagent1)
        substance2 = get_substance(reagent2)
        if substance1.__class__ == Acid:
            if substance2.__class__ == str:
                if compare_reactivity(substance2, substance1.cation) <= 0:
                    self.coefficients_error_lbl.setText(
                        "Металл не может вытеснить водород из кислоты"
                    )
                    return
        reagent3 = self.primary_output_edit.text()
        reagent4 = self.secondary_output_edit.text()
        atoms1 = Atoms(reagent1)
        atoms2 = Atoms(reagent2)
        atoms3 = Atoms(reagent3)
        atoms4 = Atoms(reagent4)
        coeff1 = coeff2 = coeff3 = coeff4 = 1
        self.coefficients_error_lbl.setText("")
        if (atoms1 + atoms2).disparity(atoms3 + atoms4) == "too different":
            self.coefficients_error_lbl.setText("Не получилось расставить коэффициенты")
        else:
            while atoms1 * coeff1 + atoms2 * coeff2 != atoms3 * coeff3 + atoms4 * coeff4:
                element = (atoms1 * coeff1 + atoms2 * coeff2).disparity(
                    atoms3 * coeff3 + atoms4 * coeff4)
                count1 = (atoms1 * coeff1 + atoms2 * coeff2).atoms[element]
                count2 = (atoms3 * coeff3 + atoms4 * coeff4).atoms[element]
                lcc = lcm(count1, count2)
                c1 = lcc // count1
                c2 = lcc // count2
                if element in atoms1:
                    coeff1 *= c1
                if element in atoms2:
                    coeff2 *= c1
                if element in atoms3:
                    coeff3 *= c2
                if element in atoms4:
                    coeff4 *= c2
            str1 = f"{coeff1} {reagent1}" if reagent1 else ""
            str2 = f"{coeff2} {reagent2}" if reagent2 else ""
            str3 = f"{coeff3} {reagent3}" if reagent3 else ""
            str4 = f"{coeff4} {reagent4}" if reagent4 else ""
            part1 = " + ".join(filter(lambda x: x, (str1, str2)))
            part2 = " + ".join(filter(lambda x: x, (str3, str4)))
            self.output_reaction_lbl.setText(
                f"{part1} -> {part2}"
            )

    def calculate_mass(self):
        """Расчитывает массовую долю выбранного элемента в выбранном веществе."""
        substance = self.substance_edit.text()
        try:
            element = self.element_edit.text()
            get_element_type(element)
        except QueryNotFoundError:
            self.mass_error_lbl.setText("Не получилось найти элемент")
            return
        substance_atoms = Atoms(substance)
        substance_mass, expression = substance_atoms.calculate_molecular_mass()
        element_mass = get_element_mass(element) * substance_atoms.atoms.get(element, 0)
        self.substance_mass_edit.setText(expression)
        self.element_mass_edit.setText(f"{element_mass:.3f}")
        mass_fraction = element_mass / substance_mass
        self.mass_calculation_lbl.setText(
            f"{element_mass:.3f} / {substance_mass:.3f} = {mass_fraction:.5f}"
        )
        self.output_mass_lbl.setText(
            f"Массовая доля {element} в {substance} составляет {mass_fraction * 100:.3f}%"
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())
