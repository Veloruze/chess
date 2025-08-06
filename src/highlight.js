function drawSuggestion(from, to, style = "outline") {
    console.log(`drawSuggestion called: from=${from}, to=${to}, style=${style}`);
    clearSuggestion();
    const fromSquare = document.querySelector(`wc-chess-board .square-${from}`);
    const toSquare = document.querySelector(`wc-chess-board .square-${to}`);
    if (fromSquare && toSquare) {
        console.log(`Squares found: from=${fromSquare.className}, to=${toSquare.className}`);
        if (style === "overlay") {
            const fromRect = fromSquare.getBoundingClientRect();
            const toRect = toSquare.getBoundingClientRect();
            const overlay = document.createElement("div");
            overlay.id = "suggestion-overlay";
            overlay.style.position = "absolute";
            overlay.style.left = `${fromRect.left}px`;
            overlay.style.top = `${fromRect.top}px`;
            overlay.style.width = `${toRect.right - fromRect.left}px`;
            overlay.style.height = `${toRect.bottom - fromRect.top}px`;
            overlay.style.backgroundColor = "rgba(255, 255, 0, 0.5)";
            overlay.style.pointerEvents = "none";
            document.body.appendChild(overlay);
            console.log("Overlay created.");
        } else {
            fromSquare.classList.add("highlight");
            toSquare.classList.add("highlight");
            console.log("Highlight classes added.");
        }
    } else {
        console.log(`Squares NOT found: from=${from}, to=${to}`);
    }
}

function clearSuggestion() {
    console.log("clearSuggestion called.");
    const overlay = document.getElementById("suggestion-overlay");
    if (overlay) {
        overlay.remove();
        console.log("Overlay removed.");
    }
    const highlighted = document.querySelectorAll(".highlight");
    highlighted.forEach(el => el.classList.remove("highlight"));
    if (highlighted.length > 0) {
        console.log("Highlight classes removed.");
    }
}