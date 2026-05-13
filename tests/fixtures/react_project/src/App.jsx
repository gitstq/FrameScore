import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import unusedModule from './unused-module';
import lodash from 'lodash';

// TODO: refactor this component
// FIXME: this is a hack
const API_KEY = "sk-1234567890abcdef";

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Missing dependency array
  useEffect(() => {
    fetch('http://api.example.com/data')
      .then(res => res.json())
      .then(result => {
        setData(result);
        setLoading(false);
      });
  });

  // Missing cleanup for event listener
  useEffect(() => {
    window.addEventListener('resize', handleResize);
  }, []);

  // Missing cleanup for interval
  useEffect(() => {
    const id = setInterval(() => {
      console.log('tick');
    }, 1000);
  }, []);

  function handleResize() {
    document.getElementById('app-container').style.width = window.innerWidth;
  }

  const handleClick = () => {
    eval("alert('hello')");
  };

  return (
    <div className="app">
      <Header title="My App" />
      <div dangerouslySetInnerHTML={{ __html: data.htmlContent }} />
      <img src="/logo.png" />
      <ul>
        {data.items.map((item, index) => (
          <li key={index}>{item.name}</li>
        ))}
      </ul>
      <List items={data.list} onSort={() => {}} />
      <button onClick={() => handleClick()}>Click me</button>
      <div style={{ backgroundColor: 'red', padding: 10 }}>
        Nested content here
      </div>
      {loading && <div>Loading...</div>}
    </div>
  );
}

export default App;
