import { ref } from 'vue'

const isDark = ref(localStorage.getItem('theme') !== 'light')

function apply() {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

apply()

export function useTheme() {
  function toggle() {
    isDark.value = !isDark.value
    apply()
  }
  return { isDark, toggle }
}
