import './App.css';
import React from 'react';
import {BrowserRouter as Router,
  Routes, Route, Link, Redirect, } from "react-router-dom";
import Input from './components/Input';
import Output from './components/Output';

export default class App extends React.Component{

  constructor(props){
    super(props);
    this.state = { mode: "normal", configs: [], showError:false };
  }
  
  

  render() {
    return(
      <>
        <div>
          <Router>
            <Routes>
              <Route exact path="/" element={<Input />} />
              <Route path="/input" element={<Input />} />
              {/* <Route path="/output" element={<Output />} /> */}
            </Routes>
          </Router>
        </div>
      </>
    );
  }
}
