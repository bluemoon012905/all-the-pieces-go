const boardEl = document.querySelector("#board");
const activePlayerEl = document.querySelector("#activePlayer");
const movesLeftEl = document.querySelector("#movesLeft");
const turnNumberEl = document.querySelector("#turnNumber");
const actionCountEl = document.querySelector("#actionCount");
const lastActionEl = document.querySelector("#lastAction");
const moveLogEl = document.querySelector("#moveLog");
const resetButton = document.querySelector("#resetButton");
const stepButton = document.querySelector("#stepButton");
const autoButton = document.querySelector("#autoButton");
const modeSelect = document.querySelector("#modeSelect");
const variantPicker = document.querySelector(".variant-picker");
const variantSelect = document.querySelector("#variantSelect");
const modeStatusEl = document.querySelector("#modeStatus");
const modeTitleEl = document.querySelector("#modeTitle");
const homePage = document.querySelector("#homePage");
const gamePage = document.querySelector("#gamePage");
const modeCardsEl = document.querySelector("#modeCards");
const roguePage = document.querySelector("#roguePage");
const roguePlayPage = document.querySelector("#roguePlayPage");

let autoTimer = null;
let seenActions = new Set();
let missingAssets = new Set();

const ROGUE_STORAGE_KEY = "all-the-pieces-go:rogue-wave-design";
const ROGUE_CHARACTERS = [
  { id: "chess", name: "Chess", detail: "Classic pieces and clean lines", glyph: "♔" },
  { id: "shogi", name: "Shogi", detail: "Promotion and forward pressure", glyph: "王" },
  { id: "xiangqi", name: "Xiangqi", detail: "Palace tactics and screens", glyph: "帥" },
];

let roguePieces = [];
let rogueState = null;
let rogueSelectedTool = null;
let roguePlayState = null;
let rogueSelectedFrom = null;
let roguePendingShopKey = null;
let roguePendingBankIndex = null;
let rogueAnimationToken = 0;

function assetFor(piece) {
  if (piece.assetFamily === "lichess") {
    const colorPrefix = piece.color === "white" ? "w" : "b";
    return {
      type: "image",
      src: `/assets/pieces/lichess/chessnut/${colorPrefix}${piece.assetName}.svg`,
    };
  }
  if (piece.assetFamily === "lishogi") {
    const colorPrefix = piece.color === "white" ? "0" : "1";
    return {
      type: "image",
      src: `/assets/pieces/lishogi/intl_colored_2d/${colorPrefix}${piece.assetName}.svg`,
    };
  }
  if (piece.assetFamily === "xiangqi") {
    return {
      type: "sprite",
      src: `/assets/pieces/xiangqi/trad/${piece.assetName}.svg`,
      side: piece.color === "white" ? "red-side" : "black-side",
    };
  }
  return { type: "letter" };
}

function facesAwayFromBlackSide(piece) {
  return piece.assetFamily === "lishogi" && piece.color === "black" && piece.assetName === "FU";
}

function buildBoard() {
  boardEl.innerHTML = "";
  for (let y = 8; y >= 0; y -= 1) {
    for (let x = 0; x < 9; x += 1) {
      const square = document.createElement("div");
      square.className = `square ${(x + y) % 2 === 0 ? "light" : "dark"}`;
      square.dataset.x = x;
      square.dataset.y = y;
      square.setAttribute("role", "gridcell");
      if (x >= 3 && x <= 5 && (y <= 2 || y >= 6)) {
        square.classList.add("palace");
      }
      boardEl.append(square);
    }
  }
}

function squareFor(piece) {
  return boardEl.querySelector(`[data-x="${piece.x}"][data-y="${piece.y}"]`);
}

