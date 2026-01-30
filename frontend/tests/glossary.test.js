/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GlossaryManager } from '../src/lib/glossaryManager.js';

describe('GlossaryManager', () => {
    let glossaryManager;

    beforeEach(() => {
        // Clear localStorage before each test
        localStorage.clear();

        // Mock window.location
        delete window.location;
        window.location = { href: '' };

        glossaryManager = new GlossaryManager();
    });

    it('should initialize with empty glossaries if localStorage is empty', () => {
        expect(glossaryManager.getAll()).toEqual([]);
    });

    it('should create a new glossary', () => {
        const name = 'Test Glossary';
        const description = 'Test Description';
        const glossary = glossaryManager.create(name, description);

        expect(glossary.name).toBe(name);
        expect(glossary.description).toBe(description);
        expect(glossary.id).toBe(1);
        expect(glossaryManager.getAll()).toHaveLength(1);
    });

    it('should load glossaries from localStorage', () => {
        const sampleGlossaries = [{ id: 1, name: 'L1', description: 'D1', terms: [] }];
        localStorage.setItem('glossaries', JSON.stringify(sampleGlossaries));

        const newManager = new GlossaryManager();
        expect(newManager.getAll()).toEqual(sampleGlossaries);
    });

    it('should update an existing glossary', () => {
        glossaryManager.create('Old Name', 'Old Description');
        const updated = glossaryManager.update(1, 'New Name', 'New Description');

        expect(updated.name).toBe('New Name');
        expect(updated.description).toBe('New Description');
        expect(glossaryManager.get(1).name).toBe('New Name');
    });

    it('should return null when updating non-existent glossary', () => {
        const result = glossaryManager.update(999, 'Name', 'Desc');
        expect(result).toBeNull();
    });

    it('should redirect to glossary page', () => {
        glossaryManager.redirectTo(1);
        expect(window.location.href).toBe('/glossary?id=1');
    });

    it('should replace all glossaries', () => {
        glossaryManager.create('G1', 'D1');
        const newList = [
            { id: 10, name: 'New 1', description: 'Desc 1', terms: [] },
            { id: 11, name: 'New 2', description: 'Desc 2', terms: [] }
        ];
        glossaryManager.replaceAll(newList);

        expect(glossaryManager.getAll()).toEqual(newList);
        expect(JSON.parse(localStorage.getItem('glossaries'))).toEqual(newList);
    });
});
