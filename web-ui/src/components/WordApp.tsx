import React, { useState, useRef, useEffect } from 'react';

interface WordAppProps {
  className?: string;
}

const WordApp: React.FC<WordAppProps> = ({ className = '' }) => {
  const [documentContent, setDocumentContent] = useState('');
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const [isUnderline, setIsUnderline] = useState(false);
  const [fontSize, setFontSize] = useState(12);
  const [saveStatus, setSaveStatus] = useState('');
  const documentRef = useRef<HTMLTextAreaElement>(null);

  // Auto-save functionality
  useEffect(() => {
    const autoSave = setTimeout(() => {
      if (documentContent.trim()) {
        setSaveStatus('Saving...');
        // Simulate save
        setTimeout(() => setSaveStatus('Saved'), 1000);
      }
    }, 2000);

    return () => clearTimeout(autoSave);
  }, [documentContent]);

  const handleFormatting = (type: 'bold' | 'italic' | 'underline') => {
    switch (type) {
      case 'bold':
        setIsBold(!isBold);
        break;
      case 'italic':
        setIsItalic(!isItalic);
        break;
      case 'underline':
        setIsUnderline(!isUnderline);
        break;
    }
  };

  const handleFontSizeChange = (size: number) => {
    setFontSize(size);
  };

  return (
    <div className={`word-app ${className}`} data-testid="word-app">
      {/* Toolbar */}
      <div className="toolbar" style={{ 
        padding: '10px', 
        borderBottom: '1px solid #ccc', 
        backgroundColor: '#f5f5f5',
        display: 'flex',
        gap: '10px',
        alignItems: 'center'
      }}>
        {/* Font Size Selector */}
        <select 
          value={fontSize} 
          onChange={(e) => handleFontSizeChange(Number(e.target.value))}
          style={{ padding: '4px' }}
        >
          <option value={10}>10pt</option>
          <option value={12}>12pt</option>
          <option value={14}>14pt</option>
          <option value={16}>16pt</option>
          <option value={18}>18pt</option>
        </select>

        {/* Formatting Buttons - These have accessibility issues that need fixing */}
        <button
          onClick={() => handleFormatting('bold')}
          style={{
            fontWeight: isBold ? 'bold' : 'normal',
            padding: '6px 12px',
            backgroundColor: isBold ? '#0078d4' : '#fff',
            color: isBold ? '#fff' : '#000',
            border: '1px solid #ccc'
          }}
          data-testid="word-toolbar-bold"
        >
          B
        </button>

        <button
          onClick={() => handleFormatting('italic')}
          style={{
            fontStyle: isItalic ? 'italic' : 'normal',
            padding: '6px 12px',
            backgroundColor: isItalic ? '#0078d4' : '#fff',
            color: isItalic ? '#fff' : '#000',
            border: '1px solid #ccc'
          }}
        >
          I
        </button>

        <button
          onClick={() => handleFormatting('underline')}
          style={{
            textDecoration: isUnderline ? 'underline' : 'none',
            padding: '6px 12px',
            backgroundColor: isUnderline ? '#0078d4' : '#fff',
            color: isUnderline ? '#fff' : '#000',
            border: '1px solid #ccc'
          }}
        >
          U
        </button>

        {/* Save Status - Poor visibility */}
        <div style={{ 
          marginLeft: 'auto', 
          fontSize: '11px', 
          color: '#999'  /* Poor contrast */
        }}>
          {saveStatus}
        </div>
      </div>

      {/* Document Content Area */}
      <div style={{ 
        padding: '20px', 
        minHeight: '500px', 
        backgroundColor: '#fff' 
      }}>
        <textarea
          ref={documentRef}
          value={documentContent}
          onChange={(e) => setDocumentContent(e.target.value)}
          placeholder="Start typing your document..."
          data-testid="word-document-content"
          style={{
            width: '100%',
            height: '400px',
            border: 'none',
            outline: 'none',
            fontSize: `${fontSize}pt`,
            fontWeight: isBold ? 'bold' : 'normal',
            fontStyle: isItalic ? 'italic' : 'normal',
            textDecoration: isUnderline ? 'underline' : 'none',
            fontFamily: 'Arial, sans-serif',
            lineHeight: 1.5,
            resize: 'none'
          }}
        />
      </div>

      {/* Status Bar */}
      <div style={{ 
        padding: '8px 20px', 
        borderTop: '1px solid #ccc', 
        backgroundColor: '#f9f9f9',
        fontSize: '12px',
        color: '#666'
      }}>
        Words: {documentContent.split(/\s+/).filter(word => word.length > 0).length} | 
        Characters: {documentContent.length}
      </div>
    </div>
  );
};

export default WordApp;
