from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[1]
pdf = pdfium.PdfDocument(str(ROOT / "Final_Thesis.pdf"))
out_dir = ROOT / "documentation" / "thesis_render"
out_dir.mkdir(parents=True, exist_ok=True)

for i, page in enumerate(pdf, start=1):
    bitmap = page.render(scale=1.7)
    image = bitmap.to_pil()
    image.save(out_dir / f"page-{i:02d}.png")

print(f"Rendered {len(pdf)} pages to {out_dir}")
