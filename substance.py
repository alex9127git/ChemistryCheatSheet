import math


class Substance:
    def __init__(self, cation, cation_charge, anion, anion_charge):
        self.formula = ""
        self.cation = cation
        self.cation_charge = cation_charge
        self.anion = anion
        self.anion_charge = anion_charge
        self.cation_count = -self.anion_charge
        self.anion_count = self.cation_charge
        gcd = math.gcd(self.cation_count, self.anion_count)
        self.cation_count //= gcd
        self.anion_count //= gcd
        self.formula = self.get_cation_formula() + self.get_anion_formula()

    def __str__(self):
        return self.formula

    def get_cation_formula(self):
        if len(list(filter(lambda x: x.isupper(), self.cation))) > 1 and self.cation_count > 1:
            return f"({self.cation}){self.cation_count}"
        else:
            return f"{self.cation}{self.cation_count if self.cation_count > 1 else ''}"

    def get_anion_formula(self):
        if len(list(filter(lambda x: x.isupper(), self.anion))) > 1 and self.anion_count > 1:
            return f"({self.anion}){self.anion_count}"
        else:
            return f"{self.anion}{self.anion_count if self.anion_count > 1 else ''}"


class Oxide(Substance):
    def __init__(self, cation, valency):
        super(Oxide, self).__init__(cation, valency, "O", -2)


class Acid(Substance):
    def __init__(self, anion, valency):
        super(Acid, self).__init__("H", 1, anion, -valency)


class Base(Substance):
    def __init__(self, cation, valency):
        super(Base, self).__init__(cation, valency, "OH", -1)


class Salt(Substance):
    def __init__(self, cation, cation_valency, anion, anion_valency):
        super(Salt, self).__init__(cation, cation_valency, anion, -anion_valency)


def get_substance(formula):
    if formula.startswith("H"):
        cation_count = int(formula[1])
        index = 2
        while formula[index].isnumeric():
            cation_count = cation_count * 10 + formula[index]
            index += 1
        anion = formula[index:]
        return Acid(anion, cation_count)
    elif "OH" in formula:
        if formula.endswith("OH"):
            cation = formula[:-2]
            return Base(cation, 1)
        else:
            index = formula.index("OH")
            cation = formula[:index-1]
            cation_charge = int(formula[index+3:])
            return Base(cation, cation_charge)
    elif "O" in formula:
        index = formula.index("O")
        if formula[index - 1] == "2":
            cation = formula[:index-1]
            cation_charge = 1 if formula.endswith("O") else int(formula[index + 1:])
        else:
            cation = formula[:index]
            cation_charge = (1 if formula.endswith("O") else int(formula[index + 1:])) * 2
        return Oxide(cation, cation_charge)


if __name__ == "__main__":
    print("Testing creating substances")
    print(Oxide("Ba", 2))
    print(Oxide("Fe", 3))
    print(Oxide("K", 1))
    print(Oxide("P", 5))
    print(Acid("SiO3", 2))
    print(Acid("SO4", 2))
    print(Acid("PO4", 3))
    print(Base("K", 1))
    print(Base("Ba", 2))
    print(Base("Al", 3))
    print(Salt("Al", 3, "SO4", 2))
    print(Salt("Ba", 2, "Cl", 1))
    print(Salt("Ba", 2, "NO3", 1))
    print(Salt("NH4", 1, "SO4", 2))
    print("-----")
    print("Testing getting substances from formula")
    acid1 = get_substance("H3PO4")
    print(acid1.__class__)
    print(acid1)
    base1 = get_substance("KOH")
    print(base1.__class__)
    print(base1)
    base2 = get_substance("Ba(OH)2")
    print(base2.__class__)
    print(base2)
    oxide1 = get_substance("Fe2O3")
    print(oxide1.__class__)
    print(oxide1)
    oxide2 = get_substance("K2O")
    print(oxide2.__class__)
    print(oxide2)
    oxide3 = get_substance("BaO")
    print(oxide3.__class__)
    print(oxide3)
    oxide4 = get_substance("CO2")
    print(oxide4.__class__)
    print(oxide4)
