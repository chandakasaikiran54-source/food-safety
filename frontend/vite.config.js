import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  const plugins = [react()];
  
  if (process.env.HTTPS === 'true') {
    plugins.push(basicSsl());
  }
  
  return {
    plugins: plugins,
  }
})
