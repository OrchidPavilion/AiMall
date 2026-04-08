import globals from 'globals';

export default [
  {
    ignores: ['dist/**', 'node_modules/**', 'build/**'],
    files: ['**/*.{js,ts,vue}'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        define: false, // Vue defineComponent
        ref: false,
        reactive: false,
        computed: false
      }
    },
    rules: {
      'vue/multi-word-component-names': 'warn',
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/consistent-type-imports': 'error',
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
    }
  }
];