function renderState(state) {
  modeTitleEl.textContent = state.modeName;
  modeSelect.value = state.mode;
  modeStatusEl.textContent = state.modeStatus.replace("_", " ");
  variantPicker.hidden = state.mode !== "pvp";
  if (state.mode === "pvp") variantSelect.value = state.variant;
  activePlayerEl.textContent = state.winner ? `${state.winner} wins` : state.activePlayer;
  movesLeftEl.textContent = state.movesLeft;
  turnNumberEl.textContent = state.turn;
  actionCountEl.textContent = state.actionCount;
  stepButton.disabled = state.phase === "game_over";
  const botMode = state.mode === "bot_maker";
  stepButton.disabled = stepButton.disabled || !botMode;
  autoButton.disabled = !botMode;
  if (state.phase === "game_over") {
    stopAuto();
  }

  document.querySelectorAll(".piece").forEach((piece) => piece.remove());
  state.pieces.forEach((piece) => {
    const square = squareFor(piece);
    if (!square) return;
    const pieceEl = document.createElement("div");
    const asset = assetFor(piece);
    pieceEl.className = `piece ${piece.color} ${piece.assetFamily}${piece.promoted ? " promoted" : ""}${facesAwayFromBlackSide(piece) ? " faces-away" : ""}`;
    pieceEl.title = `${piece.color} ${piece.name} (${piece.x}, ${piece.y})`;
    pieceEl.setAttribute("aria-label", pieceEl.title);
    pieceEl.dataset.fallback = piece.code;

    if (asset.type === "image") {
      if (missingAssets.has(asset.src)) {
        renderFallback(pieceEl, piece);
        square.append(pieceEl);
        return;
      }
      const image = document.createElement("img");
      image.src = asset.src;
      image.alt = "";
      image.loading = "eager";
      image.addEventListener("error", () => {
        missingAssets.add(asset.src);
        renderFallback(pieceEl, piece);
      });
      pieceEl.append(image);
    } else if (asset.type === "sprite") {
      if (missingAssets.has(asset.src)) {
        renderFallback(pieceEl, piece);
        square.append(pieceEl);
        return;
      }
      pieceEl.style.setProperty("--piece-image", `url("${asset.src}")`);
      pieceEl.classList.add("sprite", asset.side);
      const probe = new Image();
      probe.addEventListener("error", () => {
        missingAssets.add(asset.src);
        renderFallback(pieceEl, piece);
      });
      probe.src = asset.src;
    } else {
      renderFallback(pieceEl, piece);
    }
    square.append(pieceEl);
  });

  if (state.lastAction) {
    const action = state.lastAction;
    const captured = action.captured ? `, captured ${action.captured}` : "";
    const winner = action.winner ? ` — ${action.winner} wins` : "";
    const text = `${action.piece}: (${action.from[0]}, ${action.from[1]}) to (${action.to[0]}, ${action.to[1]})${captured}${winner}`;
    lastActionEl.textContent = text;
    if (!seenActions.has(action.number)) {
      seenActions.add(action.number);
      const item = document.createElement("li");
      item.textContent = text;
      moveLogEl.prepend(item);
    }
  } else {
    lastActionEl.textContent = "No actions yet.";
    moveLogEl.innerHTML = "";
    seenActions = new Set();
  }
}

function renderFallback(pieceEl, piece) {
  pieceEl.style.removeProperty("--piece-image");
  pieceEl.replaceChildren();
  pieceEl.textContent = piece.code;
  pieceEl.classList.remove("sprite", "red-side", "black-side");
  pieceEl.classList.add("fallback");
}

function makeRogueState() {
  return {
    selectedCharacter: "chess",
    activeWaveId: 1,
    nextWaveId: 2,
    waves: [{ id: 1, name: "Wave 1", reward: "", note: "", pieces: [] }],
  };
}

function loadRogueState() {
  try {
    const saved = JSON.parse(localStorage.getItem(ROGUE_STORAGE_KEY) || "null");
    if (saved && Array.isArray(saved.waves) && saved.waves.length) return saved;
  } catch (error) {
    // A malformed local draft should not prevent the editor from opening.
  }
  return makeRogueState();
}

