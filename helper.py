from collections import Counter, defaultdict
from twnorm.variants_generation import VariantsGenerator
from twnorm.wta_classifier import WTAclassifier


def stats():

    with open("errores.txt") as fd:
        lines = fd.read().split('\n')

    errores = [line.split(" | ") for line in lines]

    cf = WTAclassifier()
    generator = VariantsGenerator()

    repeated = defaultdict(int)
    resultados = dict()

    for i, e in enumerate(errores):
        o, mc, gc = e

        repeated["{} {} {}".format(o, mc, gc)] += 1

        if not cf.check(gc):
            resultados[i] = "not_expected"
        else:
            if gc in generator.generate(o):
                resultados[i] = "not_chosen"
            else:
                resultados[i] = "not_generated"

    return repeated, resultados, errores

# from helper import stats
# repeated, resultados = stats()
# repeated, resultados, errores = stats()
# errores
# resultados
# from collections import Counter
# c = Counter(list(resultados.values()))
# c
# not_expected = [x for x in resultados.keys() if resultados[x] == "not_expected"]
# not_generated = [x for x in resultados.keys() if resultados[x] == "not_generated"]
# not_chosen = [x for x in resultados.keys() if resultados[x] == "not_chosen"]
# len(not_expected)
# len(not_generated)
# len(not_chosen)
# not_expected
# errores
# not_expected_words = [errores[x][2] for x in not_expected]
# not_generated_words = [errores[x][2] for x in not_generated]
# not_chosen_words = [errores[x][2] for x in not_chosen]
# len(not_expected_words)
# len(not_generated_words)
# not_expected_words
# bajo = [w for w in not_expected_words if "_" in w]
# len(bajo)
# resto = [x for x in not_expected_words if x not in bajo]
# resto
# len(resto)
# barraguion = [w for w in resto if ("-" in w or "/" in w)]
# barraguion
# resto = [x for x in resto if x not in barraguion]
# resto
# len(resto)
# resto
# hist
# bajo
# barraguion
# resto
# err = [x for x in errores if x[2] in resto]
# err
# hist