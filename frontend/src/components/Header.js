import React from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';

const Header = (props) => {
  return (
    <Navbar bg="dark" variant="dark">
      <Nav className="me-auto">
        <Nav.Link href="input">Input</Nav.Link>
        {/* <Nav.Link href="output">Output</Nav.Link> */}
      </Nav>
    </Navbar>
  );
}

export default Header;