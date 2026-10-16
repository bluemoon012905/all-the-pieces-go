const listEl = document.querySelector("#pieceList");
const searchEl = document.querySelector("#pieceSearch");
const archetypeEl = document.querySelector("#archetypeFilter");
const detailEl = document.querySelector("#pieceDetail");
const boardEl = document.querySelector("#previewBoard");

let pieces = [];
let groups = [];
let selected = null;

const dirs = {
  orthogonal: [[1, 0], [-1, 0], [0, 1], [0, -1]],
  diagonal: [[1, 1], [1, -1], [-1, 1], [-1, -1]],
};

function inBounds(x, y) {
  return x >= 0 && x < 9 && y >= 0 && y < 9;
}

function addSteps(target, vectors, origin = [4, 4]) {
  vectors.forEach(([dx, dy]) => {
    const x = origin[0] + dx;
    const y = origin[1] + dy;
    if (inBounds(x, y)) target.add(`${x},${y}`);
  });
}

function addSlides(target, vectors, origin = [4, 4]) {
  vectors.forEach(([dx, dy]) => {
    let x = origin[0] + dx;
    let y = origin[1] + dy;
    while (inBounds(x, y)) {
      target.add(`${x},${y}`);
      x += dx;
      y += dy;
    }
  });
}

function destinations(piece) {
  const target = new Set();
  const allDirs = dirs.orthogonal.concat(dirs.diagonal);
  switch (piece.preview) {
    case "king": addSteps(target, allDirs); break;
    case "queen": addSlides(target, allDirs); break;
    case "rook": addSlides(target, dirs.orthogonal); break;
    case "bishop": addSlides(target, dirs.diagonal); break;
    case "knight":
      addSteps(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]);
      break;
    case "xiangqi_knight":
      addSteps(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]);
      break;
    case "xiangqi_elephant": addSteps(target, [[2, 2], [2, -2], [-2, 2], [-2, -2]]); break;
    case "xiangqi_king": addSteps(target, dirs.orthogonal); break;
    case "janggi_elephant": addSteps(target, [[3, 2], [3, -2], [-3, 2], [-3, -2], [2, 3], [2, -3], [-2, 3], [-2, -3]]); break;
    case "ferz": addSteps(target, dirs.diagonal); break;
    case "wazir": addSteps(target, dirs.orthogonal); break;
    case "alfil": addSteps(target, [[2, 2], [2, -2], [-2, 2], [-2, -2]]); break;
    case "dabbaba": addSteps(target, [[2, 0], [-2, 0], [0, 2], [0, -2]]); break;
    case "shogi_knight": addSteps(target, [[-1, 2], [1, 2]]); break;
    case "lance": addSlides(target, [[0, 1]]); break;
    // A chess pawn's forward move and diagonal captures are rendered
    // separately below. Keep the geometry here broad enough for the chess
    // case; shogi's pawn is forward-only and is handled explicitly there.
    case "pawn":
      addSteps(target, piece.game === "Shogi" ? [[0, 1]] : [[0, 1], [-1, 1], [1, 1]]);
      break;
    case "xiangqi_soldier": addSteps(target, [[0, 1]]); break;
    case "centaur": addSteps(target, allDirs.concat([[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]])); break;
    case "archbishop": addSlides(target, dirs.diagonal); addSteps(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]); break;
    case "khon": addSteps(target, dirs.diagonal.concat([[0, 1]])); break;
    case "silver": addSteps(target, [[0, 1], [-1, 1], [1, 1], [-1, -1], [1, -1]]); break;
    case "gold": addSteps(target, [[0, 1], [-1, 1], [1, 1], [-1, 0], [1, 0], [0, -1]]); break;
    case "ferocious_leopard": addSteps(target, dirs.diagonal.concat([[0, 1], [0, -1]])); break;
    case "drunk_elephant": addSteps(target, allDirs.filter(([dx, dy]) => !(dx === 0 && dy === -1))); break;
    case "blind_tiger": addSteps(target, allDirs.filter(([dx, dy]) => !(dx === 0 && dy === 1))); break;
    case "berolina_pawn": addSteps(target, [[-1, 1], [0, 1], [1, 1]]); break;
    case "reverse_chariot": addSlides(target, [[0, 1], [0, -1]]); break;
    case "vertical_mover": addSlides(target, [[0, 1], [0, -1]]); addSteps(target, [[1, 0], [-1, 0]]); break;
    case "side_mover": addSlides(target, [[1, 0], [-1, 0]]); addSteps(target, [[0, 1], [0, -1]]); break;
    case "flying_ox": addSlides(target, [[0, 1], [0, -1]].concat(dirs.diagonal)); break;
    case "free_boar": addSlides(target, [[1, 0], [-1, 0]].concat(dirs.diagonal)); break;
    case "whale": addSlides(target, [[0, 1], [0, -1], [-1, -1], [1, -1]]); break;
    case "white_horse": addSlides(target, [[0, 1], [0, -1], [-1, 1], [1, 1]]); break;
    case "camel": addSteps(target, [[3, 1], [3, -1], [-3, 1], [-3, -1], [1, 3], [1, -3], [-1, 3], [-1, -3]]); break;
    case "zebra": addSteps(target, [[3, 2], [3, -2], [-3, 2], [-3, -2], [2, 3], [2, -3], [-2, 3], [-2, -3]]); break;
    case "giraffe": addSteps(target, [[4, 1], [4, -1], [-4, 1], [-4, -1], [1, 4], [1, -4], [-1, 4], [-1, -4]]); break;
    case "nightrider": addSlides(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]); break;
    case "wildebeest": addSteps(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2], [3, 1], [3, -1], [-3, 1], [-3, -1], [1, 3], [1, -3], [-1, 3], [-1, -3]]); break;
    case "okapi": addSteps(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2], [3, 2], [3, -2], [-3, 2], [-3, -2], [2, 3], [2, -3], [-2, 3], [-2, -3]]); break;
    case "champion": addSteps(target, dirs.orthogonal.concat([[2, 0], [-2, 0], [0, 2], [0, -2], [2, 2], [2, -2], [-2, 2], [-2, -2]])); break;
    case "chancellor": addSlides(target, dirs.orthogonal); addSteps(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]); break;
    case "grasshopper": addSteps(target, allDirs); break;
    case "fire_demon": addSlides(target, allDirs); break;
    case "water_buffalo": addSlides(target, [[1, 0], [-1, 0]].concat(dirs.diagonal)); break;
    case "wizard": addSteps(target, dirs.diagonal.concat([[3, 1], [3, -1], [-3, 1], [-3, -1], [1, 3], [1, -3], [-1, 3], [-1, -3]])); break;
    case "cannon": addSlides(target, dirs.orthogonal); break;
    case "lion": addSteps(target, allDirs.concat([[0, 2], [0, -2], [2, 0], [-2, 0], [2, 2], [2, -2], [-2, 2], [-2, -2]])); break;
    case "dragon_horse": addSlides(target, dirs.diagonal); addSteps(target, dirs.orthogonal); break;
    case "dragon_king": addSlides(target, dirs.orthogonal); addSteps(target, dirs.diagonal); break;
    case "phoenix": addSteps(target, dirs.orthogonal.concat([[2, 2], [2, -2], [-2, 2], [-2, -2]])); break;
    case "kirin": addSteps(target, dirs.diagonal.concat([[2, 0], [-2, 0], [0, 2], [0, -2]])); break;
    case "amazon": addSlides(target, allDirs); addSteps(target, [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]); break;
    default: addSlides(target, allDirs); break;
  }
  return target;
}

