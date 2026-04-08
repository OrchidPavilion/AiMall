import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig(async () => {
  const autoImport = (await import('unplugin-auto-import/vite')).default;
  const vueComponents = (await import('unplugin-vue-components/vite')).default;
  const ElementPlusResolver = (await import('unplugin-vue-components/resolvers')).ElementPlusResolver;

  return {
    plugins: [
      vue(),
      // Element Plus 自动导入
      autoImport({
        imports: ['vue', 'vue-router', 'pinia'],
        dts: 'src/auto-imports.d.ts'
      }),
      vueComponents({
        // Element Plus 按需引入
        resolvers: [ElementPlusResolver()],
        dts: 'src/components.d.ts'
      })
    ],
    
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/styles/variables.scss" as *;`
        }
      }
    },
    
    server: {
      port: 3100,
      open: false,
      proxy: {
        '/api': {
          target: 'http://localhost:18080',
          changeOrigin: true
        }
      }
    },
    
    build: {
      outDir: 'dist',
      sourcemap: true,
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true
        }
      },
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'pinia'],
            element: ['element-plus', '@element-plus/icons-vue'],
            utils: ['axios', 'lodash-es', 'date-fns']
          }
        }
      }
    }
  };
});
