// utils/highlight.js

const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const KW = {
  javascript: /\b(const|let|var|function|return|if|else|for|while|class|import|export|default|new|this|typeof|null|undefined|true|false|async|await|of|in|from|try|catch|throw|switch|case|break|continue|delete|instanceof|void|yield|static|extends|super|get|set)\b/g,
  python:     /\b(def|return|if|elif|else|for|while|class|import|from|as|in|not|and|or|True|False|None|try|except|with|lambda|pass|break|continue|raise|global|yield|assert|del|finally|is|nonlocal|print)\b/g,
  java:       /\b(public|private|protected|class|interface|extends|implements|return|if|else|for|while|new|this|null|true|false|void|int|long|String|boolean|static|final|import|package|try|catch|throw|throws|break|continue|switch|case|default|abstract|synchronized|volatile|transient|native|instanceof|super|enum)\b/g,
  cpp:        /\b(int|long|void|return|if|else|for|while|class|struct|new|delete|nullptr|true|false|bool|char|float|double|include|namespace|using|public|private|protected|try|catch|throw|break|continue|switch|case|default|const|static|auto|virtual|override|template|typename|unsigned|signed|short)\b/g,
};

const TYPES = {
  javascript: /\b(Array|Object|Promise|Map|Set|Error|Date|Math|JSON|console|window|document|Number|String|Boolean|Symbol|BigInt|RegExp|Function|Generator|Iterator|Proxy|Reflect|WeakMap|WeakSet|WeakRef)\b/g,
  python:     /\b(list|dict|tuple|set|int|str|float|bool|bytes|type|object|range|enumerate|zip|map|filter|sorted|len|print|input|open|hasattr|getattr|setattr|isinstance|issubclass)\b/g,
  java:       /\b(List|Map|Set|ArrayList|HashMap|HashSet|Iterator|Optional|Stream|StringBuilder|Integer|Double|Float|Long|Short|Byte|Character|Object|System|Math|Collections|Arrays|Scanner)\b/g,
  cpp:        /\b(vector|string|map|set|unordered_map|unordered_set|pair|tuple|array|list|deque|stack|queue|priority_queue|cout|cin|endl|size_t|std)\b/g,
};

export function highlight(code, lang = "javascript") {
  if (!code) return "";
  let c = esc(code);

  // Comments first (protect from further processing)
  const comments = [];
  c = c.replace(/(\/\/[^\n]*)|(\/\*[\s\S]*?\*\/)/g, (m) => {
    comments.push(m);
    return `\x00C${comments.length - 1}\x00`;
  });
  c = c.replace(/(#[^\n]*)/g, (m) => {
    comments.push(m);
    return `\x00C${comments.length - 1}\x00`;
  });

  // Strings
  c = c.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)/g,
    '<span class="hl-str">$1</span>');

  // Types/builtins
  if (TYPES[lang]) {
    c = c.replace(TYPES[lang], '<span class="hl-type">$1</span>');
  }

  // Keywords
  const kw = KW[lang] || KW.javascript;
  c = c.replace(kw, '<span class="hl-kw">$1</span>');

  // Numbers
  c = c.replace(/\b(\d+\.?\d*[fFlLuU]?)\b/g, '<span class="hl-num">$1</span>');

  // Functions
  c = c.replace(/\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?=\()/g, (m, fn) => {
    if (m.includes('class="')) return m;
    return `<span class="hl-fn">${fn}</span>(`;
  });

  // Restore comments
  c = c.replace(/\x00C(\d+)\x00/g, (_, i) =>
    `<span class="hl-cm">${comments[+i]}</span>`);

  return c;
}