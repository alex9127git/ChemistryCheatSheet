import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

from atoms import *
from main_window import Ui_MainWindow
from substance import *
from database_searcher import *


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class CoefficientCalculationError(Exception):
    pass


class Window(QMainWindow, Ui_MainWindow):
    """Класс главного окна программы."""
    def __init__(self):
        """Инициализация окна программы."""
        super().__init__()
        self.setupUi(self)
        self.fill_reaction_btn.clicked.connect(self.fill_reaction)
        self.fill_coefficients_btn.clicked.connect(self.fill_coefficients)
        self.calculate_mass_btn.clicked.connect(self.calculate_mass)
        self.calculate_formula_btn.clicked.connect(self.calculate_formula)
        self.calculate_equation_btn.clicked.connect(self.calculate_equation)

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
        try:
            substance1 = get_substance(reagent1)
            substance2 = get_substance(reagent2)
        except IndexError:
            self.coefficients_error_lbl.setText("Не получилось расшифровать формулу вещества")
            return
        if substance1.__class__ == Acid:
            if substance2.__class__ == str:
                if compare_reactivity(substance2, substance1.cation) <= 0:
                    self.coefficients_error_lbl.setText(
                        "Металл не может вытеснить водород из кислоты"
                    )
                    return
        reagent3 = self.primary_output_edit.text()
        reagent4 = self.secondary_output_edit.text()
        self.coefficients_error_lbl.setText("")
        try:
            coeffs = self.calculate_coefficients(reagent1, reagent2, reagent3, reagent4)
        except CoefficientCalculationError:
            self.coefficients_error_lbl.setText("Не получилось расставить коэффициенты")
        else:
            coeff1, coeff2, coeff3, coeff4 = coeffs
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
        """Рассчитывает массовую долю выбранного элемента в выбранном веществе."""
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
        self.element_mass_edit.setText(f"{element_mass}")
        mass_fraction = element_mass / substance_mass
        self.mass_calculation_lbl.setText(
            f"{element_mass} / {substance_mass} = {mass_fraction}"
        )
        self.output_mass_lbl.setText(
            f"Массовая доля {element} в {substance} составляет {mass_fraction * 100:.3f}%"
        )

    def calculate_formula(self):
        """Рассчитывает формулу вещества по массовым долям его элементов."""
        edits = (self.element1_edit, self.element2_edit, self.element3_edit, self.element4_edit)
        spin_boxes = (self.element1_spinbox, self.element2_spinbox, self.element3_spinbox,
                      self.element4_spinbox)
        self.formula_error_lbl.setText("")
        try:
            element1 = self.element1_edit.text()
            if element1:
                get_element_type(element1)
            element2 = self.element2_edit.text()
            if element2:
                get_element_type(element2)
            element3 = self.element3_edit.text()
            if element3:
                get_element_type(element3)
            element4 = self.element4_edit.text()
            if element4:
                get_element_type(element4)
        except QueryNotFoundError:
            self.formula_error_lbl.setText("Не получилось найти один из элементов")
            return
        if len(list(filter(lambda x: x == "", (element1, element2, element3, element4)))) > 2:
            self.formula_error_lbl.setText("Нужно определить как минимум два элемента")
            return
        for i in range(4):
            if edits[i].text() == "":
                spin_boxes[i].setValue(0)
        elements = list(filter(lambda x: x != "", map(lambda x: x.text(), edits)))
        percentages = list(filter(lambda x: x > 0, map(lambda x: x.value(), spin_boxes)))
        if sum(percentages) != 100:
            self.formula_error_lbl.setText("Процентные соотношения в сумме должны давать 100%")
            return
        masses = list(map(lambda x: round(get_element_mass(x)), elements))
        quantity = len(elements)
        coeffs = [1] * quantity
        percent = list(map(lambda x: masses[x] * coeffs[x] / percentages[x], range(quantity)))
        while len(set(percent)) > 1:
            index = percent.index(min(percent))
            coeffs[index] += 1
            percent = list(map(lambda x: masses[x] * coeffs[x] / percentages[x], range(quantity)))
        self.output_formula_lbl.setText(f"{' : '.join(elements)} = {' : '.join(map(str, coeffs))}")

    def calculate_coefficients(self, reagent1, reagent2, reagent3, reagent4):
        atoms1 = Atoms(reagent1)
        atoms2 = Atoms(reagent2)
        atoms3 = Atoms(reagent3)
        atoms4 = Atoms(reagent4)
        coeff1 = coeff2 = coeff3 = coeff4 = 1
        if (atoms1 + atoms2).disparity(atoms3 + atoms4) == "too different":
            raise CoefficientCalculationError("Не получилось расставить коэффициенты")
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
        return [coeff1, coeff2, coeff3, coeff4]

    def calculate_equation(self):
        self.equation_error_lbl.setText("")
        reagent1 = self.eq_primary_input_edit.text()
        reagent2 = self.eq_secondary_input_edit.text()
        reagent3 = self.eq_primary_output_edit.text()
        reagent4 = self.eq_secondary_output_edit.text()
        reagents = [reagent1, reagent2, reagent3, reagent4]
        known_reagent = self.eq_substance1_edit.text()
        found_reagent = self.eq_substance2_edit.text()
        if known_reagent not in reagents or found_reagent not in reagents or known_reagent == "" \
                or found_reagent == "":
            self.equation_error_lbl.setText(
                "Известное или искомое вещество не находится в уравнении")
            return
        try:
            mass = float(self.eq_mass_edit.text().replace(",", "."))
        except ValueError:
            self.equation_error_lbl.setText("Не получилось прочитать массу")
            return
        try:
            coeffs = self.calculate_coefficients(*reagents)
        except CoefficientCalculationError:
            self.equation_error_lbl.setText("Не получилось расставить коэффициенты")
            return
        coeff1, coeff2, coeff3, coeff4 = coeffs
        str1 = f"{coeff1} {reagent1}" if reagent1 else ""
        str2 = f"{coeff2} {reagent2}" if reagent2 else ""
        str3 = f"{coeff3} {reagent3}" if reagent3 else ""
        str4 = f"{coeff4} {reagent4}" if reagent4 else ""
        part1 = " + ".join(filter(lambda x: x, (str1, str2)))
        part2 = " + ".join(filter(lambda x: x, (str3, str4)))
        self.equation_lbl.setText(
            f"Уравнение с коэффициентами: {part1} -> {part2}"
        )
        k_atoms = Atoms(known_reagent)
        r_atoms = Atoms(found_reagent)
        mol_mass, _ = k_atoms.calculate_molecular_mass()
        k_mol = mass / round(mol_mass)
        self.substance1_qty_lbl.setText(
            f"Количество известного вещества: {mass:.3f} / {round(mol_mass)} = {k_mol:.3f} моль")
        kc = coeffs[reagents.index(known_reagent)]
        rc = coeffs[reagents.index(found_reagent)]
        self.mol_fraction_lbl.setText(
            f"Мольное соотношение известного вещества к неизвестному: {kc}:{rc}")
        r_mol = k_mol / kc * rc
        mol_mass, _ = r_atoms.calculate_molecular_mass()
        r_mass = r_mol * round(mol_mass)
        self.substance2_mass_lbl.setText(
            f"Масса неизвестного вещества: {r_mol:.3f} * {round(mol_mass)} = {r_mass:.3f} г")
        self.output_equation_lbl.setText(f"Масса {found_reagent} = {r_mass:.3f}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
