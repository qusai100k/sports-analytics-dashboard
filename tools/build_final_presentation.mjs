import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/qusai/Documents/sports analytics";
const OUT = path.join(ROOT, "Sports_Analytics_Final_Presentation.pptx");
const slidesData = JSON.parse(await fs.readFile(path.join(ROOT, "presentation_assets", "slides.json"), "utf8"));

async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: style.fontSize ?? 24,
    bold: style.bold ?? false,
    color: style.color ?? "#eef4ff",
    typeface: style.typeface ?? "Aptos",
    alignment: style.alignment ?? "left",
  };
  return shape;
}

function addBox(slide, position, fill = "#111827", line = "#334155", radius = "rounded-xl") {
  return slide.shapes.add({
    geometry: "roundRect",
    position,
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
    shadow: "shadow-sm",
  });
}

async function addImage(slide, relPath, position, fit = "cover") {
  const fullPath = path.join(ROOT, relPath);
  const image = slide.images.add({
    blob: await readImageBlob(fullPath),
    contentType: relPath.toLowerCase().endsWith(".jpg") ? "image/jpeg" : "image/png",
    alt: relPath,
    fit,
    position,
    geometry: "roundRect",
    borderRadius: "rounded-xl",
  });
  return image;
}

function addFooter(slide, number) {
  addText(slide, "Sports Analytics Final Presentation", { left: 64, top: 675, width: 520, height: 24 }, { fontSize: 13, color: "#94a3b8", bold: true });
  addText(slide, String(number).padStart(2, "0"), { left: 1160, top: 670, width: 60, height: 30 }, { fontSize: 18, color: "#d6a84f", bold: true, alignment: "right" });
}

function addBullets(slide, bullets, x, y, w) {
  bullets.slice(0, 4).forEach((bullet, i) => {
    const top = y + i * 72;
    addBox(slide, { left: x, top, width: w, height: 52 }, "rgba(255,255,255,.07)", "#27344f");
    addText(slide, bullet, { left: x + 18, top: top + 12, width: w - 36, height: 28 }, { fontSize: 20, color: "#f8fbff", bold: i === 0 });
  });
}

function addArchitecture(slide) {
  const labels = ["Dataset", "Preprocessing", "Feature Engineering", "Model", "Prediction", "Dashboard"];
  labels.forEach((label, i) => {
    const left = 86 + i * 194;
    addBox(slide, { left, top: 360, width: 150, height: 82 }, i % 2 === 0 ? "#172554" : "#312e81", "#38bdf8");
    addText(slide, label, { left: left + 12, top: 386, width: 126, height: 34 }, { fontSize: 18, color: "#ffffff", bold: true, alignment: "center" });
    if (i < labels.length - 1) {
      addText(slide, ">", { left: left + 158, top: 386, width: 32, height: 30 }, { fontSize: 28, color: "#d6a84f", bold: true, alignment: "center" });
    }
  });
}

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

for (let i = 0; i < slidesData.length; i++) {
  const data = slidesData[i];
  const slide = presentation.slides.add();
  slide.background.fill = "#060810";
  slide.speakerNotes.textFrame.setText(data.notes);
  slide.speakerNotes.setVisible(true);

  if (i === 0) {
    await addImage(slide, data.image, { left: 0, top: 0, width: 1280, height: 720 }, "cover");
    slide.shapes.add({
      geometry: "rect",
      position: { left: 0, top: 0, width: 1280, height: 720 },
      fill: "rgba(6,8,16,.72)",
      line: { style: "solid", fill: "none", width: 0 },
    });
    addText(slide, "FINAL CAPSTONE PROJECT", { left: 74, top: 76, width: 480, height: 28 }, { fontSize: 16, color: "#d6a84f", bold: true });
    addText(slide, "Sports Analytics Dashboard\n& Match Outcome Prediction", { left: 74, top: 168, width: 780, height: 220 }, { fontSize: 58, color: "#ffffff", bold: true, typeface: "Aptos Display" });
    addText(slide, data.subtitle, { left: 78, top: 438, width: 620, height: 72 }, { fontSize: 22, color: "#dbeafe" });
    addFooter(slide, i + 1);
    continue;
  }

  addText(slide, data.subtitle.toUpperCase(), { left: 64, top: 46, width: 420, height: 24 }, { fontSize: 14, color: "#d6a84f", bold: true });
  addText(slide, data.title, { left: 64, top: 82, width: 760, height: 98 }, { fontSize: 39, color: "#ffffff", bold: true, typeface: "Aptos Display" });

  if (i === 4) {
    addText(slide, "The system moves from verified data to presentation-ready insight.", { left: 64, top: 202, width: 720, height: 34 }, { fontSize: 22, color: "#a8b3cf" });
    addArchitecture(slide);
    addBullets(slide, data.bullets, 64, 250, 480);
  } else if (i === 5) {
    await addImage(slide, data.image, { left: 650, top: 122, width: 560, height: 360 }, "cover");
    addBullets(slide, data.bullets, 64, 218, 500);
    const sample = JSON.parse(JSON.stringify(["date | home | away | result", "2024-08-16 | Man United | Fulham | Home Win", "2024-08-17 | Arsenal | Wolves | Home Win"]));
    addBox(slide, { left: 650, top: 508, width: 560, height: 96 }, "#0f172a", "#334155");
    addText(slide, sample.join("\n"), { left: 674, top: 528, width: 512, height: 54 }, { fontSize: 16, color: "#dbeafe", typeface: "Aptos Mono" });
  } else if (i === 11) {
    await addImage(slide, data.image, { left: 676, top: 126, width: 520, height: 330 }, "cover");
    addBullets(slide, data.bullets, 64, 218, 520);
    addText(slide, "Evaluation is visible in the app, including feature importance and confusion matrix.", { left: 682, top: 490, width: 500, height: 58 }, { fontSize: 20, color: "#dbeafe" });
  } else {
    await addImage(slide, data.image, { left: 690, top: 118, width: 520, height: 390 }, "cover");
    addBullets(slide, data.bullets, 64, 214, 540);
  }

  addFooter(slide, i + 1);
}

await fs.mkdir(path.join(ROOT, "presentation_assets"), { recursive: true });
for (const [index, slide] of presentation.slides.items.entries()) {
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(ROOT, "presentation_assets", `slide-${String(index + 1).padStart(2, "0")}.png`), Buffer.from(await png.arrayBuffer()));
}
const montage = await presentation.export({ format: "webp", montage: true, scale: 1 });
await fs.writeFile(path.join(ROOT, "presentation_assets", "deck_montage.webp"), Buffer.from(await montage.arrayBuffer()));

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUT);
console.log(OUT);
