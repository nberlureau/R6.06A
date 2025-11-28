
function parseCodeFile(fileContent, language) {
  const result = {
    classes: [],
    functions: []

  };

  let cleanedContent = fileContent;
  
  switch (language.toLowerCase()) {
    case 'java':
    case 'javascript':
    case 'typescript':
    case 'kotlin':

    case 'csharp':
      cleanedContent = cleanedContent
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\/\/.*/g, '');
      break;
    case 'python':
      cleanedContent = cleanedContent
        .replace(/"""[\s\S]*?"""/g, '')
        .replace(/'''[\s\S]*?'''/g, '')
        .replace(/#.*/g, '');
      break;
    case 'php':
      cleanedContent = cleanedContent
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\/\/.*/g, '')
        .replace(/#.*/g, '');

      break;
  }

  const patterns = {
    java: {
      class: /(?:public|private|protected)?\s*(?:static|final|abstract)?\s*(?:class|interface|enum)\s+(\w+)/g,
      function: /(?:public|private|protected)?\s*(?:static|final|abstract|synchronized)?\s*(?:<[^>]+>\s*)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{/g
    },
    php: {
      class: /(?:abstract|final)?\s*class\s+(\w+)/g,
      
      function: /(?:public|private|protected)?\s*(?:static)?\s*function\s+(\w+)\s*\(/g
    },
    javascript: {
      class: /class\s+(\w+)/g,
      function: /(?:async\s+)?(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(?[^)]*\)?\s*=>|(\w+)\s*:\s*(?:async\s*)?function)/g
    },
    typescript: {
      class: /(?:export\s+)?(?:abstract\s+)?class\s+(\w+)/g,
      function: /(?:export\s+)?(?:async\s+)?(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(?[^)]*\)?\s*=>|(\w+)\s*:\s*(?:async\s*)?function|(?:public|private|protected)?\s*(?:static)?\s*(?:async)?\s*(\w+)\s*\([^)]*\)\s*:\s*[^{]+\{)/g
    },
    kotlin: {
      class: /(?:data\s+|sealed\s+|open\s+|abstract\s+)?class\s+(\w+)/g,
      function: /fun\s+(?:<[^>]+>\s*)?(\w+)\s*\(/g
    },
    python: {
      class: /class\s+(\w+)/g,
      function: /def\s+(\w+)\s*\(/g
    },
    csharp: {
      class: /(?:public|private|protected|internal)?\s*(?:static|sealed|abstract|partial)?\s*(?:class|interface|struct)\s+(\w+)/g,
      function: /(?:public|private|protected|internal)?\s*(?:static|virtual|override|abstract|async)?\s*(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)\s*\{/g
    }
  };

  const lang = language.toLowerCase();
  
  if (!patterns[lang]) {
    throw new Error(`mauvais langage`);

  }


  let match;
  while ((match = patterns[lang].class.exec(cleanedContent)) !== null) {
    const className = match[1];

    if (className && !result.classes.includes(className)) {
      result.classes.push(className);
    }
  }

 
  patterns[lang].function.lastIndex = 0;
  while ((match = patterns[lang].function.exec(cleanedContent)) !== null) {
   
    const functionName = match[1] || match[2] || match[3] || match[4];
    if (functionName && !result.functions.includes(functionName)) {

      result.functions.push(functionName);
    }
  }

  return result;
}


if (typeof module !== 'undefined' && module.exports) {
  module.exports = parseCodeFile;
}