function saveRogueState() {
  localStorage.setItem(ROGUE_STORAGE_KEY, JSON.stringify(rogueState));
  const saveState = document.querySelector("#rogueSaveState");
  saveState.textContent = "Saved automatically · just now";
  window.clearTimeout(saveRogueState.timer);
  saveRogueState.timer = window.setTimeout(() => {
    saveState.textContent = "Saved automatically";
  }, 1800);
}

function activeRogueWave() {
  return rogueState.waves.find((wave) => wave.id === rogueState.activeWaveId) || rogueState.waves[0];
}

function updateRogueState(mutator) {
  mutator();
  saveRogueState();
  renderRogueEditor();
}

function renderCharacterChoices() {
  const choices = document.querySelector("#characterChoices");
  choices.replaceChildren(...ROGUE_CHARACTERS.map((character) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `character-choice${rogueState.selectedCharacter === character.id ? " selected" : ""}`;
    button.setAttribute("role", "radio");
    button.setAttribute("aria-checked", rogueState.selectedCharacter === character.id);
    button.innerHTML = `<span class="character-glyph">${character.glyph}</span><span><strong>${character.name}</strong><small>${character.detail}</small></span>`;
    button.addEventListener("click", () => updateRogueState(() => {
      rogueState.selectedCharacter = character.id;
    }));
    return button;
  }));
}

function renderWaveTabs() {
  const tabs = document.querySelector("#waveTabs");
  tabs.replaceChildren(...rogueState.waves.map((wave, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `wave-tab${wave.id === rogueState.activeWaveId ? " selected" : ""}`;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", wave.id === rogueState.activeWaveId);
    button.innerHTML = `<strong>${index + 1}</strong><span>${wave.name || `Wave ${index + 1}`}</span><small>${wave.pieces.length} pieces</small>`;
    button.addEventListener("click", () => updateRogueState(() => {
      rogueState.activeWaveId = wave.id;
    }));
    return button;
  }));
}

function roguePalettePiece(piece) {
  return {
    slug: piece.slug,
    name: piece.name,
    game: piece.game,
    code: piece.assetName || piece.glyph,
    symbol: piece.glyph,
    color: "black",
    promoted: false,
    assetFamily: piece.assetFamily,
    assetName: piece.assetName,
  };
}

function renderRoguePiecePalette() {
  const palette = document.querySelector("#roguePiecePalette");
  const filter = document.querySelector("#rogueGameFilter").value;
  const query = document.querySelector("#roguePieceSearch").value.trim().toLowerCase();
  const filtered = roguePieces.filter((piece) => {
    const matchesGame = filter === "all" || piece.game === filter;
    const haystack = `${piece.name} ${piece.game} ${piece.archetype}`.toLowerCase();
    return matchesGame && haystack.includes(query);
  });
  palette.replaceChildren(...filtered.map((piece) => {
    const button = document.createElement("button");
    const selected = rogueSelectedTool?.slug === piece.slug;
    button.type = "button";
    button.draggable = true;
    button.className = `palette-piece${selected ? " selected" : ""}`;
    button.title = `${piece.name} · ${piece.game}`;
    const visual = createEditorPieceVisual(roguePalettePiece(piece), "palette-visual");
    const label = document.createElement("span");
    label.textContent = piece.name;
    button.append(visual, label);
    button.addEventListener("dragstart", (event) => {
      event.dataTransfer.effectAllowed = "copy";
      event.dataTransfer.setData("text/plain", piece.slug);
      rogueSelectedTool = piece;
      button.classList.add("dragging");
    });
    button.addEventListener("dragend", () => button.classList.remove("dragging"));
    button.addEventListener("click", () => {
      rogueSelectedTool = piece;
      renderRoguePiecePalette();
      document.querySelector("#selectedToolLabel").textContent = `Placing: ${piece.name}`;
    });
    return button;
  }));
}

