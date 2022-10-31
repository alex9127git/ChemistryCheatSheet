import sqlite3


def get_anion_charge(anion):
    """Возвращает заряд аниона из базы данных по его формуле."""
    con = sqlite3.connect("elements_db.sqlite")
    cur = con.cursor()
    result = cur.execute(f"select charge from anions where formula = '{anion}'").fetchone()
    con.close()
    return result[0]


def get_element_type(element):
    """Возвращает тип элемента из базы данных по его символу."""
    con = sqlite3.connect("elements_db.sqlite")
    cur = con.cursor()
    result = cur.execute(
        f"""select type from element_types where id = (
        select type from elements where symbol = '{element}')"""
    ).fetchone()
    con.close()
    if result:
        return result[0]
    else:
        return ""


def get_acid_from_oxide(oxide):
    """По оксиду находит кислоту из базы данных, которая создается с помощью этого оксида и воды."""
    con = sqlite3.connect("elements_db.sqlite")
    cur = con.cursor()
    result = cur.execute(
        f"""select acid from anions where oxide = '{oxide}'"""
    ).fetchone()
    con.close()
    if result:
        return result[0]
    else:
        return ""


def get_anion(formula):
    """Находит в формуле соли или кислоты кислотный остаток (анион)."""
    con = sqlite3.connect("elements_db.sqlite")
    cur = con.cursor()
    result = sorted(map(lambda x: x[0], cur.execute(
        f"""select formula from anions"""
    ).fetchall()), key=lambda x: -len(x))
    con.close()
    for anion in result:
        if anion in formula and not formula.startswith(anion):
            return anion
    return ""


def compare_reactivity(element1, element2):
    """Сравнивает электроотрицательность двух металлов. Возвращает положительное число, если первый
    металл находится в ряду электрохимических напряжений левее второго, или отрицательное число,
    если второй металл левее первого в этом ряду. Если два элемента одинаковые, возвращает 0."""
    con = sqlite3.connect("elements_db.sqlite")
    cur = con.cursor()
    try:
        reactivity1 = cur.execute(
            f"""select reactivity from reactivity where element = 
            (select id from elements where symbol = '{element1}')"""
        ).fetchone()[0]
        reactivity2 = cur.execute(
            f"""select reactivity from reactivity where element = 
            (select id from elements where symbol = '{element2}')"""
        ).fetchone()[0]
        return reactivity2 - reactivity1
    except TypeError:
        return 0


def get_cation_charge(cation):
    """Возвращает заряд катиона из базы данных по его формуле."""
    con = sqlite3.connect("elements_db.sqlite")
    cur = con.cursor()
    result = cur.execute(
        f"""select charge from reactivity where element = 
        (select id from elements where symbol = '{cation}')"""
    ).fetchone()
    con.close()
    if result:
        return result[0]
    else:
        return ""
