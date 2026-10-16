"""Auxílio local de conferência: recupera glifos da fonte embutida do PDF fornecido.

O PDF possui ToUnicode vazio. Este texto NÃO substitui a imagem na revisão editorial.
Instalar requirements-dev.txt; saída local ignorada pelo Git e pela Vercel.
"""
import json
import re
import sys
import zlib
from io import BytesIO
from pathlib import Path

from fontTools.ttLib import TTFont


def stream(obj):
    start, end = obj.find(b"stream"), obj.rfind(b"endstream")
    if start < 0 or end < 0:
        return b""
    position = start + 6
    if obj[position:position + 2] == b"\r\n":
        position += 2
    elif obj[position:position + 1] in (b"\n", b"\r"):
        position += 1
    raw = obj[position:end]
    return zlib.decompress(raw) if b"/FlateDecode" in obj[:start] else raw


def extract(path):
    objects = {
        int(m[1]): m[2]
        for m in re.finditer(rb"(\d+)\s+\d+\s+obj\b(.*?)endobj", path.read_bytes(), re.S)
    }
    maps, cache = {}, {}
    for number, obj in objects.items():
        ref = re.search(rb"/DescendantFonts\s*\[\s*(\d+)", obj)
        if not ref:
            continue
        descendant = objects[int(ref[1])]
        descriptor = objects[int(re.search(rb"/FontDescriptor\s+(\d+)\s+\d+\s+R", descendant)[1])]
        key = int(re.search(rb"/FontFile2\s+(\d+)\s+\d+\s+R", descriptor)[1])
        if key not in cache:
            font = TTFont(BytesIO(stream(objects[key])))
            cache[key] = {font.getGlyphID(name): chr(code) for code, name in font.getBestCmap().items()}
        maps[number] = cache[key]
    pages = []
    for obj in objects.values():
        if not re.search(rb"/Type\s*/Page\b", obj):
            continue
        resource = objects[int(re.search(rb"/Resources\s+(\d+)\s+\d+\s+R", obj)[1])]
        fonts = {alias: maps[int(ref)] for alias, ref in re.findall(rb"/(G\d+)\s+(\d+)\s+\d+\s+R", resource)}
        content = stream(objects[int(re.search(rb"/Contents\s+(\d+)\s+\d+\s+R", obj)[1])])
        chunks = []
        for block in re.findall(rb"\bBT\b(.*?)\bET\b", content, re.S):
            font = re.search(rb"/(G\d+)\s+[\d.]+\s+Tf", block)
            mapping = fonts[font[1]] if font else {}
            for hex_value in re.findall(rb"<([0-9A-Fa-f]+)>", block):
                value = hex_value.decode()
                chunks.append("".join(mapping.get(int(value[i:i + 4], 16), "?") for i in range(0, len(value), 4)))
        pages.append(" ".join(chunks))
    return pages


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parent.parent
    pages = extract(root / "docs" / "Estatuto_GMS.pdf")
    output = root / ".local" / "statute-pages.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(pages)} páginas extraídas para conferência local.")