function createEditorPieceVisual(piece, className = "editor-piece") {
  const asset = assetFor(piece);
  if (asset.type === "image") {
    const image = document.createElement("img");
    image.className = `${className}${facesAwayFromBlackSide(piece) ? " faces-away" : ""}`;
    image.src = asset.src;
    image.alt = "";
    image.addEventListener("error", () => image.replaceWith(document.createTextNode(piece.symbol || piece.code)));
    return image;
  }
  if (asset.type === "sprite") {
    const visual = document.createElement("span");
    visual.className = `${className} sprite ${asset.side}${facesAwayFromBlackSide(piece) ? " faces-away" : ""}`;
    visual.style.setProperty("--piece-image", `url("${asset.src}")`);
    return visual;
  }
  const fallback = document.createElement("span");
  fallback.className = `${className} fallback ${piece.color}${facesAwayFromBlackSide(piece) ? " faces-away" : ""}`;
  fallback.textContent = piece.symbol || piece.code;
  return fallback;
}

function renderRogueBoard() {
  const board = document.querySelector("#rogueBoard");
  const wave = activeRogueWave();
  board.replaceChildren();
  for (let y = 8; y >= 0; y -= 1) {
    for (let x = 0; x < 9; x += 1) {
      const square = document.createElement("button");
      const placed = wave.pieces.find((piece) => piece.x === x && piece.y === y);
      square.type = "button";
      square.className = `square ${(x + y) % 2 === 0 ? "light" : "dark"}${placed ? " occupied" : ""}`;
      square.dataset.x = x;
      square.dataset.y = y;
      square.setAttribute("role", "gridcell");
      square.title = placed ? `${placed.name} at (${x}, ${y}) · click to replace` : `Place at (${x}, ${y})`;
      if (placed) square.append(createEditorPieceVisual(placed));
      square.addEventListener("dragover", (event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = "copy";
        square.classList.add("drag-over");
      });
      square.addEventListener("dragleave", () => square.classList.remove("drag-over"));
      square.addEventListener("drop", (event) => {
        event.preventDefault();
        square.classList.remove("drag-over");
        const slug = event.dataTransfer.getData("text/plain");
        const droppedPiece = roguePieces.find((piece) => piece.slug === slug);
        if (!droppedPiece) return;
        rogueSelectedTool = droppedPiece;
        updateRogueState(() => {
          const index = wave.pieces.findIndex((piece) => piece.x === x && piece.y === y);
          const nextPiece = roguePalettePiece(droppedPiece);
          nextPiece.x = x;
          nextPiece.y = y;
          if (index >= 0) wave.pieces.splice(index, 1);
          wave.pieces.push(nextPiece);
        });
      });
      square.addEventListener("click", () => updateRogueState(() => {
        const index = wave.pieces.findIndex((piece) => piece.x === x && piece.y === y);
        if (rogueSelectedTool) {
          const nextPiece = roguePalettePiece(rogueSelectedTool);
          nextPiece.x = x;
          nextPiece.y = y;
          if (index >= 0) wave.pieces.splice(index, 1);
          wave.pieces.push(nextPiece);
        } else if (index >= 0) {
          wave.pieces.splice(index, 1);
        }
      }));
      square.addEventListener("contextmenu", (event) => {
        event.preventDefault();
        const index = wave.pieces.findIndex((piece) => piece.x === x && piece.y === y);
        if (index >= 0) updateRogueState(() => wave.pieces.splice(index, 1));
      });
      board.append(square);
    }
  }
}

function renderRogueDetails() {
  const wave = activeRogueWave();
  document.querySelector("#waveNameInput").value = wave.name;
  document.querySelector("#waveRewardInput").value = wave.reward;
  document.querySelector("#waveNoteInput").value = wave.note;
  document.querySelector("#deleteWaveButton").disabled = rogueState.waves.length === 1;
}

function renderRogueEditor() {
  renderCharacterChoices();
  renderWaveTabs();
  renderRogueDetails();
  renderRogueBoard();
  renderRoguePiecePalette();
}

