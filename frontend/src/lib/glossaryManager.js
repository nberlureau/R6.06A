import { ModalManager } from "./modalManager.js";

export class GlossaryManager {
    constructor() {
        this.currentEditId = null;
        this.glossaries = null;
        this.load();
    }

    load() {
        this.glossaries = JSON.parse(localStorage.getItem("glossaries")) || [];
        this.nextId = Math.max(...this.glossaries.map(g => g.id), 0) + 1;
    }

    save() {
        localStorage.setItem("glossaries", JSON.stringify(this.glossaries));
    }

    getAll() {
        return this.glossaries;
    }

    get(id) {
        return this.glossaries.find(g => g.id === id);
    }

    create(name, description, terms) {
        const glossary = {
            id: this.nextId++,
            name,
            description,
            terms: []
        };
        if(terms) {
            glossary.terms = terms;
        }
        this.glossaries.push(glossary);
        this.save();
        return glossary;
    }

    update(id, name, description) {
        const g = this.get(id);
        if (!g) return null;
        g.name = name;
        g.description = description;
        
        this.save();
        return g;
    }

    replaceAll(newList) {
        this.glossaries = newList;
        this.save();
    }

    redirectTo(id) {
        window.location.href = `/glossary?id=${id}`;
    }
}