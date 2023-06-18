import React from 'react';
import axios from 'axios';

class LetterForm extends React.Component {
  state = {
    letter: '',
    prediction: '',
    issues: [],
  };

  handleInputChange = (event) => {
    this.setState({
      letter: event.target.value,
    });
  };

  handleSubmit = (event) => {
    event.preventDefault();
    fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        userLetter: this.state.letter,
      }),
    })
      .then((response) => {
        console.log(response);
        return response.json();
      })

      .then((data) => {
        console.log('Data object:', data);
        this.setState({
          prediction: data.prediction,
          issues: data.issues,
        });
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  render() {
    return (
      <div>
        <form onSubmit={this.handleSubmit}>
          <label>
            Enter your letter:
            <input
              type='text'
              value={this.state.letter}
              onChange={this.handleInputChange}
            />
          </label>
          <button type='submit'>Submit</button>
        </form>
        <p>Prediction: {this.state.prediction}</p>
        <p>Issues: {this.state.issues.join(', ')}</p>
      </div>
    );
  }
}

export default LetterForm;
