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
    [/^bg--(\w+)$/, ([, w]) => ({ background: `hsl(var(--${w},0,0%,0%))` })],
    [/^bg--(\w+)\/(\d+)$/, ([, w, d]) => ({
      'background': `hsla(var(--${w},0,0%,0%),var(--opacity,1))`,
      '--opacity': +d / 100,
    })],
    [/^text--(\w+)$/, ([, w]) => ({ color: `hsl(var(--${w},0,0%,0%))` })],
    [/^color--(\w+)$/, ([, w]) => ({ color: `hsl(var(--${w},0,0%,0%))` })],
    [/^fill--(\w+)$/, ([, w]) => ({ fill: `hsl(var(--${w},0,0%,0%))` })],
    [/^stroke--(\w+)$/, ([, w]) => ({ stroke: `hsl(var(--${w},0,0%,0%))` })],
    [/^border--(\w+)$/, ([, w]) => ({ 'border-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^border--(\w+)\/(\d+)$/, ([, w, d]) => ({
      'border-color': `hsla(var(--${w},0,0%,0%),var(--opacity,1))`,
      '--opacity': +d / 100,
    })],
  ],
  shortcuts: [
  ],
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
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
  safelist: 'prose prose-sm m-auto text-left'.split(' '),
})
