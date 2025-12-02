// frontend/src/lib/deleteUtils.js
import { ConfirmModal } from './confirmModal.js';

export class DeleteUtils {
    constructor() {
        this.confirmModal = new ConfirmModal();
    }

    async deleteItem(message, deleteFunction) {
        try {
            const confirmed = await this.confirmModal.show(message);
            if (confirmed) {
                await deleteFunction();
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error in deleteItem:', error);
            return false;
        }
    }

    // Méthode pour supprimer un terme du glossaire
    async deleteTerm(glossaryId, termId, updateCallback) {
        const message = "Are you sure you want to delete this term?";

        return await this.deleteItem(message, async () => {
            // Charger les glossaires
            const glossaries = JSON.parse(localStorage.getItem("glossaries")) || [];
            const glossaryIndex = glossaries.findIndex(g => g.id === glossaryId);

            if (glossaryIndex !== -1) {
                // Filtrer le terme à supprimer
                glossaries[glossaryIndex].terms = glossaries[glossaryIndex].terms.filter(t => t.id !== termId);

                // Sauvegarder
                localStorage.setItem("glossaries", JSON.stringify(glossaries));

                // Callback pour mettre à jour l'UI
                if (updateCallback) {
                    updateCallback();
                }

                return true;
            }
            return false;
        });
    }

    // Méthode pour supprimer un glossaire
    async deleteGlossary(glossaryId, updateCallback) {
        const message = "Are you sure you want to delete this glossary?";

        return await this.deleteItem(message, async () => {
            // Charger les glossaires
            const glossaries = JSON.parse(localStorage.getItem("glossaries")) || [];

            // Filtrer le glossaire à supprimer
            const updatedGlossaries = glossaries.filter(g => g.id !== glossaryId);

            // Sauvegarder
            localStorage.setItem("glossaries", JSON.stringify(updatedGlossaries));

            // Callback pour mettre à jour l'UI
            if (updateCallback) {
                updateCallback(updatedGlossaries);
            }

            return true;
        });
    }
}