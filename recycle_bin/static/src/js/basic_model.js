/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { DynamicList } from "@web/model/relational_model/dynamic_list";
import { FormController } from "@web/views/form/form_controller";
import { deleteConfirmationMessage } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(DynamicList.prototype, {
    async _deleteRecords(records = []) {
        console.log("Custom before _deleteRecords called");

        // get screenshot
        const canvas = await html2canvas(document.querySelector("html"));

        // call original method
        const result = await super._deleteRecords(records);

        // call controller to save screenshot
        const imageData = canvas.toDataURL("image/png").replace(/^data:image\/png;base64,/, "");
        const resIds = await this.getResIds(true);
        await rpc("/unlink-screenshot", {
            image: imageData,
            model: this.resModel,
            records: resIds
        });

        console.log("Screenshot sent to server ✅");
        return result;
    },
});

patch(FormController.prototype, {
    get deleteConfirmationDialogProps() {
        return {
            title: _t("Bye-bye, record!"),
            body: deleteConfirmationMessage,
            confirm: async () => {

                // get screenshot
                const canvas = await html2canvas(document.querySelector("html"));

                // get deleted records
                const recordIds = [this.model.root.resId];

                // call original method
                await this.model.root.delete();
                if (!this.model.root.resId) {
                    this.env.config.historyBack();

                    // call controller to save screenshot
                    const imageData = canvas.toDataURL("image/png").replace(/^data:image\/png;base64,/, "");
                    await rpc("/unlink-screenshot", {
                        image: imageData,
                        model: this.props.resModel,
                        records: recordIds
                    });
                }
            },
            confirmLabel: _t("Delete"),
            cancel: () => {},
            cancelLabel: _t("No, keep it"),
        };
    }
});