async function initRogueEditor() {
  rogueState = loadRogueState();
  const response = await fetch("/api/pieces");
  roguePieces = (await response.json()).pieces;
  document.querySelector("#rogueGameFilter").addEventListener("change", renderRoguePiecePalette);
  document.querySelector("#roguePieceSearch").addEventListener("input", renderRoguePiecePalette);
  document.querySelector("#eraserButton").addEventListener("click", () => {
    rogueSelectedTool = null;
    renderRoguePiecePalette();
    document.querySelector("#selectedToolLabel").textContent = "Eraser selected · click a piece to remove it.";
  });
  [
    ["#waveNameInput", "name"],
    ["#waveRewardInput", "reward"],
    ["#waveNoteInput", "note"],
  ].forEach(([selector, field]) => document.querySelector(selector).addEventListener("input", (event) => {
    activeRogueWave()[field] = event.target.value;
    saveRogueState();
    renderWaveTabs();
  }));
  document.querySelector("#addWaveButton").addEventListener("click", () => updateRogueState(() => {
    const id = rogueState.nextWaveId++;
    rogueState.waves.push({ id, name: `Wave ${rogueState.waves.length + 1}`, reward: "", note: "", pieces: [] });
    rogueState.activeWaveId = id;
  }));
  document.querySelector("#duplicateWaveButton").addEventListener("click", () => updateRogueState(() => {
    const source = activeRogueWave();
    const id = rogueState.nextWaveId++;
    rogueState.waves.push({ ...source, id, name: `${source.name || "Wave"} copy`, pieces: source.pieces.map((piece) => ({ ...piece })) });
    rogueState.activeWaveId = id;
  }));
  document.querySelector("#deleteWaveButton").addEventListener("click", () => updateRogueState(() => {
    if (rogueState.waves.length === 1) return;
    const index = rogueState.waves.findIndex((wave) => wave.id === rogueState.activeWaveId);
    rogueState.waves.splice(index, 1);
    rogueState.activeWaveId = rogueState.waves[Math.max(0, index - 1)].id;
  }));
  renderRogueEditor();
}

async function requestRogue(path, options = {}) {
  const response = await fetch(path, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Rogue request failed");
  roguePlayState = payload;
  rogueSelectedFrom = null;
  roguePendingShopKey = null;
  roguePendingBankIndex = null;
  const token = ++rogueAnimationToken;
  const frames = payload.actionFrames || [];
  renderRoguePlayState(frames.length > 1 ? frames[0].pieces : null);
  if (frames.length > 1) {
    for (let index = 1; index < frames.length; index += 1) {
      await new Promise((resolve) => window.setTimeout(resolve, 420));
      if (token !== rogueAnimationToken) return;
      renderRoguePlayState(frames[index].pieces, frames[index].action);
    }
    renderRoguePlayState();
  }
}

function roguePlayPieceVisual(piece) {
  const asset = assetFor(piece);
  if (asset.type === "image") {
    const image = document.createElement("img");
    image.src = asset.src;
    image.alt = "";
    return image;
  }
  if (asset.type === "sprite") {
    const sprite = document.createElement("span");
    sprite.className = `rogue-play-piece-sprite ${asset.side}`;
    sprite.style.setProperty("--piece-image", `url("${asset.src}")`);
    return sprite;
  }
  const fallback = document.createElement("span");
  fallback.className = `rogue-play-piece-fallback ${piece.color}`;
  fallback.textContent = piece.symbol || piece.code;
  return fallback;
}

function renderRogueCharacterSelect() {
  const select = document.querySelector("#rogueCharacterSelect");
  select.replaceChildren(...(roguePlayState.characters || []).map((character) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "rogue-character-card";
    card.innerHTML = `<span class="character-glyph">${character.name === "Chess" ? "♔" : character.name === "Shogi" ? "王" : "帥"}</span><strong>${character.name}</strong><span>${character.material} material</span><small>${character.ability}</small>`;
    card.addEventListener("click", () => requestRogue("/api/rogue/character", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ character: character.key }),
    }));
    return card;
  }));
}

