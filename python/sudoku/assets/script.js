document.addEventListener("DOMContentLoaded", function () {
    const getNextCell = {
        left: function (cell) {
            return cell.previousElementSibling;
        },
        right: function (cell) {
            return cell.nextElementSibling;
        },
        up: function (cell) {
            const row = cell.parentElement.previousElementSibling;
            const idx = Array.from(cell.parentElement.childNodes).indexOf(cell);
            return row !== null ? row.childNodes[idx] : null;
        },
        down: function (cell) {
            const row = cell.parentElement.nextElementSibling;
            const idx = Array.from(cell.parentElement.childNodes).indexOf(cell);
            return row !== null ? row.childNodes[idx] : null;
        },
    };

    // Move focus in the grid.

    function moveFocus(cell, direction) {
        while (true) {
            cell = getNextCell[direction](cell);
            if (cell === null) {
                return;
            }
            if (cell.isContentEditable) {
                cell.focus();
                return;
            }
        }
    }

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

    // Clear the content of a <td contenteditable>.

    function deleteCellContent(cell) {
        cell.textContent = "";
        fixEmptyCell(cell);
        cell.classList.remove("temporary");
    }

    // Normalize the content of a <td contenteditable>.

    function normalizeCellContent(cell) {
        var content = cell.textContent;

        // Sort.
        content = content.split("");
        content.sort();
        content = content.join("");

        // Keep only non-zero digits.
        content = content.replace(/[^1-9]+/g, "");

        // Remove duplicate digits.
        content = content.replace(/([1-9])\1/g, "");

        // Replace cell content.
        cell.textContent = content;
        fixEmptyCell(cell);

        // Add a class if the cell contains more than one digit.
        if (content.length < 2) {
            cell.classList.remove("temporary");
        } else {
            cell.classList.add("temporary");
        }
    }

    document
        .querySelector("table")
        .addEventListener("keydown", function (event) {
            const arrowKeys = [
                "ArrowDown",
                "ArrowLeft",
                "ArrowRight",
                "ArrowUp",
            ];
            if (arrowKeys.includes(event.key)) {
                moveFocus(event.target, event.key.slice(5).toLowerCase());
            }
            const deleteKeys = ["Backspace", "Clear", "Delete"];
            if (deleteKeys.includes(event.key)) {
                deleteCellContent(event.target);
            }
        });

    document.querySelector("table").addEventListener("input", function (event) {
        normalizeCellContent(event.target);
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
            normalizeCellContent(input);
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
