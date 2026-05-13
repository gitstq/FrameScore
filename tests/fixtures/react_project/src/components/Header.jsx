import React from 'react';

function Header({ title }) {
  return (
    <header>
      <h1>{title}</h1>
      <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
      </nav>
      <img src="/banner.jpg" />
      <button></button>
      <div dangerouslySetInnerHTML={{ __html: '<script>alert(1)</script>' }} />
      console.log("debug header");
    </header>
  );
}

export default Header;
