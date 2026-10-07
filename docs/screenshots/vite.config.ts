import path from 'node:path'
import original from '../../frontend/vite.config'

// Preview only: preserve the application plugins and avoid certificate creation.
export default {
  ...original,
  root: path.resolve(__dirname, '../../frontend'),
  base: '/',
  plugins: original.plugins.filter((plugin: any) => !plugin?.name?.includes('mkcert')),
  server: { host: '127.0.0.1', port: 5177, strictPort: true, https: false },
}
