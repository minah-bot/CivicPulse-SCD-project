import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default [
  // Ignore generated files
  {
    ignores: ["dist/**", "coverage/**"],
  },

  // JavaScript recommended rules
  js.configs.recommended,

  // TypeScript recommended rules
  ...tseslint.configs.recommended,

  // React + TypeScript files
  {
    files: ["**/*.{ts,tsx}"],

    languageOptions: {
      globals: globals.browser,
    },

    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },

    rules: {
      ...reactHooks.configs.flat.recommended.rules,
      ...reactRefresh.configs.vite.rules,
    },
  },

  // Disable the React setState-in-effect rule for pages
  {
    files: [
      "src/pages/Dashboard.tsx",
      "src/pages/Stats.tsx",
    ],

    rules: {
      "react-hooks/set-state-in-effect": "off",
    },
  },
];