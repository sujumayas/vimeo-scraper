import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './ui/theme';
import { MovieBrowser } from './components/MovieBrowser';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <MovieBrowser />
    </ThemeProvider>
  );
};

export default App;
