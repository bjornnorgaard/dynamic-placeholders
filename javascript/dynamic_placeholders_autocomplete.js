/**
 * Built-in __placeholder__ autocomplete for prompt textareas.
 *
 * Yields to Tag Autocomplete when it is present and wildcards are enabled
 * (this extension also exposes lists via a wildcards/ symlink for TAC).
 */
(function () {
    "use strict";

    const API_URL = "/dynph/v1/completions";
    const MAX_VISIBLE = 12;
    const DEBOUNCE_MS = 40;

    let wrap = "__";
    let names = [];
    let loaded = false;
    let loadPromise = null;
    let popup = null;
    let activeIndex = -1;
    let activeTextarea = null;
    let matchStart = -1;
    let debounceTimer = null;

    function tacHandlesWildcards() {
        try {
            return typeof TAC_CFG !== "undefined" && TAC_CFG && TAC_CFG.useWildcards;
        } catch (_) {
            return false;
        }
    }

    function ensurePopup() {
        if (popup) return popup;
        popup = document.createElement("ul");
        popup.id = "dynph-autocomplete";
        popup.className = "dynph-autocomplete";
        popup.setAttribute("role", "listbox");
        popup.style.display = "none";
        document.body.appendChild(popup);
        return popup;
    }

    function hidePopup() {
        if (!popup) return;
        popup.style.display = "none";
        popup.innerHTML = "";
        activeIndex = -1;
        activeTextarea = null;
        matchStart = -1;
    }

    async function loadCompletions(force) {
        if (loaded && !force) return;
        if (loadPromise && !force) return loadPromise;
        loadPromise = fetch(API_URL, { cache: "no-store" })
            .then((r) => {
                if (!r.ok) throw new Error("dynph completions HTTP " + r.status);
                return r.json();
            })
            .then((data) => {
                wrap = data.wrap || "__";
                names = Array.isArray(data.names) ? data.names : [];
                loaded = true;
            })
            .catch((err) => {
                console.warn("Dynamic Placeholders autocomplete:", err);
            })
            .finally(() => {
                loadPromise = null;
            });
        return loadPromise;
    }

    function findIncomplete(textBefore, wrapStr) {
        if (!wrapStr || !textBefore) return null;

        if (textBefore.endsWith(wrapStr)) {
            const start = textBefore.length - wrapStr.length;
            const before = textBefore.slice(0, start);
            const prev = before.lastIndexOf(wrapStr);
            if (prev >= 0) {
                const between = before.slice(prev + wrapStr.length);
                if (/^[A-Za-z0-9_\-]+(?:[\\/][A-Za-z0-9_\-]+)*$/.test(between)) {
                    return null;
                }
            }
            return { start, prefix: "" };
        }

        const start = textBefore.lastIndexOf(wrapStr);
        if (start < 0) return null;
        const prefix = textBefore.slice(start + wrapStr.length);
        if (!prefix || prefix.includes(wrapStr)) return null;
        if (!/^[A-Za-z0-9_\-]*(?:[\\/][A-Za-z0-9_\-]*)*$/.test(prefix)) return null;
        return { start, prefix };
    }

    function filterNames(prefix) {
        const needle = (prefix || "").toLowerCase().replace(/\\/g, "/");
        const matches = names.filter((n) => n.toLowerCase().includes(needle));
        matches.sort((a, b) => {
            const al = a.toLowerCase();
            const bl = b.toLowerCase();
            const ap = al.startsWith(needle) ? 0 : 1;
            const bp = bl.startsWith(needle) ? 0 : 1;
            if (ap !== bp) return ap - bp;
            if (a.length !== b.length) return a.length - b.length;
            return al < bl ? -1 : al > bl ? 1 : 0;
        });
        return matches.slice(0, MAX_VISIBLE);
    }

    function positionPopup(textarea) {
        const rect = textarea.getBoundingClientRect();
        popup.style.left = `${Math.max(8, rect.left)}px`;
        popup.style.top = `${rect.bottom + 4}px`;
        popup.style.minWidth = `${Math.min(rect.width, 360)}px`;
        popup.style.maxWidth = `${Math.max(rect.width, 280)}px`;
    }

    function renderPopup(matches, textarea) {
        ensurePopup();
        if (!matches.length) {
            hidePopup();
            return;
        }
        activeTextarea = textarea;
        popup.innerHTML = "";
        matches.forEach((name, i) => {
            const li = document.createElement("li");
            li.className = "dynph-autocomplete-item" + (i === 0 ? " active" : "");
            li.setAttribute("role", "option");
            li.dataset.index = String(i);
            li.dataset.name = name;
            li.textContent = `${wrap}${name}${wrap}`;
            li.addEventListener("mousedown", (ev) => {
                ev.preventDefault();
                applyCompletion(name);
            });
            popup.appendChild(li);
        });
        activeIndex = 0;
        positionPopup(textarea);
        popup.style.display = "block";
    }

    function setActive(index) {
        const items = popup ? popup.querySelectorAll(".dynph-autocomplete-item") : [];
        if (!items.length) return;
        activeIndex = ((index % items.length) + items.length) % items.length;
        items.forEach((el, i) => {
            el.classList.toggle("active", i === activeIndex);
        });
        items[activeIndex].scrollIntoView({ block: "nearest" });
    }

    function applyCompletion(name) {
        const ta = activeTextarea;
        if (!ta || matchStart < 0) return;
        const start = matchStart;
        const end = ta.selectionStart;
        const before = ta.value.slice(0, start);
        const after = ta.value.slice(end);
        const inserted = `${wrap}${name}${wrap}`;
        ta.value = before + inserted + after;
        const caret = before.length + inserted.length;
        ta.setSelectionRange(caret, caret);
        ta.dispatchEvent(new Event("input", { bubbles: true }));
        hidePopup();
        ta.focus();
    }

    async function onTextareaInput(textarea) {
        if (tacHandlesWildcards()) {
            hidePopup();
            return;
        }
        await loadCompletions(false);
        const caret = textarea.selectionStart;
        const before = textarea.value.slice(0, caret);
        const found = findIncomplete(before, wrap);
        if (!found) {
            hidePopup();
            return;
        }
        matchStart = found.start;
        renderPopup(filterNames(found.prefix), textarea);
    }

    function scheduleUpdate(textarea) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => onTextareaInput(textarea), DEBOUNCE_MS);
    }

    function onKeyDown(ev) {
        if (!popup || popup.style.display === "none") return;
        if (ev.key === "ArrowDown") {
            ev.preventDefault();
            setActive(activeIndex + 1);
        } else if (ev.key === "ArrowUp") {
            ev.preventDefault();
            setActive(activeIndex - 1);
        } else if (ev.key === "Enter" || ev.key === "Tab") {
            const items = popup.querySelectorAll(".dynph-autocomplete-item");
            if (!items.length || activeIndex < 0) return;
            ev.preventDefault();
            applyCompletion(items[activeIndex].dataset.name);
        } else if (ev.key === "Escape") {
            hidePopup();
        }
    }

    function bindTextarea(textarea) {
        if (!textarea || textarea.dataset.dynphBound === "1") return;
        textarea.dataset.dynphBound = "1";
        textarea.addEventListener("input", () => scheduleUpdate(textarea));
        textarea.addEventListener("click", () => scheduleUpdate(textarea));
        textarea.addEventListener("keyup", (ev) => {
            if (["ArrowDown", "ArrowUp", "Enter", "Tab", "Escape"].includes(ev.key)) return;
            scheduleUpdate(textarea);
        });
        textarea.addEventListener("keydown", onKeyDown);
        textarea.addEventListener("blur", () => {
            // Delay so mousedown on an item can fire first.
            setTimeout(() => {
                if (document.activeElement !== textarea) hidePopup();
            }, 150);
        });
    }

    function scanTextareas() {
        const selectors = [
            "#txt2img_prompt textarea",
            "#txt2img_neg_prompt textarea",
            "#img2img_prompt textarea",
            "#img2img_neg_prompt textarea",
            "#hires_prompt textarea",
            "#hires_neg_prompt textarea",
            "textarea[id*='_prompt']",
        ];
        const seen = new Set();
        for (const sel of selectors) {
            document.querySelectorAll(sel).forEach((ta) => {
                if (seen.has(ta)) return;
                seen.add(ta);
                bindTextarea(ta);
            });
        }
    }

    function boot() {
        if (tacHandlesWildcards()) {
            // Tag Autocomplete owns __ completion; wildcards/ symlink feeds it.
            return;
        }
        loadCompletions(false);
        scanTextareas();
        // Gradio rebuilds DOM; re-bind periodically early on, then settle.
        let tries = 0;
        const timer = setInterval(() => {
            scanTextareas();
            tries += 1;
            if (tries > 40) clearInterval(timer);
        }, 500);
        const observer = new MutationObserver(() => scanTextareas());
        observer.observe(document.body, { childList: true, subtree: true });
    }

    onUiLoaded(boot);
})();
