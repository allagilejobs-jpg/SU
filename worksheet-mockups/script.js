const worksheets = [
  {
    title: "Name Tracing Practice",
    category: "Name Tracing",
    type: "Generator",
    preview: "name",
    summary: "A custom name worksheet with dotted trace rows and blank copy space.",
    inputs: "Student name, font, repeat count, font color, page orientation.",
    output: "Printable tracing worksheet with preview and download."
  },
  {
    title: "Name Tracing Pack",
    category: "Name Tracing",
    type: "Generator",
    preview: "namePack",
    summary: "A multi-page name practice set using the same student name in several layouts.",
    inputs: "Student name, font style, line count, practice style.",
    output: "A small printable packet for repeated handwriting practice."
  },
  {
    title: "Cursive Name Tracing",
    category: "Name Tracing",
    type: "Generator",
    preview: "cursive",
    summary: "A cursive version of the name tracing page for older handwriting practice.",
    inputs: "Student name, cursive font, repeat count, color, orientation.",
    output: "Cursive dotted-name worksheet."
  },
  {
    title: "Holiday Name Tracing",
    category: "Name Tracing",
    type: "Generator",
    preview: "holiday",
    summary: "A themed name tracing worksheet with holiday visuals and repeated writing lines.",
    inputs: "Student name, holiday theme, font, repeat count.",
    output: "Seasonal printable name practice page."
  },
  {
    title: "Seasonal Name Tracing",
    category: "Name Tracing",
    type: "Generator",
    preview: "seasonal",
    summary: "A name tracing page themed around spring, summer, fall, or winter.",
    inputs: "Student name, season, font, font color, orientation.",
    output: "Seasonal handwriting practice sheet."
  },
  {
    title: "Name and Picture Practice",
    category: "Name Tracing",
    type: "Generator",
    preview: "namePicture",
    summary: "A page that pairs the child name with a picture-style name display.",
    inputs: "Child name, font, font color, picture/font-image option.",
    output: "Name recognition and name writing worksheet."
  },
  {
    title: "Name Playdough Mat",
    category: "Fine Motor",
    type: "Worksheet",
    preview: "playdough",
    summary: "A fine-motor mat where the student forms their name with dough.",
    inputs: "Student name and style options.",
    output: "Printable name-forming playdough mat."
  },
  {
    title: "Editable Name Collage Activity",
    category: "Name Tracing",
    type: "Blog Variant",
    preview: "collage",
    summary: "A name activity concept where students build or decorate their name.",
    inputs: "Student name and activity style.",
    output: "Name collage activity sheet."
  },
  {
    title: "Rainbow Name Tracing",
    category: "Name Tracing",
    type: "Blog Variant",
    preview: "rainbowName",
    summary: "A color-layer name practice variation for repeated tracing.",
    inputs: "Student name, tracing style, colors.",
    output: "Rainbow-themed name tracing page."
  },
  {
    title: "Paint Name Tracing",
    category: "Name Tracing",
    type: "Blog Variant",
    preview: "paint",
    summary: "An alternative name tracing activity styled around paint practice.",
    inputs: "Student name, font, activity theme.",
    output: "Paint-themed name practice worksheet."
  },
  {
    title: "Sticker Name Outline",
    category: "Name Tracing",
    type: "Blog Variant",
    preview: "sticker",
    summary: "A name outline worksheet where students place stickers or trace the name.",
    inputs: "Student name and outline style.",
    output: "Name outline activity printable."
  },
  {
    title: "Word Tracing Practice",
    category: "Word Tracing",
    type: "Generator",
    preview: "word",
    summary: "A custom worksheet for tracing teacher-provided words.",
    inputs: "Word list, font, font color, page orientation.",
    output: "Printable word tracing worksheet."
  },
  {
    title: "A-Z Letter Formation",
    category: "Letters",
    type: "Worksheet",
    preview: "letter",
    summary: "An alphabet formation worksheet for preschool and kindergarten.",
    inputs: "Preset A-Z layout with font/download options.",
    output: "Full alphabet tracing worksheet."
  },
  {
    title: "Letter Tracing With Images",
    category: "Letters",
    type: "Worksheet",
    preview: "letterImages",
    summary: "Letter tracing paired with phonetic picture prompts.",
    inputs: "Preset letter set and image-based alphabet layout.",
    output: "Letter tracing worksheet with picture cues."
  },
  {
    title: "Seasonal Letter Tracing",
    category: "Letters",
    type: "Worksheet",
    preview: "seasonLetter",
    summary: "Letter tracing pages with seasonal styling.",
    inputs: "Season/theme and alphabet worksheet style.",
    output: "Seasonal letter tracing printable."
  },
  {
    title: "Bubble A-Z Tracing",
    category: "Letters",
    type: "Worksheet",
    preview: "bubble",
    summary: "A bubble-letter alphabet worksheet for tracing and coloring.",
    inputs: "Preset A-Z bubble letter layout.",
    output: "Bubble alphabet tracing worksheet."
  },
  {
    title: "Alphabet Letter Chart",
    category: "Letters",
    type: "Worksheet",
    preview: "chart",
    summary: "A printable alphabet chart with letter recognition support.",
    inputs: "Preset chart layout.",
    output: "Alphabet reference chart."
  },
  {
    title: "Days of the Week Tracing",
    category: "Word Tracing",
    type: "Worksheet",
    preview: "days",
    summary: "Tracing practice for weekday vocabulary.",
    inputs: "Preset days of week words and layout.",
    output: "Calendar word tracing worksheet."
  },
  {
    title: "Numbers Tracing 1-20",
    category: "Numbers",
    type: "Worksheet",
    preview: "number",
    summary: "A number tracing worksheet for early numeracy.",
    inputs: "Font choice for dotted and lined numbers.",
    output: "Printable number tracing worksheet."
  },
  {
    title: "1-100 Number Tracing Pack",
    category: "Numbers",
    type: "Worksheet Pack",
    preview: "numberPack",
    summary: "A larger number tracing packet covering numbers 1 through 100.",
    inputs: "Preset number range and style options.",
    output: "Multi-page number tracing pack."
  },
  {
    title: "Address and Phone Number Tracing",
    category: "Life Skills",
    type: "Generator",
    preview: "address",
    summary: "A functional tracing worksheet for personal information.",
    inputs: "Phone number and address.",
    output: "Personal info tracing worksheet."
  },
  {
    title: "I Know My Colors",
    category: "Colors",
    type: "Worksheet",
    preview: "colors",
    summary: "A color recognition worksheet with a simple coloring-page layout.",
    inputs: "Preset color page.",
    output: "Printable color recognition worksheet."
  },
  {
    title: "Editable Diploma Certificate",
    category: "Certificates",
    type: "Generator",
    preview: "certificate",
    summary: "A customizable certificate or diploma printable.",
    inputs: "Background, wording, child name, school, date, teacher name.",
    output: "Editable diploma or certificate."
  },
  {
    title: "Graduation Day Memories",
    category: "Certificates",
    type: "Worksheet",
    preview: "graduation",
    summary: "A memory certificate style page for graduation milestones.",
    inputs: "Student details, school year, celebration wording.",
    output: "Graduation memory printable."
  },
  {
    title: "Rainbow Chore Chart",
    category: "Chores",
    type: "Generator",
    preview: "chores",
    summary: "A customizable home routine chart with chore rows.",
    inputs: "Background, chart title, child name, chore lines, colors.",
    output: "Printable rainbow chore chart."
  }
];

