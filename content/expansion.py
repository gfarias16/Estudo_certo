"""Lote editorial de 16/10/2026: 120 itens diretos e 120 análises de assertivas.

Os fatos e distratores são escritos em expansion.csv e conferidos no PDF.
Não há IA em runtime. Preserve a ordem deste lote; novas expansões são novos lotes.
"""
import csv
from collections import defaultdict
from pathlib import Path


def build_expansion(topics):
    with Path(__file__).with_suffix(".csv").open(encoding="utf-8", newline="") as source:
        facts = list(csv.DictReader(source, delimiter="|"))
    if len(facts) != 120:
        raise ValueError("O lote editorial exige exatamente 120 fatos conferidos.")
    excerpts, questions = {}, []
    by_topic = defaultdict(list)
    for index, fact in enumerate(facts):
        by_topic[fact["topic"]].append(index)
        key = f"exp-20261016-{index + 1:03}"
        excerpts[key] = (int(fact["page"]), fact["reference"], fact["excerpt"])
        explanation = f'{fact["reference"]}: {fact["correct"]}'
        options = [(fact["correct"], f"Correta. {explanation}")]
        options.extend(
            (fact[field], f'Incorreta: “{fact[field]}” contraria a regra. {explanation}')
            for field in ("wrong1", "wrong2", "wrong3")
        )
        style = "case" if fact["prompt"].startswith(("Um ", "Uma ", "A chefia", "Há ", "Não há", "Eliminado")) else "literal"
        questions.append((fact["topic"], key, style, fact["prompt"], options, explanation))
    classifications = [
        ((True, True), "As duas assertivas estão corretas."),
        ((True, False), "Somente a assertiva I está correta."),
        ((False, True), "Somente a assertiva II está correta."),
        ((False, False), "As duas assertivas estão incorretas."),
    ]
    for index, fact in enumerate(facts):
        peers = by_topic[fact["topic"]]
        partner_index = peers[(peers.index(index) + 1) % len(peers)]
        partner = facts[partner_index]
        # Distribui as quatro combinações sem vincular a classificação à letra
        # do gabarito, que é balanceada posteriormente pela importação.
        expected = classifications[(index * 7 + index // 4) % 4][0]
        statements = [
            item["correct"] if valid else item["wrong1"]
            for item, valid in zip((fact, partner), expected, strict=True)
        ]
        prompt = (
            f'Analise as assertivas sobre {topics[fact["topic"]].lower()}:\n\n'
            f'I — {statements[0]}\nII — {statements[1]}\n\nAssinale a classificação correta segundo o estatuto.'
        )
        analysis = " ".join(
            f'{label} está {"correta" if valid else "incorreta"}. {item["reference"]}: {item["correct"]}'
            for label, item, valid in zip(("I", "II"), (fact, partner), expected, strict=True)
        )
        options = [
            (label, f'{label} {"É a classificação correta." if truth == expected else "Não corresponde à análise."} {analysis}')
            for truth, label in sorted(classifications, key=lambda entry: entry[0] != expected)
        ]
        sources = (f"exp-20261016-{index + 1:03}", f"exp-20261016-{partner_index + 1:03}")
        questions.append((fact["topic"], sources, "comparison", prompt, options, analysis))
    return excerpts, questions