function renderRoguePlayBoard(boardPieces = null, movingAction = null) {
  const board = document.querySelector("#roguePlayBoard");
  const pieces = boardPieces || roguePlayState.pieces || [];
  const movable = new Set((roguePlayState.movablePieces || []).map((coord) => coord.join(",")));
  board.replaceChildren();
  for (let y = 8; y >= 0; y -= 1) {
    for (let x = 0; x < 9; x += 1) {
      const square = document.createElement("button");
      const piece = pieces.find((item) => item.x === x && item.y === y);
      const selected = rogueSelectedFrom && rogueSelectedFrom[0] === x && rogueSelectedFrom[1] === y;
      square.type = "button";
      square.className = `square ${(x + y) % 2 === 0 ? "light" : "dark"}${selected ? " selected-source" : ""}`;
      square.setAttribute("role", "gridcell");
      square.title = piece ? `${piece.color} ${piece.name} at (${x}, ${y})` : `Empty square (${x}, ${y})`;
      if (piece) {
        const visual = roguePlayPieceVisual(piece);
        visual.classList.add("rogue-piece");
        if (piece.color === "white" && movable.has(`${x},${y}`)) visual.classList.add("rogue-piece-wiggle");
        if (movingAction?.to?.[0] === x && movingAction?.to?.[1] === y && movingAction.actionType === "move") {
          visual.classList.add("rogue-piece-moving");
          visual.style.setProperty("--move-x", `${(movingAction.from[0] - movingAction.to[0]) * 100}%`);
          visual.style.setProperty("--move-y", `${(movingAction.to[1] - movingAction.from[1]) * 100}%`);
        }
        if (piece.assetFamily === "lishogi" && piece.color === "black" && piece.assetName === "FU") visual.classList.add("faces-away");
        square.append(visual);
      }
      square.addEventListener("click", () => handleRogueBoardClick(x, y, piece));
      board.append(square);
    }
  }
}

function handleRogueBoardClick(x, y, piece) {
  if (!roguePlayState || roguePlayState.activePlayer !== "white" || roguePlayState.waveComplete) return;
  if (roguePendingShopKey) {
    if (piece) return setRogueHint("Choose an empty square for the new piece.");
    const shopKey = roguePendingShopKey;
    roguePendingShopKey = null;
    requestRogue("/api/rogue/buy-drop", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ piece: shopKey, to: [x, y] }),
    }).catch(showRogueError);
    return;
  }
  if (roguePendingBankIndex !== null) {
    if (piece) return setRogueHint("Choose an empty square for the banked piece.");
    const bankIndex = roguePendingBankIndex;
    roguePendingBankIndex = null;
    requestRogue("/api/rogue/bank-drop", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bankIndex, to: [x, y] }),
    }).catch(showRogueError);
    return;
  }
  if (!rogueSelectedFrom) {
    if (piece?.color === "white") {
      rogueSelectedFrom = [x, y];
      renderRoguePlayState();
    }
    return;
  }
  const from = rogueSelectedFrom;
  rogueSelectedFrom = null;
  requestRogue("/api/rogue/action", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "move", from, to: [x, y] }),
  }).catch(showRogueError);
}

function setRogueHint(text) {
  document.querySelector("#roguePlayHint").textContent = text;
}

function showRogueError(error) {
  setRogueHint(error.message);
}

function renderRogueShop() {
  const shop = document.querySelector("#rogueShop");
  shop.replaceChildren(...(roguePlayState.shop || []).map((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `rogue-shop-item${roguePendingShopKey === item.key ? " selected" : ""}`;
    button.disabled = roguePlayState.activePlayer !== "white" || roguePlayState.waveComplete || roguePlayState.movesLeft === 0 || roguePlayState.material < item.cost;
    button.innerHTML = `<strong>${item.name}</strong><span>${item.cost} material</span>`;
    button.addEventListener("click", () => {
      roguePendingShopKey = item.key;
      rogueSelectedFrom = null;
      renderRoguePlayState();
      setRogueHint(`Buying ${item.name}: choose an empty square to deploy it.`);
    });
    return button;
  }));
}

