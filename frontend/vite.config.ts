import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import UnoCSS from 'unocss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Pages from 'vite-plugin-pages'
import Layouts from 'vite-plugin-vue-layouts'
import mkcert from 'vite-plugin-mkcert'
import { quasar } from '@quasar/vite-plugin'
import { QuasarResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  base: './',

  define: {
    APP_VERSION: JSON.stringify(process.env.npm_package_version),
  },

  build: {
    // outDir: './dist',
    outDir: path.resolve(__dirname, '../backend/djud/static/src/vue/dist/'),
  },

  resolve: {
    alias: {
      '@/': `${path.resolve(__dirname, 'src')}/`,
    },
  },

  server: {
    https: true,
  },

  plugins: [
    vue({
      reactivityTransform: true,
    }),

    quasar({
      autoImportComponentCase: 'pascal',
      sassVariables: 'src/assets/quasar-variables.sass',
    }),

    UnoCSS(),

    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'vue/macros',
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
            'getCookie',
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
      resolvers: [QuasarResolver()],
      dts: 'src/components.d.ts',
    }),

    Pages({
      extensions: ['vue'],
    }),

    Layouts(),

    mkcert(),
  ],
})
