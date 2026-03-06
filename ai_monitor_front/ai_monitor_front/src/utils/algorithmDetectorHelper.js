export function detectAlgorithm(code) {
  if (code.includes("for") && code.match(/for/g).length >= 2) {
    return "Nested Loop Pattern";
  }
  return "Unknown";
}