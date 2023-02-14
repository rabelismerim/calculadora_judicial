import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetTypography,
  presetUno,
  presetWebFonts,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

export default defineConfig({
  rules: [
    [/^bg--(\w+)$/, ([, w]) => ({ background: `var(--${w})` })],
    [/^text--(\w+)$/, ([, w]) => ({ color: `var(--${w})` })],
    [/^color--(\w+)$/, ([, w]) => ({ color: `var(--${w})` })],
    [/^fill--(\w+)$/, ([, w]) => ({ fill: `var(--${w})` })],
    [/^stroke--(\w+)$/, ([, w]) => ({ stroke: `var(--${w})` })],
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
