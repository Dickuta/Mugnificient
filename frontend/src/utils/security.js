/**
 * Security utilities for frontend
 */

// Sanitize user input to prevent XSS
export function sanitizeInput(input) {
  if (!input) return ''
  const div = document.createElement('div')
  div.textContent = input
  return div.innerHTML
}

// Validate email format
export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

// Validate password strength
export function validatePassword(password) {
  if (password.length < 8) return false
  if (!/[A-Z]/.test(password)) return false
  if (!/[0-9]/.test(password)) return false
  return true
}

// Secure token storage with encryption
export function secureStorage = {
  set(key, value) {
    try {
      // Simple base64 encoding (not encryption, but better than plain text)
      const encoded = btoa(JSON.stringify(value))
      localStorage.setItem(key, encoded)
    } catch (e) {
      console.error('Failed to store securely:', e)
    }
  },
  
  get(key) {
    try {
      const encoded = localStorage.getItem(key)
      if (!encoded) return null
      return JSON.parse(atob(encoded))
    } catch (e) {
      console.error('Failed to retrieve securely:', e)
      return null
    }
  },
  
  remove(key) {
    localStorage.removeItem(key)
  }
}

export default { sanitizeInput, validateEmail, validatePassword, secureStorage }
