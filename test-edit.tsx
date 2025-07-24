import React, { useState } from 'react';

const TestComponent: React.FC = () => {
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState('Hello, World!');

  const increment = () => {
    setCount(count + 1);
  };

  const decrement = () => {
    setCount(count - 1);
  };

  const updateMessage = () => {
    setMessage(`카운트: ${count}`);
  };

  return (
    <div style={{ 
      padding: '20px', 
      textAlign: 'center', 
      fontFamily: 'Arial, sans-serif' 
    }}>
      <h1>테스트 컴포넌트</h1>
      <p>{message}</p>
      <div style={{ margin: '20px 0' }}>
        <h2>카운터: {count}</h2>
        <button onClick={decrement} style={{ margin: '0 10px' }}>
          -
        </button>
        <button onClick={increment} style={{ margin: '0 10px' }}>
          +
        </button>
      </div>
      <button onClick={updateMessage} style={{ 
        padding: '10px 20px', 
        backgroundColor: '#007bff', 
        color: 'white', 
        border: 'none', 
        borderRadius: '4px',
        cursor: 'pointer'
      }}>
        메시지 업데이트
      </button>
    </div>
  );
};

export default TestComponent;
