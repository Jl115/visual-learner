import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import js from '@eslint/js'
import tseslint from '@typescript-eslint/eslint-plugin'
import tsparser from '@typescript-eslint/parser'
import vueParser from 'vue-eslint-parser'
import vue from 'eslint-plugin-vue'
import importPlugin from 'eslint-plugin-import'
import unusedImports from 'eslint-plugin-unused-imports'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const tsFiles = ['src/**/*.ts', 'src/**/*.vue']

/** Shared FSA layer aliases enforced by import/order */
const fsaPathGroups = [
  { pattern: '@/shared/**', group: 'internal', position: 'before' },
  { pattern: '@/entities/**', group: 'internal', position: 'before' },
  { pattern: '@/features/**', group: 'internal', position: 'before' },
  { pattern: '@/widgets/**', group: 'internal', position: 'before' },
  { pattern: '@/pages/**', group: 'internal', position: 'before' },
  { pattern: '@/app/**', group: 'internal', position: 'before' },

  { pattern: '@shared/**', group: 'internal', position: 'before' },
  { pattern: '@entities/**', group: 'internal', position: 'before' },
  { pattern: '@features/**', group: 'internal', position: 'before' },
  { pattern: '@widgets/**', group: 'internal', position: 'before' },
  { pattern: '@pages/**', group: 'internal', position: 'before' },
  { pattern: '@app/**', group: 'internal', position: 'before' },
]

/** No feature may import the internals of another feature */
const featureNames = [
  'achievements',
  'documentLibrary',
  'documentUpload',
  'knowledgeGraph',
  'masteryProgress',
  'quizSession',
]

const restrictedPaths = []
for (const target of featureNames) {
  for (const fromFeat of featureNames) {
    if (target === fromFeat) continue
    restrictedPaths.push({
      target: `./src/features/${target}`,
      from: `./src/features/${fromFeat}`,
      message: `Cross-feature import blocked: ${target} cannot depend on ${fromFeat}.`,
    })
  }
}

export default [
  // Base JS recommended
  js.configs.recommended,

  // TypeScript + Vue + FSA
  {
    files: tsFiles,
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsparser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: join(__dirname, './tsconfig.json'),
        extraFileExtensions: ['.vue'],
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        requestAnimationFrame: 'readonly',
        fetch: 'readonly',
        navigator: 'readonly',
        location: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
      vue,
      import: importPlugin,
      'unused-imports': unusedImports,
    },
    settings: {
      'import/resolver': {
        typescript: {
          project: join(__dirname, './tsconfig.json'),
        },
      },
    },
    rules: {
      // Vue
      ...vue.configs.essential.rules,
      'vue/multi-word-component-names': 'warn',
      'vue/no-mutating-props': 'error',

      // TypeScript
      'no-unused-vars': 'off',
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', disallowTypeAnnotations: false },
      ],
      'no-undef': 'off',

      // Unused imports
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'warn',
        { vars: 'all', varsIgnorePattern: '^_', args: 'after-used', argsIgnorePattern: '^_' },
      ],

      // General
      'no-console': 'warn',
      'prefer-const': 'error',
      eqeqeq: ['error', 'always'],

      // FSA import/order layer enforcing
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index', 'object', 'type'],
          pathGroups: fsaPathGroups,
          pathGroupsExcludedImportTypes: ['builtin', 'external'],
          'newlines-between': 'always',
          alphabetize: { order: 'asc', caseInsensitive: true },
        },
      ],
      'import/no-duplicates': 'error',
      'import/first': 'error',
      'import/newline-after-import': ['error', { count: 1 }],

      // Cross-feature import restriction
      'import/no-restricted-paths': [
        'error',
        { zones: restrictedPaths },
      ],
    },
  },

  // Ignore patterns
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'coverage/**',
      '*.config.ts',
      '*.config.js',
      '*.config.mjs',
      '*.d.ts',
      '**/*.d.ts',
      '.eslintrc.cjs',
    ],
  },
]
