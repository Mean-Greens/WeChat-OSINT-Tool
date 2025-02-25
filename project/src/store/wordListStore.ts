import { create } from 'zustand';

interface WordListState {
  words: string[];
  addWord: (word: string) => Promise<void>;
  removeWord: (word: string) => Promise<void>;
  fetchWords: () => Promise<void>;
}

export const useWordListStore = create<WordListState>((set) => ({
  words: [],
  fetchWords: async () => {
    try {
      const res = await fetch('http://localhost:5000/api/words');
      const data = await res.json();
      set({ words: data.words });
    } catch (error) {
      console.error('Error fetching words:', error);
    }
  },
  addWord: async (word) => {
    try {
      const res = await fetch('http://localhost:5000/api/words', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ word }),
      });
      const data = await res.json();
      set({ words: data.words });
    } catch (error) {
      console.error('Error adding word:', error);
    }
  },
  removeWord: async (word) => {
    try {
      const res = await fetch(`http://localhost:5000/api/words/${word}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      set({ words: data.words });
    } catch (error) {
      console.error('Error removing word:', error);
    }
  },
}));