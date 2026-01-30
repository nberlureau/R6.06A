// frontend/src/lib/confirmModal.js
export class ConfirmModal {
    modal = null;
    resolve = null;
    reject = null;

    constructor() {
        this.init();
    }

    init() {
        // Créer la structure de la modal
        this.modal = document.createElement('div');
        this.modal.id = 'customConfirmModal';
        this.modal.className = 'hidden fixed inset-0 z-50';
        this.modal.innerHTML = `
            <div class="modal-overlay absolute inset-0 bg-opacity-30 backdrop-blur-sm" id="confirmModalOverlay"></div>
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="modal-content bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 relative">
                    <h3 class="text-2xl font-semibold text-gray-900 mb-6">Confirmation</h3>
                    
                    <div class="space-y-4 mb-6">
                        <p id="confirmMessage" class="text-gray-600"></p>
                    </div>

                    <div class="flex justify-end gap-3">
                        <button
                            id="confirmCancelBtn"
                            class="px-6 py-2 border border-gray-300 rounded-lg font-medium text-gray-900 hover:bg-gray-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            id="confirmOkBtn"
                            class="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
                        >
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Ajouter au DOM
        document.body.appendChild(this.modal);

        // Événements
        const overlay = this.modal.querySelector('#confirmModalOverlay');
        const cancelBtn = this.modal.querySelector('#confirmCancelBtn');
        const okBtn = this.modal.querySelector('#confirmOkBtn');

        const closeModal = () => {
            this.modal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        };

        overlay.addEventListener('click', () => {
            closeModal();
            if (this.reject) this.reject(false);
        });

        cancelBtn.addEventListener('click', () => {
            closeModal();
            if (this.reject) this.reject(false);
        });

        okBtn.addEventListener('click', () => {
            closeModal();
            if (this.resolve) this.resolve(true);
        });

        // Gestion de la touche Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                closeModal();
                if (this.reject) this.reject(false);
            }
        });
    }

    show(message) {
        return new Promise((resolve, reject) => {
            this.resolve = resolve;
            this.reject = reject;

            // Mettre à jour le message
            document.getElementById('confirmMessage').textContent = message;

            // Afficher la modal
            this.modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        });
    }
}