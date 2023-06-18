import React from 'react';
import './Header.css'; // Import the CSS file
import student from './images/student3.png';

class Header extends React.Component {
  render() {
    return (
      <header className='header'>
        <h1 className='header__title'>Letter Quality Predictor</h1>
        <p className='header__subtitle'>
          The most effective, cutting-edge techniques that you can apply to your
          motivational letters.
          {/* <a className='header__link' href='#'>
            Learn more →
          </a> */}
        </p>
        <img
          className='header__main-illustration'
          src={student}
          alt='man standing on a rock'
        ></img>
        <div className='header__square-pic rotation'></div>
      </header>
    );
  }
}
export default Header;
