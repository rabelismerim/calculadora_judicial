import {
  defineConfig,
  presetAttributify,
  presetTypography,
  presetUno,
  presetWebFonts,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'
import presetIcons from '@unocss/preset-icons'

export default defineConfig({
  rules: [
    ['block', { display: 'block !important' }],
    [/^bg--([\w-]+)$/, ([, w]) => ({ background: `hsl(var(--${w},0,0%,0%))` })],
    [/^bg--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ background: `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^text--([\w-]+)$/, ([, w]) => ({ color: `hsl(var(--${w},0,0%,0%))` })],
    [/^color--([\w-]+)$/, ([, w]) => ({ color: `hsl(var(--${w},0,0%,0%))` })],
    [/^fill--([\w-]+)$/, ([, w]) => ({ fill: `hsl(var(--${w},0,0%,0%))` })],
    [/^fill--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ fill: `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^stop--([\w-]+)$/, ([, w]) => ({ 'stop-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^stop--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ 'stop-color': `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^stroke--([\w-]+)$/, ([, w]) => ({ stroke: `hsl(var(--${w},0,0%,0%))` })],
    [/^border--([\w-]+)$/, ([, w]) => ({ 'border-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^border--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ 'border-color': `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^outline--([\w-]+)$/, ([, w]) => ({ outline: `2px solid hsl(var(--${w},0,0%,0%))` })],
    [/^outline--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ outline: `2px solid hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    ['max-w-fill', { 'max-width': '-webkit-fill-available' }],
    [/^ring--(\w+)$/, ([, w]) => ({ '--un-ring-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^ring--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ '--un-ring-color': `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    ['ring-inner', { 'box-shadow': 'inset var(--un-ring-offset-shadow),inset var(--un-ring-shadow), var(--un-shadow) !important' }],
    ['text-vertical', { 'writing-mode': 'vertical-lr' }],
    [/^m-([\.\d]+)\!$/, ([_, num]) => ({ margin: `${num}px !important` })],
    [/^mb-([\.\d]+)\!$/, ([_, num]) => ({ 'margin-botton': `${num}px !important` })],
    [/^mt-([\.\d]+)\!$/, ([_, num]) => ({ 'margin-top': `${num}px !important` })],
    [/^mr-([\.\d]+)\!$/, ([_, num]) => ({ 'margin-rigth': `${num}px !important` })],
    [/^ml-([\.\d]+)\!$/, ([_, num]) => ({ 'margin-left': `${num}px !important` })],
  ],
  shortcuts: [
    { tween: 'transition ease-in-out duration-300' },
    [/^tween-(\d+)$/, ([, d]) => `transition ease-in-out duration-${d}`],
  ],
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
      collections: {
        carbon: () => import('@iconify-json/carbon').then(module => module.icons),
      },
    }),
    presetTypography(),
    presetWebFonts({
      fonts: {
        sans: 'DM Sans',
        serif: 'DM Serif Display',
        mono: 'DM Mono',
      },
    }),
  ],
  transformers: [
    transformerDirectives(),
    transformerVariantGroup(),
  ],
})