function assetUrl(piece) {
  if (piece.assetFamily === "lichess") return `/assets/pieces/lichess/chessnut/w${piece.assetName}.svg`;
  if (piece.assetFamily === "lishogi") {
    const aliases = { OU: "KI" };
    return `/assets/pieces/lishogi/intl_colored_2d/0${aliases[piece.assetName] || piece.assetName}.svg`;
  }
  if (piece.assetFamily === "xiangqi") return `/assets/pieces/xiangqi/trad/${piece.assetName}.svg`;
  return null;
}

function groupKey(piece) {
  // Keep base and promoted forms, and pieces with different promotion rules,
  // distinct even when their raw movement text matches.
  return [piece.movement, piece.promotion].join("|");
}

function buildGroups() {
  const grouped = new Map();
  pieces.forEach((piece) => {
    const key = groupKey(piece);
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(piece);
  });
  groups = [...grouped.values()].map((members) => ({
    members,
    representative: members[0],
  }));
}

function createPreviewPiece(piece) {
  if (piece.assetFamily === "xiangqi") {
    const sprite = document.createElement("span");
    sprite.className = "preview-piece xiangqi-preview";
    sprite.style.backgroundImage = `url("${assetUrl(piece)}")`;
    return sprite;
  }
  if (!assetUrl(piece)) {
    const fallback = document.createElement("span");
    fallback.className = "preview-piece preview-glyph";
    fallback.textContent = piece.glyph;
    return fallback;
  }
  const image = document.createElement("img");
  image.className = "preview-piece";
  image.src = assetUrl(piece) || "";
  image.alt = `${piece.name} at origin`;
  image.addEventListener("error", () => image.replaceWith(document.createTextNode(piece.glyph)));
  return image;
}

