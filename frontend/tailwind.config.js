/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#4F46E5",
        "primary-hover": "#4338CA",
        bg: "#F9FAFB",
        surface: "#FFFFFF",
        text: "#111827",
        muted: "#6B7280",
        border: "#E5E7EB",
      },
      status: {
        draft: "#6B7280",
        issued: "#2563EB",
        paid: "#16A34A",
        overdue: "#DC2626",
        void: "#9CA3AF",
      },
    },
  },
  plugins: [],
}
