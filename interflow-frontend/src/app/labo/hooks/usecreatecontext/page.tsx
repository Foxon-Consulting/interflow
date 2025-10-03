'use client';

import React, { createContext, useContext, useState } from 'react';

// 1. Créer un contexte avec un type
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// 2. Créer un Provider component
function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. Hook personnalisé pour utiliser le contexte
function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme doit être utilisé à l\'intérieur d\'un ThemeProvider');
  }
  return context;
}

// 4. Composants enfants qui consomment le contexte
function Header() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <header className={`p-4 ${theme === 'light' ? 'bg-blue-100' : 'bg-gray-800'}`}>
      <h1 className={`text-2xl font-bold ${theme === 'light' ? 'text-gray-900' : 'text-white'}`}>
        Thème actuel: {theme}
      </h1>
      <button
        onClick={toggleTheme}
        className={`mt-2 px-4 py-2 rounded ${
          theme === 'light' 
            ? 'bg-gray-800 text-white hover:bg-gray-700' 
            : 'bg-blue-100 text-gray-900 hover:bg-blue-200'
        }`}
      >
        Changer le thème
      </button>
    </header>
  );
}

function Content() {
  const { theme } = useTheme();
  
  return (
    <div className={`p-8 ${theme === 'light' ? 'bg-white text-gray-900' : 'bg-gray-900 text-white'}`}>
      <h2 className="text-xl mb-4">Contenu de la page</h2>
      <p>
        Ce composant utilise également le contexte via useContext.
        Le thème est automatiquement appliqué à tous les composants enfants.
      </p>
    </div>
  );
}

// 5. Composant principal qui utilise le Provider
export default function UseContextExample() {
  return (
    <ThemeProvider>
      <div className="min-h-screen">
        <Header />
        <Content />
      </div>
    </ThemeProvider>
  );
}