function createCatalogVisual(piece) {
  const source = assetUrl(piece);
  if (piece.assetFamily === "xiangqi") {
    const sprite = document.createElement("span");
    sprite.className = "catalog-piece xiangqi-preview";
    sprite.style.backgroundImage = `url("${source}")`;
    return sprite;
  }
  if (source) {
    const image = document.createElement("img");
    image.className = "catalog-piece";
    image.src = source;
    image.alt = "";
    image.addEventListener("error", () => image.replaceWith(document.createTextNode(piece.glyph)));
    return image;
  }
  const fallback = document.createElement("span");
  fallback.className = "catalog-piece catalog-glyph-fallback";
  fallback.textContent = piece.glyph;
  return fallback;
}

function captureDestination(piece) {
  const candidates = [...destinations(piece)];
  if (piece.preview === "pawn" && piece.game === "Chess") {
    return candidates.find((coord) => coord.split(",")[0] !== "4") || candidates[0];
  }
  return candidates[0];
}

function captureDestinations(piece) {
  if (piece.preview === "pawn" && piece.game === "Chess") {
    return new Set(["3,5", "5,5"]);
  }
  if (hasSpecialCaptureExample(piece)) return new Set([captureDestination(piece)]);
  return new Set();
}

function hasSpecialCaptureExample(piece) {
  const ruleText = `${piece.movement} ${piece.special}`.toLowerCase();
  return /capture|captur|sandwich|screen|burns adjacent|freezes adjacent|igui|jumping/.test(ruleText);
}

function previewExample(piece) {
  const state = {
    destinations: destinations(piece),
    blockedDestinations: new Set(),
    blockers: new Set(),
    screens: new Set(),
    captureTargets: new Set(),
  };

  if (piece.preview === "cannon") {
    // Xiangqi Pao: quiet movement stops at the screen; a capture lands
    // exactly one square beyond it. This mirrors pieces/xiangqi.py.
    state.destinations = new Set([
      "0,4", "1,4", "2,4", "3,4", "5,4",
      "4,0", "4,1", "4,2", "4,3", "4,5", "4,6", "4,7", "4,8",
    ]);
    state.screens.add("6,4");
    state.captureTargets.add("7,4");
    return state;
  }

  if (piece.preview === "xiangqi_knight") {
    // Block the north leg. Both destinations using that leg are illegal.
    state.blockers.add("4,5");
    state.blockedDestinations.add("5,6");
    state.blockedDestinations.add("3,6");
  }

  state.captureTargets = captureDestinations(piece);
  state.captureTargets.forEach((coord) => {
    if (state.blockedDestinations.has(coord)) state.captureTargets.delete(coord);
  });
  return state;
}