const gallery = document.querySelector("#gallery");
const filters = document.querySelector("#filters");
const searchInput = document.querySelector("#searchInput");
const cardTemplate = document.querySelector("#cardTemplate");
const visibleCount = document.querySelector("#visibleCount");
const totalCount = document.querySelector("#totalCount");

let activeCategory = "All";

function categories() {
  return ["All", ...Array.from(new Set(worksheets.map((item) => item.category)))];
}

function createFilters() {
  filters.innerHTML = "";
  categories().forEach((category) => {
    const button = document.createElement("button");
    button.className = "filterBtn";
    button.type = "button";
    button.textContent = category;
    button.dataset.category = category;
    button.addEventListener("click", () => {
      activeCategory = category;
      document.querySelectorAll(".filterBtn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.category === category);
      });
      render();
    });
    if (category === activeCategory) button.classList.add("active");
    filters.appendChild(button);
  });
}

function dots(count) {
  return `<div class="dots">${Array.from({ length: count }, () => "<span></span>").join("")}</div>`;
}

function previewMarkup(kind, title) {
  const head = `<div class="sheetHead"><div class="sheetTitle">${title}</div><div class="sheetName"></div></div>`;
  const trace = (word, count = 5) => Array.from({ length: count }, (_, index) => {
    const cls = index > 2 ? "traceLine faded" : "traceLine";
    return `<div class="${cls}">${word}</div>`;
  }).join("");

  const simpleTrace = (label, word) => `
    <div class="worksheet">
      ${head}
      <div class="sheetBody">${trace(word, 6)}</div>
    </div>`;

  const map = {
    name: simpleTrace(title, "Maya"),
    namePack: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          ${trace("Maya", 3)}
          <div class="matchGrid"><div class="matchBox"></div><div class="matchBox"></div><div class="matchBox"></div><div class="matchBox"></div></div>
        </div>
      </div>`,
    cursive: simpleTrace(title, "Maya"),
    holiday: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="pic">★</div>
          ${trace("Maya", 4)}
        </div>
      </div>`,
    seasonal: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="shapeGrid"><div class="pic">☀</div><div class="pic">❄</div></div>
          ${trace("Maya", 4)}
        </div>
      </div>`,
    namePicture: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="pic">M</div>
          ${trace("Maya", 4)}
        </div>
      </div>`,
    playdough: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="bigLetter">M</div>
          <div class="traceLine">Maya</div>
          <div class="shapeGrid"><div class="shapeBox"></div><div class="shapeBox"></div><div class="shapeBox"></div><div class="shapeBox"></div></div>
        </div>
      </div>`,
    collage: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="cardGrid"><div class="smallCard"></div><div class="smallCard"></div><div class="smallCard"></div><div class="smallCard"></div></div>
          ${trace("Maya", 3)}
        </div>
      </div>`,
    rainbowName: `
      <div class="worksheet">
        ${head}
        <div class="rainbow"></div>
        <div class="sheetBody">${trace("Maya", 5)}</div>
      </div>`,
    paint: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="pictureChoices"><div class="pic">●</div><div class="pic">●</div><div class="pic">●</div></div>
          ${trace("Maya", 4)}
        </div>
      </div>`,
    sticker: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="traceLine faded">Maya</div>
          <div class="pictureChoices"><div class="pic">•</div><div class="pic">•</div><div class="pic">•</div></div>
          ${trace("Maya", 3)}
        </div>
      </div>`,
    word: simpleTrace(title, "school"),
    letter: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="bigLetter">A</div>
          ${trace("A a", 4)}
        </div>
      </div>`,
    letterImages: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="bigLetter">A</div>
          <div class="pictureChoices"><div class="pic">🍎</div><div class="pic">✈</div><div class="pic">🐜</div></div>
          ${trace("A a", 3)}
        </div>
      </div>`,
    seasonLetter: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="pic">☂</div>
          <div class="bigLetter">S</div>
          ${trace("S s", 3)}
        </div>
      </div>`,
    bubble: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="bigLetter">ABC</div>
          <div class="shapeGrid"><div class="shapeBox"></div><div class="shapeBox"></div><div class="shapeBox"></div><div class="shapeBox"></div></div>
        </div>
      </div>`,
    chart: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="cardGrid">${"ABCDEFGHIJKLMNOPQRSTUVWXYZ".slice(0, 12).split("").map((l) => `<div class="tile">${l}</div>`).join("")}</div>
        </div>
      </div>`,
    days: simpleTrace(title, "Monday"),
    number: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="bigNumber">5</div>
          ${trace("5 5 5", 4)}
        </div>
      </div>`,
    numberPack: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="numberGrid">
            <div class="numberBox">1 ${dots(1)}</div>
            <div class="numberBox">2 ${dots(2)}</div>
            <div class="numberBox">3 ${dots(3)}</div>
            <div class="numberBox">4 ${dots(4)}</div>
          </div>
          ${trace("1 2 3 4", 3)}
        </div>
      </div>`,
    address: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          ${trace("555-1234", 3)}
          ${trace("123 Main St", 3)}
        </div>
      </div>`,
    colors: `
      <div class="worksheet">
        ${head}
        <div class="sheetBody">
          <div class="shapeGrid"><div class="shapeBox"></div><div class="shapeBox"></div><div class="shapeBox"></div><div class="shapeBox"></div></div>
          <div class="cutStrip"><div class="tile">red</div><div class="tile">blue</div><div class="tile">green</div><div class="tile">yellow</div></div>
        </div>
      </div>`,
    certificate: `
      <div class="worksheet certificate">
        <div class="crest"></div>
        <h3>Certificate</h3>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
      </div>`,
    graduation: `
      <div class="worksheet certificate">
        <div class="crest"></div>
        <h3>Graduation</h3>
        <div class="line"></div>
        <div class="pictureChoices"><div class="pic">★</div><div class="pic">✓</div><div class="pic">1</div></div>
      </div>`,
    chores: `
      <div class="worksheet">
        ${head}
        <div class="rainbow"></div>
        <div class="sheetBody choreRows">
          ${Array.from({ length: 7 }, () => `<div class="choreRow"><div class="check"></div><div class="bar"></div><div class="day"></div><div class="day"></div><div class="day"></div><div class="day"></div><div class="day"></div></div>`).join("")}
        </div>
      </div>`
  };

  return map[kind] || simpleTrace(title, "trace");
}

function render() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = worksheets.filter((item) => {
    const matchesCategory = activeCategory === "All" || item.category === activeCategory;
    const haystack = `${item.title} ${item.category} ${item.type} ${item.summary}`.toLowerCase();
    return matchesCategory && haystack.includes(query);
  });

  gallery.innerHTML = "";
  if (!filtered.length) {
    gallery.innerHTML = `<div class="empty">No mockups match this filter.</div>`;
  }

  filtered.forEach((item) => {
    const node = cardTemplate.content.cloneNode(true);
    node.querySelector(".previewShell").innerHTML = previewMarkup(item.preview, item.title);
    node.querySelector(".category").textContent = item.category;
    node.querySelector(".type").textContent = item.type;
    node.querySelector("h2").textContent = item.title;
    node.querySelector(".summary").textContent = item.summary;
    node.querySelector(".inputs").textContent = item.inputs;
    node.querySelector(".output").textContent = item.output;
    gallery.appendChild(node);
  });

  visibleCount.textContent = filtered.length;
  totalCount.textContent = worksheets.length;
}

searchInput.addEventListener("input", render);
createFilters();
render();
