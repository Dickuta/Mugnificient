/**
 * Sanitize API responses to remove circular references
 * This prevents Vue's reactivity system from hitting infinite loops
 */

export function sanitizeResponse(data, maxDepth = 3, currentDepth = 0, seen = new WeakSet()) {
  if (data === null || typeof data !== 'object') return data
  if (currentDepth > maxDepth) return null
  
  if (seen.has(data)) return null
  seen.add(data)
  
  if (Array.isArray(data)) {
    return data.map(item => sanitizeResponse(item, maxDepth, currentDepth + 1, seen))
  }
  
  const sanitized = {}
  for (const key in data) {
    if (Object.prototype.hasOwnProperty.call(data, key)) {
      if (key === 'products' && data.constructor?.name === 'Category') {
        continue
      }
      if (key === 'category' && data.constructor?.name === 'Product') {
        sanitized[key] = typeof data[key] === 'object' 
          ? { id: data[key].id, name: data[key].name } 
          : data[key]
        continue
      }
      sanitized[key] = sanitizeResponse(data[key], maxDepth, currentDepth + 1, seen)
    }
  }
  
  seen.delete(data)
  return sanitized
}

export default sanitizeResponse
