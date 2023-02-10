import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import UnoCSS from 'unocss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Pages from 'vite-plugin-pages'
import Layouts from 'vite-plugin-vue-layouts'

// https://vitejs.dev/config/
export default defineConfig({
  base: './',

  build: {
    outDir: './dist',
  },

  resolve: {
    alias: {
      '@/': `${path.resolve(__dirname, 'src')}/`,
    },
  },

  plugins: [
    vue({
      reactivityTransform: true,
    }),

    UnoCSS(),

    AutoImport({
      imports: [
        'vue',
        '@vueuse/core',
        {
          'animol': [
            ['css', 'animate'],
            'ease',
            ['Easing', 'easing'],
            'parseColor',
            'blend',
          ],
          '@jrnwn/utils': [
            'typeOf',
            'createEl',
            'setClass',
            'removeClass',
            'setStyle',
            'getSelector',
            'platform',
            'get',
            'set',
            'getListOfPaths',
          ],
        },
      ],
      dts: 'src/auto-imports.d.ts',
      dirs: [
        'src/composables',
        'src/stores',
        'src/services',
      ],
      vueTemplate: true,
    }),

    Components({
      extensions: ['vue', 'md'],
      include: [/\.vue$/, /\.vue\?vue/, /\.md$/],
      dts: 'src/components.d.ts',
    }),

    Pages({
      extensions: ['vue'],
    }),

    Layouts(),
  ],
})
