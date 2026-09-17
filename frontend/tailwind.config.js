/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#070B14",
        surface: "#0F172A",
        surfaceBorder: "#1E293B",
        accentCyan: "#06B6D4",
        accentEmerald: "#10B981",
        accentAmber: "#F59E0B",
        accentRose: "#F43F5E",
      },
    },
  },
  plugins: [],
}
