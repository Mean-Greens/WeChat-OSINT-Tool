import { create } from 'zustand';

interface WordListState {
  words: string[];
  addWord: (word: string) => void;
  removeWord: (word: string) => void;
}

export const useWordListStore = create<WordListState>((set) => ({
  words: [],
  addWord: (word) =>
    set((state) => ({
      words: [...new Set([...state.words, word])],
    })),
  removeWord: (word) =>
    set((state) => ({
      words: state.words.filter((w) => w !== word),
    })),
}));