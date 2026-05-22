/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

// ─── Search Dialog ────────────────────────────────────────────────────────────

class GlobalSearchDialog extends Component {
    static template = "webright_global_search.GlobalSearchDialog";
    static components = { Dialog };
    static props = {
        close: Function,
        initialQuery: { type: String, optional: true },
    };

    setup() {
        this.actionService = useService("action");
        this.state = useState({
            query:    "",
            results:  [],
            loading:  false,
            searched: false,
            errorMsg: "",
        });
        this.inputRef       = useRef("searchInput");
        this._debounceTimer = null;

        onMounted(() => {
            const initial = (this.props.initialQuery || "").trim();
            if (initial) {
                this.state.query   = initial;
                this.state.loading = true;
                if (this.inputRef.el) {
                    this.inputRef.el.value = initial;
                    this.inputRef.el.focus();
                }
                this._doSearch(initial);
            } else {
                this.inputRef.el?.focus();
            }
        });
    }

    get groupedResults() {
        const groups = new Map();
        for (const r of this.state.results) {
            if (!groups.has(r.model_label)) groups.set(r.model_label, []);
            groups.get(r.model_label).push(r);
        }
        return [...groups.entries()].map(([label, items]) => ({ label, items }));
    }

    onSearchInput(ev) {
        const query = ev.target.value;
        this.state.query = query;
        clearTimeout(this._debounceTimer);

        if (query.trim().length < 1) {
            Object.assign(this.state, {
                results: [], searched: false, loading: false, errorMsg: "",
            });
            return;
        }

        this.state.loading  = true;
        this.state.errorMsg = "";
        const clean = query.trim().replace(/^\/+/, "");
        this._debounceTimer = setTimeout(() => this._doSearch(clean), 300);
    }

    async _doSearch(query) {
        try {
            const results = await rpc("/web/global_search/search", {
                query,
                limit: 10,
            });
            this.state.results  = results || [];
            this.state.searched = true;
            this.state.errorMsg = "";
        } catch (err) {
            const msg = err?.message || String(err);
            console.error("[Webright Global Search] failed:", msg, err);
            this.state.results  = [];
            this.state.searched = true;
            this.state.errorMsg = msg;
        } finally {
            this.state.loading = false;
        }
    }

    openRecord(result) {
        this.props.close();
        this.actionService.doAction({
            type:      "ir.actions.act_window",
            res_model: result.model,
            res_id:    result.id,
            views:     [[false, "form"]],
            target:    "current",
        });
    }
}

// ─── Hotkey service: Ctrl+Shift+F ────────────────────────────────────────────

registry.category("services").add("webright_global_search_service", {
    dependencies: ["hotkey", "dialog"],
    start(_env, { hotkey, dialog }) {
        hotkey.add(
            "control+shift+f",
            () => dialog.add(GlobalSearchDialog, {}),
            { global: true },
        );
        return {};
    },
});

// ─── Command palette: Ctrl+K → type + ────────────────────────────────────────

// 1. Configure the custom "+" namespace in the command setup registry
registry.category("command_setup").add("+", {
    debounceDelay: 200,
    name: _t("Global Search"),
    placeholder: _t("Search all Odoo records... (e.g., Jick)"),
    emptyMessage: _t("No query provided"),
});

// 2. Add the provider bound strictly to the "+" namespace
// Note: Ensure it says "command_provider" (singular), which is the correct Odoo registry
registry.category("command_provider").add("webright_global_search", {
    namespace: "+",
    async provide(env, options) {
        // Because of the namespace, Odoo automatically strips the "+" sign.
        // options.searchValue will only contain the text typed AFTER the "+".
        const query = String(options.searchValue || "").trim();

        if (!query) {
            return [{
                name: _t("Type your search query (e.g., Jick, INV-11942)"),
                action() {}, // Action is empty until they type something
            }];
        }

        return [{
            name: _t(`Search all records for: "${query}"`),
            action() { // Opens the modal instantly when they press Enter or click
                env.services.dialog.add(GlobalSearchDialog, { initialQuery: query });
            },
        }];
    },
});