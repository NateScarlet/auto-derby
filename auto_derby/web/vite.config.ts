import { defineConfig, build, Plugin } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

import * as cheerio from 'cheerio';
import * as babel from '@babel/core';
import { execSync } from 'child_process';

function shell(command: string): string {
  return execSync(command).toString().trimEnd();
}

const alias = {
  '@/': resolve(__dirname, 'src') + '/',
  'auto-derby/': resolve(__dirname, '..') + '/',
};

const define = {
  __VERSION__: JSON.stringify(shell('git describe --always --dirty')),
};

function one<T>(v: T | T[]): T {
  if (Array.isArray(v)) {
    return v[0];
  }
  return v;
}

export const preload = (): Plugin => ({
  name: 'preload',
  async transformIndexHtml(html) {
    const res = one(
      await build({
        root: __dirname,
        configFile: false,
        plugins: [],
        resolve: { alias },
        define,
        build: {
          write: false,
          target: false,
          rollupOptions: {
            input: resolve(__dirname, './src/preload.ts'),
            output: {
              format: 'iife',
            },
          },
        },
      })
    );
    if (!('output' in res)) {
      throw new Error('invalid build result');
    }
    const output = one(res.output);
    if (!('code' in output)) {
      throw new Error('invalid output');
    }

    const $ = cheerio.load(html);
    const code = (
      await babel.transformAsync(output.code, {
        configFile: false,
        minified: true,
        presets: [['@babel/preset-env', { targets: { ie: 10 } }]],
      })
    ).code;

    $('#app').after(`<script>${code}</script>`);
    return $.html();
  },
});

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias,
  },
  define,
  plugins: [vue(), preload()],
});