function createDummy(className, alt) {
  const dummy = document.createElement("img");
  dummy.className = className;
  dummy.src = "/assets/pieces/lichess/chessnut/bP.svg";
  dummy.alt = alt;
  return dummy;
}

function buildPreviewBoard() {
  boardEl.replaceChildren();
  const example = selected ? previewExample(selected) : null;
  for (let y = 8; y >= 0; y -= 1) {
    for (let x = 0; x < 9; x += 1) {
      const square = document.createElement("div");
      square.className = `preview-square ${(x + y) % 2 === 0 ? "light" : "dark"}`;
      square.dataset.coord = `${x},${y}`;
      if (x === 4 && y === 4) {
        square.classList.add("origin");
        if (selected) square.append(createPreviewPiece(selected));
      }
      const coord = `${x},${y}`;
      if (example?.destinations.has(coord) && !example.captureTargets.has(coord) && !example.blockedDestinations.has(coord)) {
        square.classList.add("possible");
      }
      if (example?.blockedDestinations.has(coord)) square.classList.add("blocked");
      if (example?.blockers.has(coord)) {
        square.classList.add("blocker");
        square.append(createDummy("piece-obstacle", "Blocking piece"));
      }
      if (example?.screens.has(coord)) {
        square.classList.add("screen");
        square.append(createDummy("screen-piece", "Cannon screen"));
      }
      if (example?.captureTargets.has(coord)) {
        square.classList.add("capture-target");
        square.append(createDummy("capture-piece", "Dummy opposing piece that can be captured"));
      }
      boardEl.append(square);
    }
  }
}

function renderDetail(piece) {
  const group = groups.find((item) => item.members.some((member) => member.slug === piece.slug));
  const related = group?.members.map((member) => `${member.name} (${member.game})`).join(", ");
  detailEl.innerHTML = `
    <p class="eyebrow">${piece.archetype}</p>
    <h2>${piece.name}</h2>
    <p class="piece-origin">${piece.game}</p>
    ${group && group.members.length > 1 ? `<p class="piece-group"><strong>Shared behavior:</strong> ${related}</p>` : ""}
    <dl>
      <div><dt>Movement</dt><dd>${piece.movement}</dd></div>
      <div><dt>Promotion</dt><dd>${piece.promotion}</dd></div>
      <div><dt>Special rule</dt><dd>${piece.special}</dd></div>
    </dl>
  `;
}

function renderList() {
  const query = searchEl.value.trim().toLowerCase();
  const archetype = archetypeEl.value;
  const filtered = groups.filter((group) => {
    const haystack = group.members.map((piece) => `${piece.name} ${piece.game} ${piece.archetype} ${piece.movement}`).join(" ").toLowerCase();
    return haystack.includes(query) && (!archetype || group.members.some((piece) => piece.archetype === archetype));
  });
  listEl.replaceChildren(...filtered.map((group) => {
    const piece = group.representative;
    const card = document.createElement("button");
    card.type = "button";
    card.className = `piece-card${group.members.some((member) => selected?.slug === member.slug) ? " selected" : ""}`;
    const visual = document.createElement("span");
    visual.className = "catalog-glyph";
    visual.replaceChildren(createCatalogVisual(piece));
    const text = document.createElement("span");
    const names = group.members.map((member) => member.name).join(" · ");
    text.innerHTML = `<strong>${names}</strong><small>${group.members.length} shared movement${group.members.length === 1 ? "" : "s"}</small>`;
    card.append(visual, text);
    card.addEventListener("click", () => {
      selected = piece;
      renderDetail(piece);
      renderList();
      buildPreviewBoard();
    });
    return card;
  }));
}

async function init() {
  const response = await fetch("/api/pieces");
  pieces = (await response.json()).pieces;
  buildGroups();
  [...new Set(pieces.map((piece) => piece.archetype))].sort().forEach((archetype) => {
    const option = document.createElement("option");
    option.value = archetype;
    option.textContent = archetype;
    archetypeEl.append(option);
  });
  searchEl.addEventListener("input", renderList);
  archetypeEl.addEventListener("change", renderList);
  renderList();
  buildPreviewBoard();
}

init();
