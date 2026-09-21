import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dts from 'vite-plugin-dts'
import { resolve } from 'path'

export default defineConfig(({ command, mode }) => {
    // Dev server config — also applies during preview
    const server = {
        port: 5173,
        host: true,
    };

    // Application mode (yarn dev) — used by TestRunner.tsx for local preview
    if (mode !== 'lib') {
        return {
            server,
            plugins: [react()],
        };
    }

    // Library mode (yarn build --mode lib) — the Chub Stage bundle
    return {
        server,
        plugins: [
            react(),
            dts({
                outDir: ['dist'],
                include: ['src/**/*.ts*'],
                staticImport: true,
                rollupTypes: true,
                insertTypesEntry: true,
            }),
        ],
        build: {
            lib: {
                entry: resolve(__dirname, 'src/index.ts'),
                name: 'index',
                formats: ['umd', 'es', 'cjs', 'iife'],
                fileName: 'index',
            },
            rollupOptions: {
                external: ['react', 'react-dom'],
                output: {
                    globals: {
                        react: 'React',
                        'react-dom': 'ReactDOM',
                    },
                },
            },
        },
    };
});