function renderRogueReserve() {
  const reserve = document.querySelector("#rogueReserve");
  reserve.textContent = roguePlayState.reserve?.length ? roguePlayState.reserve.map((piece) => piece.name).join(", ") : "Empty";
}

function renderRogueBank() {
  const bank = document.querySelector("#rogueBank");
  bank.replaceChildren(...(roguePlayState.bank || []).map((piece) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `bank-piece${roguePendingBankIndex === piece.index ? " selected" : ""}`;
    button.disabled = roguePlayState.activePlayer !== "white" || roguePlayState.waveComplete || roguePlayState.movesLeft === 0;
    button.textContent = piece.name;
    button.addEventListener("click", () => {
      roguePendingBankIndex = piece.index;
      roguePendingShopKey = null;
      rogueSelectedFrom = null;
      renderRoguePlayState();
      setRogueHint(`Deploying ${piece.name} from the captured bank: choose an empty square.`);
    });
    return button;
  }));
  if (!roguePlayState.bank?.length) bank.textContent = "No captured pieces yet.";
}

function renderRogueReward() {
  const panel = document.querySelector("#rogueRewardPanel");
  panel.hidden = !roguePlayState.waveComplete;
  if (!roguePlayState.waveComplete) return;
  const reward = roguePlayState.reward;
  document.querySelector("#rogueRewardTitle").textContent = `${roguePlayState.wave.name} cleared`;
  document.querySelector("#rogueRewardCopy").textContent = `${reward.kind === "major" ? "Major" : "Minor"} reward: ${reward.material} material. Choose one piece.`;
  const choices = document.querySelector("#rogueRewardChoices");
  choices.replaceChildren(...reward.choices.map((key) => {
    const item = roguePlayState.shop.find((shopItem) => shopItem.key === key);
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = item ? item.name : key;
    button.addEventListener("click", () => requestRogue("/api/rogue/reward", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ piece: key }),
    }).catch(showRogueError));
    return button;
  }));
}

function renderRoguePlayState(boardPieces = null, movingAction = null) {
  if (!roguePlayState) return;
  const selecting = roguePlayState.phase === "character_select";
  document.querySelector("#rogueCharacterSelect").hidden = !selecting;
  document.querySelector("#rogueGameScreen").hidden = selecting;
  if (selecting) {
    renderRogueCharacterSelect();
    return;
  }
  document.querySelector("#roguePlayTitle").textContent = roguePlayState.victory ? "Run complete" : roguePlayState.character.name;
  document.querySelector("#roguePlayIntro").textContent = roguePlayState.victory ? "You cleared the first five-wave test run." : "Your turn first. Spend five actions, then the enemy answers.";
  document.querySelector("#rogueCharacterName").textContent = roguePlayState.character.name;
  document.querySelector("#rogueWaveName").textContent = `${roguePlayState.wave.number}/${roguePlayState.wave.total} · ${roguePlayState.wave.name}`;
  document.querySelector("#rogueMovesLeft").textContent = roguePlayState.movesLeft;
  document.querySelector("#rogueMaterial").textContent = roguePlayState.material;
  document.querySelector("#rogueAbility").textContent = roguePlayState.character.ability;
  document.querySelector("#roguePassButton").disabled = roguePlayState.activePlayer !== "white" || roguePlayState.waveComplete || roguePlayState.movesLeft === 0;
  renderRoguePlayBoard(boardPieces, movingAction);
  renderRogueShop();
  renderRogueReserve();
  renderRogueBank();
  const log = document.querySelector("#rogueBattleLog");
  log.replaceChildren(...(roguePlayState.lastActions || []).map((action) => {
    const item = document.createElement("li");
    item.textContent = action.actionType === "pass" ? `${action.piece} (${action.actionType})` : `${action.piece}: ${action.from} → ${action.to}${action.captured ? `, captured ${action.captured}` : ""}`;
    return item;
  }));
  renderRogueReward();
}

