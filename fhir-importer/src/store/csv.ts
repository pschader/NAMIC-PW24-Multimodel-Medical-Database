// Utilities
import { defineStore } from 'pinia'

export const useCsvStore = defineStore('csv', {
  state: () => ({
    headers: [],
    items: []
  }),
  actions: {
    setCsvData(headers, items) {
      this.headers = headers;
      this.items = items;
    }
  }
});