import React from 'react';
import './App.css';
import LetterForm from './LetterForm';
import Header from './Header';

function App() {
  return (
    <div className='App'>
      {/* <div className='App-header'>
        <h1>Letter Quality Predictor</h1>
      </div> */}
      <Header />
      <LetterForm />
    </div>
  );
}

export default App;