async function initRoguePlay() {
  document.querySelector("#rogueResetButton").addEventListener("click", () => requestRogue("/api/rogue/reset", { method: "POST" }).catch(showRogueError));
  document.querySelector("#roguePassButton").addEventListener("click", () => requestRogue("/api/rogue/action", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "pass" }),
  }).catch(showRogueError));
  // The current playtest session is intentionally single-user and in-memory;
  // entering /rogue always starts at character selection.
  await requestRogue("/api/rogue/reset", { method: "POST" });
}

async function requestState(path, options = {}) {
  const response = await fetch(path, options);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  renderState(payload);
}

async function loadModes() {
  const response = await fetch("/api/modes");
  const payload = await response.json();
  modeSelect.replaceChildren(...payload.modes.map((mode) => {
    const option = document.createElement("option");
    option.value = mode.id;
    option.textContent = mode.name;
    return option;
  }));
  modeSelect.dataset.modes = JSON.stringify(payload.modes);
}

async function renderHome() {
  const response = await fetch("/api/modes");
  const payload = await response.json();
  modeCardsEl.replaceChildren(...payload.modes.map((mode) => {
    const card = document.createElement("a");
    card.className = `mode-card mode-${mode.status}`;
    card.href = `/${mode.id.replace("_", "-")}`;
    card.innerHTML = `
      <span class="mode-card-status">${mode.status.replace("_", " ")}</span>
      <h2>${mode.name}</h2>
      <p>${mode.description}</p>
      <span class="mode-card-link">Enter mode <span aria-hidden="true">→</span></span>
    `;
    return card;
  }));
}

async function step() {
  stepButton.disabled = true;
  try {
    await requestState("/api/step", { method: "POST" });
  } finally {
    stepButton.disabled = false;
  }
}

function stopAuto() {
  window.clearInterval(autoTimer);
  autoTimer = null;
  autoButton.classList.remove("is-active");
}

if (window.location.pathname === "/") {
  homePage.hidden = false;
  gamePage.hidden = true;
  renderHome();
} else if (window.location.pathname === "/rogue/designer") {
  homePage.hidden = true;
  gamePage.hidden = true;
  roguePlayPage.hidden = true;
  roguePage.hidden = false;
  initRogueEditor();
} else if (window.location.pathname === "/rogue") {
  homePage.hidden = true;
  gamePage.hidden = true;
  roguePage.hidden = true;
  roguePlayPage.hidden = false;
  initRoguePlay();
} else {
  homePage.hidden = true;
  gamePage.hidden = false;
  resetButton.addEventListener("click", async () => {
    stopAuto();
    await requestState("/api/reset", { method: "POST" });
  });

  stepButton.addEventListener("click", step);

  autoButton.addEventListener("click", () => {
    if (autoTimer) {
      stopAuto();
      return;
    }
    autoButton.classList.add("is-active");
    autoTimer = window.setInterval(() => {
      step().catch(() => stopAuto());
    }, 650);
  });

  modeSelect.addEventListener("change", async () => {
    const modes = JSON.parse(modeSelect.dataset.modes || "[]");
    const mode = modes.find((item) => item.id === modeSelect.value);
    const variant = mode?.variants?.[0];
    stopAuto();
    const route = modeSelect.value.replace("_", "-");
    history.pushState({}, "", `/${route}`);
    await requestState("/api/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: modeSelect.value, variant }),
    });
  });

  variantSelect.addEventListener("change", async () => {
    await requestState("/api/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "pvp", variant: variantSelect.value }),
    });
  });

  buildBoard();
  loadModes().then(() => {
    const routeMode = {
      "/pvp": "pvp",
      "/bot-maker": "bot_maker",
      "/rogue": "rogue",
    }[window.location.pathname];
    if (!routeMode) return requestState("/api/state");
    const mode = JSON.parse(modeSelect.dataset.modes).find((item) => item.id === routeMode);
    return requestState("/api/mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: routeMode, variant: mode?.variants?.[0] }),
    });
  });
}
