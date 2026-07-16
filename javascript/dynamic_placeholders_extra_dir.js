/**
 * Restore the Additional placeholders directory textbox after WebUI load.
 *
 * Script UI defaults are overridden by ui-config.json (often empty), so the
 * persisted path must be pushed into the field once Gradio has mounted.
 */
(function () {
    "use strict";

    const API_URL = "/dynph/v1/extra-dir";
    const FIELD_ID = "dynph_extra_dir";

    function setNativeValue(el, value) {
        const proto = el.tagName === "TEXTAREA"
            ? window.HTMLTextAreaElement.prototype
            : window.HTMLInputElement.prototype;
        const descriptor = Object.getOwnPropertyDescriptor(proto, "value");
        if (descriptor && descriptor.set) {
            descriptor.set.call(el, value);
        } else {
            el.value = value;
        }
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function findFields() {
        const root = typeof gradioApp === "function" ? gradioApp() : document;
        const hosts = root.querySelectorAll("#" + FIELD_ID);
        const fields = [];
        hosts.forEach((host) => {
            const el = host.tagName === "TEXTAREA" || host.tagName === "INPUT"
                ? host
                : host.querySelector("textarea, input");
            if (el) fields.push(el);
        });
        // Fallback: label-adjacent search if elem_id landed elsewhere.
        if (!fields.length) {
            root.querySelectorAll("textarea, input").forEach((el) => {
                const wrap = el.closest(".form, .gr-form, label, div");
                const label = wrap && wrap.querySelector("label, span, .label-wrap");
                if (label && /Additional placeholders directory/i.test(label.textContent || "")) {
                    fields.push(el);
                }
            });
        }
        return fields;
    }

    function restore() {
        fetch(API_URL, { cache: "no-store" })
            .then((r) => {
                if (!r.ok) throw new Error("HTTP " + r.status);
                return r.json();
            })
            .then((data) => {
                const path = (data && data.path) || "";
                if (!path) return;
                findFields().forEach((el) => {
                    if ((el.value || "").trim() !== path) {
                        setNativeValue(el, path);
                    }
                });
            })
            .catch((err) => {
                console.warn("Dynamic Placeholders: restore extra dir failed:", err);
            });
    }

    function boot() {
        restore();
        // Gradio may remount script accordions shortly after first paint.
        let tries = 0;
        const timer = setInterval(() => {
            restore();
            tries += 1;
            if (tries > 10) clearInterval(timer);
        }, 500);
    }

    if (typeof onUiLoaded === "function") {
        onUiLoaded(boot);
    } else {
        document.addEventListener("DOMContentLoaded", boot);
    }
})();
