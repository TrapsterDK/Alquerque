let boardsvg = document.getElementById("boardsvg");
let boardcells = document.getElementById("boardcells");
let back_menu = document.getElementById("back-menu");
let menu = document.getElementById("menu");
let game = document.getElementById("game");

let piece = document.createElement("div");
piece.classList.add("cell");

let circle_percentage = 0.4;

function drawLine(fx, fy, tx, ty, spacing) {
    let line = `<line x1='${fx * spacing + spacing / 2}' y1='${
        fy * spacing + spacing / 2
    }' x2='${tx * spacing + spacing / 2}' y2='${
        ty * spacing + spacing / 2
    }' stroke='#3c3c3c' stroke-width='8' />`;
    boardsvg.innerHTML += line;
}

function drawCircle(x, y, spacing, radius) {
    let circle = `<circle cx='${x * spacing + spacing / 2}' cy='${
        y * spacing + spacing / 2
    }' r='${radius}' stroke='#3c3c3c'  fill='#3c3c3c' />`;

    boardsvg.innerHTML += circle;
}

function drawBoard() {
    boardsvg.innerHTML = "";
    let board_size = boardsvg.clientWidth;
    let circle_spacing = board_size / 5;
    let circle_radius = (circle_spacing / 2) * circle_percentage;

    // draw circles
    for (let x = 0; x < 5; x++) {
        for (let y = 0; y < 5; y++) {
            drawCircle(x, y, circle_spacing, circle_radius);
        }
    }

    // vertical
    drawLine(0, 0, 0, 4, circle_spacing);
    drawLine(1, 0, 1, 4, circle_spacing);
    drawLine(2, 0, 2, 4, circle_spacing);
    drawLine(3, 0, 3, 4, circle_spacing);
    drawLine(4, 0, 4, 4, circle_spacing);

    // horizontal
    drawLine(0, 0, 4, 0, circle_spacing);
    drawLine(0, 1, 4, 1, circle_spacing);
    drawLine(0, 2, 4, 2, circle_spacing);
    drawLine(0, 3, 4, 3, circle_spacing);
    drawLine(0, 4, 4, 4, circle_spacing);

    // diagonals
    drawLine(0, 0, 4, 4, circle_spacing);
    drawLine(0, 4, 4, 0, circle_spacing);

    //short diagonals
    drawLine(2, 0, 4, 2, circle_spacing);
    drawLine(0, 2, 2, 0, circle_spacing);
    drawLine(0, 2, 2, 4, circle_spacing);
    drawLine(2, 4, 4, 2, circle_spacing);
}

for (let i = 1; i < 26; i++) {
    let addpiece = piece.cloneNode(false);
    addpiece.id = i;
    boardcells.appendChild(addpiece);
}

back_menu.addEventListener("click", () => {
    menu.style.visibility = "visible";
    game.style.visibility = "hidden";
});

window.addEventListener("resize", drawBoard);
drawBoard();
