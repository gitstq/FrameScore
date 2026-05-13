import React, { useState, useEffect } from 'react';

function List({ items, onSort }) {
  const [filter, setFilter] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');

  // Direct state mutation pattern
  const updateItem = (index, value) => {
    setFilter(value);
  };

  // Inline function in JSX
  const renderItem = (item) => {
    return (
      <div className="list-item" onClick={() => console.log(item)}>
        <span>{item.name}</span>
        <span>{item.description}</span>
      </div>
    );
  };

  // Missing error handling
  async function loadData() {
    const response = await fetch('/api/items');
    const data = await response.json();
    return data;
  }

  useEffect(() => {
    loadData();
  }, []);

  // Deeply nested code
  function processItems(items) {
    if (items) {
      if (items.length > 0) {
        for (let i = 0; i < items.length; i++) {
          if (items[i].active) {
            if (items[i].visible) {
              if (items[i].approved) {
                console.log(items[i]);
              }
            }
          }
        }
      }
    }
  }

  // Magic numbers
  const threshold = 86400;
  const maxRetries = 3;
  const pageSize = 25;

  return (
    <div className="list-container">
      <input type="text" value={filter} onChange={(e) => setFilter(e.target.value)} />
      <button onClick={() => onSort(sortOrder)}>Sort</button>
      <ul>
        {items.map((item) => (
          <li>{renderItem(item)}</li>
        ))}
      </ul>
    </div>
  );
}

export default List;
