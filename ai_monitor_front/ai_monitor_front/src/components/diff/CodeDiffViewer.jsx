import { DiffEditor } from "@monaco-editor/react";

export default function CodeDiffViewer({ original, optimized }) {
  return (
    <DiffEditor
      height="400px"
      original={original}
      modified={optimized}
      theme="vs-dark"
      options={{
        readOnly: true,
        renderSideBySide: true
      }}
    />
  );
}