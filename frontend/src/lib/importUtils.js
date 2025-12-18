export class ImportUtils {
    constructor(storage, renderer, modalManager) {
        this.storage = storage;
        this.renderer = renderer;
        this.modals = modalManager;
    }

    async import(file) {
        const ext = file.name.split(".").pop().toLowerCase();
        const text = await file.text();

        const { parseMarkdown, parseJSON } = await import("./exportDocuments.js");

        const parsed =
            ext === "md" ? parseMarkdown(text) : parseJSON(text);

        const glossary = this.storage.create(
            parsed.title || "Imported Glossary",
            parsed.description || "Imported file"
        );

        glossary.terms = parsed.data.map((r, i) => ({
            id: i + 1,
            term: r[0],
            definition: r[1],
            synonyms: Array.isArray(r[2]) ? r[2] : []
        }));

        this.storage.save();
        this.renderer.render();
        this.modals.close("importModal");

        window.location.href = `/glossary?id=${glossary.id}`;
    }
}
