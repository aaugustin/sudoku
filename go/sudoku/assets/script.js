document.addEventListener("DOMContentLoaded", function () {
    // If a <td contenteditable> element contains nothing, its height
    // collapses to zero and the cursor isn't vertically centered anymore.
    // Add a line break, which the browser ignores, to avoid this problem.
    // Firefox uses this workaround; see also:
    // https://bugzilla.mozilla.org/show_bug.cgi?id=503838

    function fixEmptyCell(cell) {
        if (cell.textContent === "") {
            cell.innerHTML = "<br>";
        }
    }

    document.querySelector("table").addEventListener("input", function (event) {
        fixEmptyCell(event.target);
    });

    // Add classes to <td contenteditable> elements based on their contents.

    function setCellMarkers(cell) {
        if (cell.textContent.match(/^[1-9]*$/)) {
            cell.classList.remove("invalid");
        } else {
            cell.classList.add("invalid");
        }
        if (cell.textContent.length < 2) {
            cell.classList.remove("temporary");
        } else {
            cell.classList.add("temporary");
        }
    }

    document.querySelector("table").addEventListener("input", function (event) {
        setCellMarkers(event.target);
    });

    // Save and restore input state with location hash.

    const inputs = Array.from(document.querySelectorAll("[contenteditable]"));
    const separator = "|";

    function getState() {
        return inputs.map((input) => input.textContent).join(separator);
    }

    function setState(state) {
        const contents = state.split(separator);
        window.console.assert(
            inputs.length === contents.length,
            "Cannot restore grid, was the URL truncated?"
        );
        inputs.forEach(function (input, index) {
            input.textContent = contents[index];
            fixEmptyCell(input);
            setCellMarkers(input);
        });
    }

    function saveState() {
        window.location = "#" + encodeURIComponent(getState());
    }

    function restoreState() {
        if (window.location.hash[0] === "#") {
            const state = decodeURIComponent(window.location.hash.slice(1));
            if (state !== getState()) {
                // Hash was changed by navigation, not by saveInputs().
                setState(state);
            }
        }
    }

    restoreState();
    window.addEventListener("hashchange", restoreState);
    document.querySelector("table").addEventListener("input", saveState);
});
