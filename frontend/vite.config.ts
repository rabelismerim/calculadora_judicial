import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import UnoCSS from 'unocss/vite'


// https://vitejs.dev/config/
export default defineConfig({
  base: './',

  build: {
    outDir: './dist',
  },

  resolve: {
    alias: {
      '~/': `${path.resolve(__dirname, 'src')}/`,
    },
  },

  plugins: [
    vue({
      reactivityTransform: true,
    }),
    
    UnoCSS(),
  ],
})
